from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.roles import crear_roles
from apps.usuarios.politica import ADMIN_USERNAME


class Command(BaseCommand):
    help = 'Configura ADMIN_MPD como único administrador y retira privilegios administrativos a las demás cuentas.'

    def handle(self, *args, **options):
        clave = getpass('Contraseña para ADMIN_MPD: ')
        confirmacion = getpass('Repite la contraseña: ')
        if not clave or clave != confirmacion:
            raise CommandError('Las contraseñas deben coincidir y no estar vacías.')
        # La clave elegida por el propietario se introduce solo en la terminal.
        # No se escribe en el código, los argumentos ni la salida del comando.
        with transaction.atomic():
            grupos = {grupo.name: grupo for grupo in crear_roles()}
            Usuario = get_user_model()
            administrador, _ = Usuario.objects.get_or_create(username=ADMIN_USERNAME)
            administrador.is_active = True
            administrador.is_staff = True
            administrador.is_superuser = True
            administrador.first_name = 'Administrador'
            administrador.last_name = ''
            administrador.set_password(clave)
            administrador.save()
            administrador.groups.set([grupos['Administrador']])
            otros = Usuario.objects.exclude(pk=administrador.pk)
            permisos_usuarios = Permission.objects.filter(content_type__app_label='usuarios')
            for usuario in otros.select_for_update():
                era_admin = usuario.is_superuser or usuario.groups.filter(name='Administrador').exists()
                usuario.is_superuser = False
                usuario.is_staff = False
                if usuario.username == 'admin.demo':
                    usuario.is_active = False
                usuario.save(update_fields=['is_superuser', 'is_staff', 'is_active'])
                usuario.groups.remove(grupos['Administrador'])
                usuario.user_permissions.remove(*permisos_usuarios)
                if era_admin and not usuario.groups.exists():
                    usuario.groups.add(grupos['Mesa de partes'])
        self.stdout.write(self.style.SUCCESS('ADMIN_MPD configurado como único administrador. No se eliminaron usuarios ni documentos.'))
