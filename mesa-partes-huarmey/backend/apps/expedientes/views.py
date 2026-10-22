from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

import logging

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar
from apps.documentos.servicios import validar_archivos_subidos
from apps.documentos.validadores import normalizar_extensiones
from apps.notificaciones.servicios import notificar_registro

from apps.identidad.servicios import esta_configurado as dni_configurado

from .models import Solicitante
from .serializers import SolicitudSerializer
from .servicios import ErrorDeConfiguracion, construir_cargo, registrar_solicitud

logger = logging.getLogger(__name__)

# NOTA SOBRE LOS ENDPOINTS PÚBLICOS DE ESTE ARCHIVO
# Son para ciudadanos sin cuenta, por eso usan authentication_classes = [] (sin sesión):
#  - No dependen de cookies, así que no hay riesgo de CSRF.
#  - Si el navegador tuviera abierta una sesión del administrador, no interfiere.


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def configuracion(request):
    """
    Datos que React necesita para armar el formulario: límites de archivos y opciones.
    Así los límites se definen en UN solo lugar (settings/.env) y el frontend los lee.
    """
    return Response(
        {
            # True solo si hay un token configurado en el servidor (el token nunca se envía al navegador).
            'verificacion_dni': dni_configurado(),
            'archivos': {
                'max_archivos': settings.UPLOAD_MAX_FILES,
                'max_tamano_mb': settings.UPLOAD_MAX_FILE_SIZE_MB,
                'extensiones_permitidas': sorted(normalizar_extensiones(settings.UPLOAD_ALLOWED_EXTENSIONS)),
            },
            'tipos_persona': [
                {'valor': valor, 'etiqueta': etiqueta} for valor, etiqueta in Solicitante.TipoPersona.choices
            ],
            'tipos_documento_identidad': [
                {'valor': valor, 'etiqueta': etiqueta}
                for valor, etiqueta in Solicitante.TipoDocumentoIdentidad.choices
            ],
        }
    )


class ValidarSolicitudView(APIView):
    """
    POST /api/solicitudes/validar/

    ETAPA 4: comprueba en el servidor que los datos y los archivos sean válidos.
    NO guarda nada: el registro real del expediente y el cargo de recepción llegan en la ETAPA 5.
    Por eso la respuesta siempre incluye "registrado": false.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'solicitudes'  # límite de intentos definido en settings (REST_FRAMEWORK)

    def post(self, request):
        errores = {}

        serializador = SolicitudSerializer(data=request.data)
        if not serializador.is_valid():
            errores.update(serializador.errors)

        archivos = request.FILES.getlist('archivos')
        errores_archivos = validar_archivos_subidos(archivos)
        if errores_archivos:
            errores['archivos'] = errores_archivos

        if errores:
            return Response(
                {
                    'ok': False,
                    'registrado': False,
                    'mensaje': 'Revisa los datos marcados e inténtalo de nuevo.',
                    'errores': errores,
                },
                status=400,
            )

        return Response(
            {
                'ok': True,
                'registrado': False,
                'mensaje': 'Los datos son válidos. La solicitud todavía no ha sido registrada.',
                'archivos_validados': len(archivos),
            }
        )


class RegistrarSolicitudView(APIView):
    """
    POST /api/solicitudes/

    ETAPA 5: valida y REGISTRA la solicitud. Responde 201 con el cargo solo cuando la base de
    datos confirmó el guardado. Si el mismo envío llega repetido, responde 200 con
    "duplicado": true y el mismo cargo (no se crea otro expediente).
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'solicitudes'

    def post(self, request):
        errores = {}
        serializador = SolicitudSerializer(data=request.data)
        if not serializador.is_valid():
            errores.update(serializador.errors)

        archivos = request.FILES.getlist('archivos')
        errores_archivos = validar_archivos_subidos(archivos)
        if errores_archivos:
            errores['archivos'] = errores_archivos

        if errores:
            return Response(
                {
                    'ok': False,
                    'registrado': False,
                    'mensaje': 'Revisa los datos marcados e inténtalo de nuevo.',
                    'errores': errores,
                },
                status=400,
            )

        try:
            expediente, creado = registrar_solicitud(serializador.validated_data, archivos)
        except ErrorDeConfiguracion:
            logger.error('Registro imposible: falta el estado inicial.')
            return Response(
                {'ok': False, 'registrado': False, 'mensaje': 'El sistema no está disponible en este momento. Inténtalo más tarde.'},
                status=503,
            )
        except Exception:  # noqa: BLE001 - nunca se afirma un registro que no ocurrió
            logger.exception('Error inesperado al registrar una solicitud.')
            return Response(
                {'ok': False, 'registrado': False, 'mensaje': 'No se pudo registrar tu solicitud. No se guardó nada; inténtalo de nuevo.'},
                status=500,
            )

        if creado:
            registrar(request, RegistroAuditoria.Accion.EXPEDIENTE_REGISTRADO, expediente, 'Registro desde el portal ciudadano.')
            notificar_registro(expediente)  # un fallo de correo no impide el registro

        return Response(
            {
                'ok': True,
                'registrado': True,
                'duplicado': not creado,
                'mensaje': 'Tu solicitud fue registrada.' if creado else 'Esta solicitud ya había sido registrada.',
                'cargo': construir_cargo(expediente),
            },
            status=201 if creado else 200,
        )
