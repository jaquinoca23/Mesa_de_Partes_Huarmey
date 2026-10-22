from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import RegistroAuditoria
from apps.core.mixins import AuditaCambiosMixin
from apps.core.permisos import PermisosModelo, requiere
from apps.core.roles import ROLES

from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioViewSet(AuditaCambiosMixin, viewsets.ModelViewSet):
    """
    /api/panel/usuarios/ — gestión del personal. Exige los permisos de Django sobre "usuario".
    Los usuarios no se eliminan (se desactivan) para conservar la trazabilidad.
    """

    serializer_class = UsuarioSerializer
    permission_classes = [PermisosModelo]
    queryset = Usuario.objects.select_related('area').prefetch_related('groups').order_by('username')
    pagination_class = None
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    accion_creacion = RegistroAuditoria.Accion.USUARIO_CREADO
    accion_modificacion = RegistroAuditoria.Accion.USUARIO_MODIFICADO

    def get_queryset(self):
        consulta = super().get_queryset()
        usuario = self.request.user
        # Los superusuarios solo los ve (y modifica) otro superusuario.
        if not usuario.is_superuser:
            consulta = consulta.filter(is_superuser=False)
            # Y los Administradores, solo otro Administrador: así nadie "toma" una cuenta con más poder.
            if not usuario.groups.filter(name='Administrador').exists():
                consulta = consulta.exclude(groups__name='Administrador')
        return consulta


class RolesView(APIView):
    """GET /api/panel/roles/ — lista de roles disponibles para asignar."""

    permission_classes = [requiere('usuarios.view_usuario')]

    def get(self, request):
        return Response([{'valor': nombre, 'etiqueta': nombre} for nombre in ROLES])
