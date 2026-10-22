"""
Crea los roles de ejemplo y usuarios de DEMOSTRACIÓN:  python manage.py crear_roles_demo

- Los roles y permisos son PROVISIONALES (ver apps/core/roles.py).
- Los usuarios son ficticios (*.demo). Cada uno recibe una contraseña ALEATORIA que se muestra
  una sola vez en pantalla; nunca hay contraseñas escritas en el código.
- Opciones:  --password "ClaveLarga123!"  usa esa contraseña para los usuarios nuevos.
- Si un usuario demo ya existe, no se le cambia la contraseña.
"""
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.roles import crear_roles
from apps.organizacion.models import Area

# (usuario, rol, nombre de área ficticia o None, nombres, apellidos, cargo)
USUARIOS_DEMO = [
    ('admin.demo', 'Administrador', None, 'Admin', 'Demo', 'Administrador del sistema (FICTICIO)'),
    ('mesa.demo', 'Mesa de partes', 'Oficina de Ejemplo A (FICTICIO)', 'Mesa', 'Demo', 'Personal de mesa de partes (FICTICIO)'),
    ('area1.demo', 'Funcionario de área', 'Gerencia de Ejemplo 1 (FICTICIO)', 'Área Uno', 'Demo', 'Funcionario (FICTICIO)'),
    ('area2.demo', 'Funcionario de área', 'Gerencia de Ejemplo 2 (FICTICIO)', 'Área Dos', 'Demo', 'Funcionario (FICTICIO)'),
    ('auditor.demo', 'Consulta y reportes', None, 'Consulta', 'Demo', 'Consulta y reportes (FICTICIO)'),
]


class Command(BaseCommand):
    help = 'Crea roles de ejemplo y usuarios de demostración con contraseñas aleatorias.'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='', help='Contraseña para los usuarios NUEVOS (por defecto, aleatoria).')

    @transaction.atomic
    def handle(self, *args, **opciones):
        grupos = {g.name: g for g in crear_roles()}
        self.stdout.write(self.style.SUCCESS(f'Roles listos: {", ".join(grupos)}'))

        Usuario = get_user_model()
        nuevos = []
        for username, rol, nombre_area, nombres, apellidos, cargo in USUARIOS_DEMO:
            area = Area.objects.filter(nombre=nombre_area).first() if nombre_area else None
            if nombre_area and area is None:
                self.stdout.write(self.style.WARNING(f'  Aviso: no existe el área "{nombre_area}". Ejecuta antes cargar_datos_ficticios.'))
            usuario = Usuario.objects.filter(username=username).first()
            if usuario is None:
                clave = opciones['password'] or secrets.token_urlsafe(12)
                usuario = Usuario(username=username)
                usuario.set_password(clave)
                nuevos.append((username, clave))
            usuario.first_name, usuario.last_name = nombres, apellidos
            usuario.email = f'{username}@example.com'
            usuario.cargo, usuario.area, usuario.is_active = cargo, area, True
            usuario.save()
            usuario.groups.set([grupos[rol]])

        if nuevos:
            self.stdout.write('\nUsuarios NUEVOS (anota las contraseñas: no se vuelven a mostrar):')
            for username, clave in nuevos:
                self.stdout.write(f'  {username:14} {clave}')
        else:
            self.stdout.write('Los usuarios demo ya existían: no se cambiaron sus contraseñas.')
