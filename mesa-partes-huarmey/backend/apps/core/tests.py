from django.core.management import call_command
from django.test import TestCase

from apps.catalogos.models import EstadoExpediente, TipoDocumental
from apps.expedientes.models import Expediente
from apps.organizacion.models import Area


class HealthEndpointTests(TestCase):
    """Pruebas automáticas del endpoint GET /api/health/."""

    def test_health_responde_ok_en_json(self):
        respuesta = self.client.get('/api/health/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/json')
        datos = respuesta.json()
        self.assertEqual(datos['status'], 'ok')
        self.assertEqual(datos['service'], 'mesa-partes-huarmey-api')
        self.assertIn('server_time', datos)

    def test_health_no_acepta_post(self):
        respuesta = self.client.post('/api/health/')
        self.assertEqual(respuesta.status_code, 405)


class CargarDatosFicticiosTests(TestCase):
    """El comando de datos ficticios debe poder repetirse sin duplicar registros."""

    def test_se_puede_ejecutar_dos_veces_sin_duplicar(self):
        call_command('cargar_datos_ficticios', verbosity=0)
        totales = (
            TipoDocumental.objects.count(),
            EstadoExpediente.objects.count(),
            Area.objects.count(),
            Expediente.objects.count(),
        )
        call_command('cargar_datos_ficticios', verbosity=0)
        self.assertEqual(
            totales,
            (
                TipoDocumental.objects.count(),
                EstadoExpediente.objects.count(),
                Area.objects.count(),
                Expediente.objects.count(),
            ),
        )
        self.assertEqual(TipoDocumental.objects.count(), 10)
        self.assertEqual(EstadoExpediente.objects.count(), 7)
        self.assertEqual(Expediente.objects.count(), 3)

    def test_las_areas_de_prueba_quedan_marcadas_como_ficticias(self):
        call_command('cargar_datos_ficticios', verbosity=0)
        self.assertFalse(Area.objects.filter(es_ficticia=False).exists())
