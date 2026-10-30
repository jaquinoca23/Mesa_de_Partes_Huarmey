from django.db import migrations


def habilitar_registro(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    permiso = Permission.objects.filter(content_type__app_label='expedientes', codename='add_expediente').first()
    grupo = Group.objects.filter(name='Mesa de partes').first()
    if permiso and grupo:
        grupo.permissions.add(permiso)


class Migration(migrations.Migration):
    dependencies = [('expedientes', '0002_initial'), ('auth', '0012_alter_user_first_name_max_length')]
    operations = [migrations.RunPython(habilitar_registro, migrations.RunPython.noop)]
