"""Pruebas de la ETAPA 7: bandejas por área, derivación, recepción, actuaciones y descarga de adjuntos."""
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.auditoria.models import RegistroAuditoria
from apps.catalogos.models import EstadoExpediente
from apps.derivaciones.models import Derivacion
from apps.documentos.models import Adjunto
from apps.organizacion.models import Area

from .models import Expediente

CLAVE = 'Clave-Segura-9182!'
PDF = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n'


def sesion(username):
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.get('/api/auth/csrf/')
    cabecera = {'HTTP_X_CSRFTOKEN': cliente.cookies['csrftoken'].value}
    r = cliente.post('/api/auth/login/', {'username': username, 'password': CLAVE}, format='json', **cabecera)
    assert r.status_code == 200, r.content
    return cliente


def post(cliente, url, datos=None):
    return cliente.post(url, datos or {}, format='json', HTTP_X_CSRFTOKEN=cliente.cookies['csrftoken'].value)


class BasePanel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._carpeta = tempfile.mkdtemp()
        cls._override = override_settings(PRIVATE_MEDIA_ROOT=cls._carpeta)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._carpeta, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos_ficticios', verbosity=0)
        call_command('crear_roles_demo', '--password', CLAVE, verbosity=0)
        cls.area1 = Area.objects.get(nombre='Gerencia de Ejemplo 1 (FICTICIO)')
        cls.area2 = Area.objects.get(nombre='Gerencia de Ejemplo 2 (FICTICIO)')
        cls.exp = Expediente.objects.order_by('id').first()
        cls.exp2 = Expediente.objects.order_by('id').last()
        for codigo in ('en-derivacion', 'en-atencion'):
            assert EstadoExpediente.objects.filter(codigo=codigo).exists()
        Expediente.objects.filter(pk=cls.exp.pk).update(email_contacto='ana.ejemplo@example.com')

    def setUp(self):
        cache.clear()

    def url(self, exp, accion=''):
        return f'/api/panel/expedientes/{exp.uuid}/{accion}'

    def derivar(self, cliente, exp, area, **extra):
        return post(cliente, self.url(exp, 'derivar/'), {'area': area.pk, 'motivo': 'Para atención', **extra})


class VisibilidadTests(BasePanel):
    def test_anonimo_no_accede(self):
        for url in ['/api/panel/expedientes/', '/api/panel/expedientes/opciones/', self.url(self.exp)]:
            self.assertIn(APIClient().get(url).status_code, (401, 403), url)
        self.assertIn(APIClient().post(self.url(self.exp, 'derivar/')).status_code, (401, 403))

    def test_mesa_ve_todo_y_el_area_no_ve_lo_que_no_es_suyo(self):
        self.assertEqual(sesion('mesa.demo').get('/api/panel/expedientes/').json()['count'], 3)
        self.assertEqual(sesion('area1.demo').get('/api/panel/expedientes/').json()['count'], 0)

    def test_idor_detalle_de_otra_area_da_404(self):
        self.assertEqual(sesion('area1.demo').get(self.url(self.exp)).status_code, 404)
        self.assertEqual(sesion('mesa.demo').get(self.url(self.exp)).status_code, 200)

    def test_usuario_sin_area_no_ve_nada(self):
        from apps.usuarios.models import Usuario
        Usuario.objects.filter(username='area1.demo').update(area=None)
        self.assertEqual(sesion('area1.demo').get('/api/panel/expedientes/').json()['count'], 0)

    def test_filtros_y_fecha_invalida(self):
        mesa = sesion('mesa.demo')
        self.assertEqual(mesa.get('/api/panel/expedientes/?q=queja').json()['count'], 1)
        self.assertEqual(mesa.get('/api/panel/expedientes/?estado=atendido').json()['count'], 0)
        self.assertEqual(mesa.get('/api/panel/expedientes/?desde=no-fecha').status_code, 400)

    def test_consulta_y_reportes_ve_pero_no_actua(self):
        auditor = sesion('auditor.demo')
        self.assertEqual(auditor.get('/api/panel/expedientes/').json()['count'], 3)
        self.assertEqual(self.derivar(auditor, self.exp, self.area1).status_code, 403)
        self.assertEqual(post(auditor, self.url(self.exp, 'cambiar-estado/'), {'estado': 'en-atencion'}).status_code, 403)


