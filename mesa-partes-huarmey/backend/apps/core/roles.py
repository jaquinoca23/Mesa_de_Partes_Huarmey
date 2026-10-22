"""
Roles de ejemplo (PROVISIONALES). Un rol es un "grupo" de Django con un conjunto de permisos.
Los roles y permisos definitivos dependen de la estructura y los procedimientos de la
Municipalidad Provincial de Huarmey (ver docs/institucional/pendientes.md).
"""
from django.contrib.auth.models import Group, Permission

# El Administrador recibe todos los permisos de estas aplicaciones.
APPS_ADMINISTRADOR = ('expedientes', 'organizacion', 'usuarios', 'catalogos', 'auditoria')

ROLES = {
    'Administrador': None,  # None = todos los permisos de APPS_ADMINISTRADOR
    'Mesa de partes': [
        'expedientes.view_expediente',
        'expedientes.ver_todos_expedientes',
        'expedientes.cambiar_estado_expediente',
        'expedientes.derivar_expediente',
        'expedientes.registrar_actuacion',
    ],
    'Funcionario de área': [
        'expedientes.view_expediente',
        'expedientes.cambiar_estado_expediente',
        'expedientes.derivar_expediente',
        'expedientes.registrar_actuacion',
    ],
    'Consulta y reportes': [
        'expedientes.view_expediente',
        'expedientes.ver_todos_expedientes',
        'expedientes.ver_reportes',
        'auditoria.view_registroauditoria',
    ],
}


def _permiso(codigo):
    aplicacion, nombre = codigo.split('.')
    return Permission.objects.get(content_type__app_label=aplicacion, codename=nombre)


def crear_roles():
    """Crea (o actualiza) los roles de ejemplo. Se puede repetir sin duplicar. Devuelve los grupos."""
    grupos = []
    for nombre, codigos in ROLES.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        if codigos is None:
            permisos = list(Permission.objects.filter(content_type__app_label__in=APPS_ADMINISTRADOR))
        else:
            permisos = [_permiso(codigo) for codigo in codigos]
        grupo.permissions.set(permisos)
        grupos.append(grupo)
    return grupos
