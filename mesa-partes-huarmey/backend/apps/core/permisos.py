from rest_framework.permissions import BasePermission, DjangoModelPermissions


def requiere(*permisos):
    """
    Crea una regla de acceso que exige TODOS los permisos indicados.

    Uso:  permission_classes = [requiere('expedientes.view_expediente')]

    Esto se comprueba en el SERVIDOR en cada petición: ocultar un botón en React no basta.
    Los superusuarios de Django tienen todos los permisos.
    """

    class PermisoRequerido(BasePermission):
        message = 'No tienes permiso para realizar esta acción.'

        def has_permission(self, request, view):
            usuario = request.user
            return bool(
                usuario
                and usuario.is_authenticated
                and usuario.is_active
                and all(usuario.has_perm(permiso) for permiso in permisos)
            )

    return PermisoRequerido


class PermisosModelo(DjangoModelPermissions):
    """
    Permisos de Django por modelo (ver, agregar, cambiar, eliminar).
    A diferencia de la clase original, aquí TAMBIÉN se exige el permiso "ver" para consultar.
    """

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