class DerivacionTests(BasePanel):
    def test_flujo_completo_derivar_recibir(self):
        mesa, a1, a2 = sesion('mesa.demo'), sesion('area1.demo'), sesion('area2.demo')
        r = self.derivar(mesa, self.exp, self.area1)
        self.assertEqual(r.status_code, 201, r.content)
        self.exp.refresh_from_db()
        self.assertIsNone(self.exp.area_actual)  # sigue en mesa de partes hasta que el área lo reciba
        self.assertEqual(self.exp.estado_actual.codigo, 'en-derivacion')

        # El área destino lo ve (por recibir); la otra área no.
        fila = a1.get('/api/panel/expedientes/').json()['results'][0]
        self.assertTrue(fila['por_recibir'])
        self.assertEqual(a1.get('/api/panel/expedientes/?pendientes=1').json()['count'], 1)
        self.assertEqual(a2.get('/api/panel/expedientes/').json()['count'], 0)
        self.assertEqual(a2.get(self.url(self.exp)).status_code, 404)

        derivacion = Derivacion.objects.get()
        self.assertEqual(post(a2, f'/api/panel/derivaciones/{derivacion.pk}/recibir/').status_code, 404)
        self.assertEqual(post(a1, f'/api/panel/derivaciones/{derivacion.pk}/recibir/').status_code, 200)
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.area_actual, self.area1)
        self.assertEqual(self.exp.estado_actual.codigo, 'en-atencion')
        self.assertEqual(post(a1, f'/api/panel/derivaciones/{derivacion.pk}/recibir/').status_code, 409)  # ya recibida

        # Ahora el área 1 puede derivarlo al área 2.
        self.assertEqual(self.derivar(a1, self.exp, self.area2).status_code, 201)
        acciones = ['DERIVACION_CREADA', 'DERIVACION_RECIBIDA']
        for accion in acciones:
            self.assertTrue(RegistroAuditoria.objects.filter(accion=accion).exists())

    def test_no_se_puede_derivar_dos_veces_pendiente(self):
        mesa = sesion('mesa.demo')
        self.assertEqual(self.derivar(mesa, self.exp, self.area1).status_code, 201)
        self.assertEqual(self.derivar(mesa, self.exp, self.area2).status_code, 409)
        self.assertEqual(Derivacion.objects.filter(expediente=self.exp).count(), 1)

    def test_no_se_cambia_estado_con_derivacion_pendiente(self):
        mesa = sesion('mesa.demo')
        self.derivar(mesa, self.exp, self.area1)
        r = post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'atendido'})
        self.assertEqual(r.status_code, 409)

    def test_derivar_a_area_inactiva_o_inexistente(self):
        mesa = sesion('mesa.demo')
        Area.objects.filter(pk=self.area1.pk).update(activo=False)
        self.assertEqual(self.derivar(mesa, self.exp, self.area1).status_code, 400)
        self.assertEqual(post(mesa, self.url(self.exp, 'derivar/'), {'area': 99999, 'motivo': 'x'}).status_code, 400)

    def test_receptor_designado_debe_ser_del_area_destino(self):
        from apps.usuarios.models import Usuario
        mesa = sesion('mesa.demo')
        area2_user = Usuario.objects.get(username='area2.demo')
        self.assertEqual(self.derivar(mesa, self.exp, self.area1, receptor=area2_user.pk).status_code, 400)
        area1_user = Usuario.objects.get(username='area1.demo')
        self.assertEqual(self.derivar(mesa, self.exp, self.area1, receptor=area1_user.pk).status_code, 201)

    def test_estado_final_bloquea_derivar_y_cambiar(self):
        mesa = sesion('mesa.demo')
        self.assertEqual(post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'atendido'}).status_code, 200)
        self.assertEqual(self.derivar(mesa, self.exp, self.area1).status_code, 409)
        self.assertEqual(post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'archivado'}).status_code, 409)

    def test_cambiar_al_mismo_estado_y_estado_invalido(self):
        mesa = sesion('mesa.demo')
        self.assertEqual(post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'recibido'}).status_code, 400)
        self.assertEqual(post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'inventado'}).status_code, 400)

    def test_cambio_de_estado_guarda_historial_y_notifica(self):
        from django.core import mail
        mesa = sesion('mesa.demo')
        post(mesa, self.url(self.exp, 'cambiar-estado/'), {'estado': 'pendiente-revision', 'observacion': 'Revisando'})
        detalle = mesa.get(self.url(self.exp)).json()
        self.assertEqual(len(detalle['historial']), 2)
        self.assertEqual(detalle['historial'][-1]['usuario'], 'Mesa Demo')
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('Código de verificación', mail.outbox[0].body)

    def test_area_que_no_tiene_el_expediente_no_actua(self):
        a1 = sesion('area1.demo')
        self.assertEqual(post(a1, self.url(self.exp, 'actuaciones/'), {'tipo': 'OBSERVACION', 'texto': 'hola'}).status_code, 404)

    def test_actuacion_y_detalle(self):
        mesa = sesion('mesa.demo')
        r = post(mesa, self.url(self.exp, 'actuaciones/'), {'tipo': 'OBSERVACION', 'texto': 'Falta el anexo 2'})
        self.assertEqual(r.status_code, 201, r.content)
        detalle = mesa.get(self.url(self.exp)).json()
        self.assertEqual(detalle['actuaciones'][0]['texto'], 'Falta el anexo 2')
        self.assertEqual(post(mesa, self.url(self.exp, 'actuaciones/'), {'tipo': 'X', 'texto': 'hola'}).status_code, 400)

    def test_acciones_sin_csrf_se_rechazan(self):
        mesa = sesion('mesa.demo')
        r = APIClient.post(mesa, self.url(self.exp, 'derivar/'), {'area': self.area1.pk, 'motivo': 'x'}, format='json')
        self.assertEqual(r.status_code, 403)


