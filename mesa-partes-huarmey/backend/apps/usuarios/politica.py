from rest_framework.permissions import BasePermission


ADMIN_USERNAME = 'ADMIN_MPD'


def es_administrador_unico(usuario):
    return bool(
        usuario and usuario.is_authenticated and usuario.is_active
        and usuario.username == ADMIN_USERNAME and usuario.is_superuser
    )


class SoloAdministradorUnico(BasePermission):
    message = 'Solo ADMIN_MPD puede administrar las cuentas del personal.'

    def has_permission(self, request, view):
        return es_administrador_unico(request.user)
