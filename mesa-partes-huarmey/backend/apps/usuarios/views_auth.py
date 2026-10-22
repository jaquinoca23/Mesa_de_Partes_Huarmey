"""Inicio y cierre de sesión del personal municipal (sesión por cookie + CSRF)."""
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar

MENSAJE_LOGIN_INCORRECTO = 'Usuario o contraseña incorrectos.'


def datos_de_sesion(usuario):
    """Qué sabe React del usuario: lo justo para armar el menú. La seguridad real se aplica en el servidor."""
    return {
        'id': usuario.pk,
        'username': usuario.username,
        'nombre': usuario.get_full_name() or usuario.username,
        'email': usuario.email,
        'cargo': usuario.cargo,
        'area': {'id': usuario.area_id, 'nombre': usuario.area.nombre} if usuario.area_id else None,
        'roles': sorted(usuario.groups.values_list('name', flat=True)),
        'permisos': sorted(usuario.get_all_permissions()),
        'es_superusuario': usuario.is_superuser,
    }


class CsrfView(APIView):
    """GET /api/auth/csrf/ — entrega la cookie CSRF que React reenvía en cada petición que modifica datos."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)  # al pedir el token, Django coloca la cookie CSRF en la respuesta
        return Response({'ok': True})


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, trim_whitespace=False)


class LoginView(APIView):
    """POST /api/auth/login/ {username, password}. Mensaje genérico si falla; límite de intentos por IP."""

    authentication_classes = []  # sin sesión previa; el CSRF se comprueba a mano abajo
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        # Evita que otro sitio web inicie sesión "en nombre" del navegador (login CSRF).
        SessionAuthentication().enforce_csrf(request)

        serializador = LoginSerializer(data=request.data)
        if not serializador.is_valid():
            return Response({'ok': False, 'mensaje': MENSAJE_LOGIN_INCORRECTO}, status=400)

        usuario = authenticate(
            request,
            username=serializador.validated_data['username'],
            password=serializador.validated_data['password'],
        )
        if usuario is None or not usuario.is_active:
            # No se guarda el nombre escrito (podría ser un dato personal o una contraseña mal puesta).
            registrar(request, RegistroAuditoria.Accion.LOGIN_FALLIDO, detalle='Credenciales incorrectas.')
            return Response({'ok': False, 'mensaje': MENSAJE_LOGIN_INCORRECTO}, status=400)

        login(request, usuario)  # crea una sesión nueva y rota el token CSRF
        registrar(request, RegistroAuditoria.Accion.LOGIN, usuario=usuario)
        return Response({'ok': True, 'usuario': datos_de_sesion(usuario)})


class LogoutView(APIView):
    """POST /api/auth/logout/"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        registrar(request, RegistroAuditoria.Accion.LOGOUT)
        logout(request)
        return Response({'ok': True})


class SesionView(APIView):
    """GET /api/auth/me/ — datos del usuario con sesión iniciada (403 si no la hay)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'ok': True, 'usuario': datos_de_sesion(request.user)})