class AdjuntosTests(BasePanel):
    def setUp(self):
        super().setUp()
        self.adjunto = Adjunto(expediente=self.exp, nombre_original='oficio.pdf', extension='pdf', tamano=len(PDF), sha256='0' * 64)
        self.adjunto.archivo.save('oficio.pdf', ContentFile(PDF), save=False)
        self.adjunto.save()
        self.url_descarga = f'/api/panel/adjuntos/{self.adjunto.pk}/descargar/'

    def test_descarga_con_cabeceras_seguras_y_auditoria(self):
        r = sesion('mesa.demo').get(self.url_descarga)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), PDF)
        self.assertIn('attachment', r['Content-Disposition'])
        self.assertEqual(r['X-Content-Type-Options'], 'nosniff')
        self.assertTrue(RegistroAuditoria.objects.filter(accion='ADJUNTO_DESCARGADO').exists())

    def test_anonimo_y_otra_area_no_descargan(self):
        self.assertIn(APIClient().get(self.url_descarga).status_code, (401, 403))
        self.assertEqual(sesion('area2.demo').get(self.url_descarga).status_code, 404)

    def test_detalle_no_expone_rutas_internas(self):
        texto = str(sesion('mesa.demo').get(self.url(self.exp)).json())
        self.assertNotIn(self._carpeta, texto)
        self.assertNotIn('adjuntos/', texto)

    def test_el_adjunto_no_se_puede_eliminar(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.adjunto.delete()
