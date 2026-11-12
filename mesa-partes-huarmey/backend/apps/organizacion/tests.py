from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.organizacion.models import Area
from apps.usuarios.models import Usuario


class AreasHuarmeyTests(TestCase):
    def test_carga_jerarquia_y_se_puede_repetir(self):
        call_command('cargar_areas_huarmey', verbosity=0)
        call_command('cargar_areas_huarmey', verbosity=0)
        self.assertEqual(Area.objects.filter(activo=True).count(), 42)
        gerencia = Area.objects.get(nombre='Gerencia de Servicios a la Ciudad y Gestión Ambiental')
        self.assertEqual(gerencia.padre.nombre, 'Gerencia Municipal')
        subgerencia = Area.objects.get(nombre='Subgerencia de Seguridad Ciudadana')
        self.assertEqual(subgerencia.padre, gerencia)
        oficina = Area.objects.get(nombre='Oficina de Tecnologías de la Información')
        self.assertEqual(oficina.padre.nombre, 'Oficina General de Planeamiento y Presupuesto')
        self.assertFalse(Area.objects.filter(es_ficticia=True).exists())

    def test_desactiva_ejemplos_sin_perder_asignaciones(self):
        ejemplo = Area.objects.create(nombre='Gerencia de Ejemplo 1 (FICTICIO)', tipo='GERENCIA')
        usuario = Usuario.objects.create_user(username='personal', area=ejemplo)
        call_command('cargar_areas_huarmey', verbosity=0)
        ejemplo.refresh_from_db()
        usuario.refresh_from_db()
        self.assertFalse(ejemplo.activo)
        self.assertEqual(usuario.area_id, ejemplo.pk)
        self.assertEqual(Area.objects.count(), 43)
        cliente = APIClient()
        admin = Usuario.objects.create_superuser('ADMIN_MPD', password='Clave-Prueba-8194!')
        cliente.force_authenticate(admin)
        respuesta = cliente.get('/api/panel/expedientes/opciones/')
        self.assertEqual(respuesta.status_code, 200)
        opciones = respuesta.json()['areas']
        self.assertEqual(len(opciones), 42)
        self.assertNotIn(ejemplo.pk, [a['valor'] for a in opciones])
