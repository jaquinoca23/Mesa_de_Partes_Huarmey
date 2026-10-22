"""Pruebas de la ETAPA 5: registro de expedientes, cargo y consulta pública."""
import shutil
import tempfile
import uuid

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.auditoria.models import RegistroAuditoria
from apps.catalogos.models import EstadoExpediente, TipoDocumental
from apps.documentos.models import Adjunto
from apps.notificaciones.models import Notificacion

from .models import Expediente, HistorialEstado, Solicitante
from .servicios import enmascarar_documento

PDF_VALIDO = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n'
URL_REGISTRO = '/api/solicitudes/'
URL_CONSULTA = '/api/seguimiento/consultar/'


def datos_validos(**cambios):
    datos = {
        'clave_envio': str(uuid.uuid4()),
        'tipo_persona': 'NATURAL',
        'tipo_documento_identidad': 'DNI',
        'numero_documento': '00000001',
        'nombres': 'Ana',
        'apellidos': 'Ejemplo',
        'email': 'ana@example.com',
        'telefono': '900000001',
        'tipo_documental': 'solicitud',
        'asunto': 'Asunto de prueba',
        'descripcion': 'Texto de prueba',
        'acepta_politica_privacidad': 'true',
        'declara_veracidad': 'true',
    }
    datos.update(cambios)
    return datos


def pdf(nombre='oficio.pdf'):
    return SimpleUploadedFile(nombre, PDF_VALIDO, content_type='application/pdf')


class BaseRegistro(TestCase):
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
        TipoDocumental.objects.create(codigo='solicitud', nombre='Solicitud', orden=1)
        cls.inicial = EstadoExpediente.objects.create(codigo='recibido', nombre='Recibido', es_inicial=True, orden=1)

    def setUp(self):
        cache.clear()

    def registrar(self, archivos=(), **cambios):
        datos = datos_validos(**cambios)
        if archivos:
            datos['archivos'] = list(archivos)
        return self.client.post(URL_REGISTRO, datos)


class RegistroTests(BaseRegistro):
    def test_registro_correcto_crea_expediente_historial_y_cargo(self):
        r = self.registrar(archivos=[pdf()])
        self.assertEqual(r.status_code, 201)
        cuerpo = r.json()
        self.assertTrue(cuerpo['registrado'])
        self.assertFalse(cuerpo['duplicado'])
        cargo = cuerpo['cargo']
        self.assertRegex(cargo['numero'], r'^\d{4}-\d{6}$')
        self.assertEqual(len(cargo['codigo_verificacion']), 8)
        self.assertTrue(cargo['advertencias'])
        self.assertEqual(cargo['documento_identidad'], 'DNI ******01')
        expediente = Expediente.objects.get(numero=cargo['numero'])
        self.assertEqual(expediente.estado_actual, self.inicial)
        self.assertEqual(HistorialEstado.objects.filter(expediente=expediente).count(), 1)
        self.assertEqual(Adjunto.objects.filter(expediente=expediente).count(), 1)
        self.assertTrue(RegistroAuditoria.objects.filter(accion='EXPEDIENTE_REGISTRADO').exists())

    def test_el_cargo_no_expone_rutas_internas(self):
        cargo = self.registrar(archivos=[pdf()]).json()['cargo']
        texto = str(cargo)
        self.assertNotIn('adjuntos/', texto)
        self.assertNotIn(self._carpeta, texto)

    def test_archivo_guardado_con_nombre_aleatorio(self):
        self.registrar(archivos=[pdf('mi-oficio.pdf')])
        adjunto = Adjunto.objects.get()
        self.assertNotIn('mi-oficio', adjunto.archivo.name)
        self.assertEqual(adjunto.nombre_original, 'mi-oficio.pdf')
        self.assertEqual(len(adjunto.sha256), 64)

    def test_envio_repetido_no_duplica(self):
        clave = str(uuid.uuid4())
        primero = self.registrar(clave_envio=clave)
        segundo = self.registrar(clave_envio=clave)
        self.assertEqual(primero.status_code, 201)
        self.assertEqual(segundo.status_code, 200)
        self.assertTrue(segundo.json()['duplicado'])
        self.assertEqual(primero.json()['cargo']['numero'], segundo.json()['cargo']['numero'])
        self.assertEqual(Expediente.objects.count(), 1)

    def test_numeros_correlativos_distintos(self):
        a = self.registrar().json()['cargo']['numero']
        b = self.registrar().json()['cargo']['numero']
        self.assertNotEqual(a, b)

    def test_datos_invalidos_no_registran(self):
        r = self.registrar(email='no-es-correo')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()['registrado'])
        self.assertEqual(Expediente.objects.count(), 0)

    def test_archivo_invalido_no_registra_nada(self):
        falso = SimpleUploadedFile('informe.pdf', b'MZ\x90\x00', content_type='application/pdf')
        r = self.registrar(archivos=[falso])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Expediente.objects.count(), 0)
        self.assertEqual(Adjunto.objects.count(), 0)

    def test_sin_estado_inicial_responde_503_y_no_guarda(self):
        EstadoExpediente.objects.all().delete()
        r = self.registrar()
        self.assertEqual(r.status_code, 503)
        self.assertFalse(r.json()['registrado'])
        self.assertEqual(Expediente.objects.count(), 0)

    def test_solicitante_existente_no_se_sobrescribe(self):
        self.registrar(nombres='Ana', apellidos='Original')
        self.registrar(nombres='Intruso', apellidos='Cambiado', email='otro@example.com')
        persona = Solicitante.objects.get(numero_documento='00000001')
        self.assertEqual(persona.apellidos, 'Original')
        self.assertEqual(Expediente.objects.count(), 2)
        self.assertEqual(Expediente.objects.latest('id').email_contacto, 'otro@example.com')

    def test_se_envia_correo_y_se_registra_sin_cuerpo(self):
        self.registrar()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Código de verificación', mail.outbox[0].body)
        notificacion = Notificacion.objects.get()
        self.assertEqual(notificacion.estado, 'ENVIADA')

    @override_settings(EMAIL_BACKEND='apps.expedientes.test_registro.CorreoRoto')
    def test_fallo_de_correo_no_impide_el_registro(self):
        r = self.registrar()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Notificacion.objects.get().estado, 'FALLIDA')

    def test_enmascarar_documento(self):
        self.assertEqual(enmascarar_documento('12345678'), '******78')
        self.assertEqual(enmascarar_documento('1'), '*')


from django.core.mail.backends.base import BaseEmailBackend  # noqa: E402


class CorreoRoto(BaseEmailBackend):
    def send_messages(self, mensajes):
        raise ConnectionError('simulado')


class ConsultaPublicaTests(BaseRegistro):
    def setUp(self):
        super().setUp()
        self.cargo = self.registrar().json()['cargo']

    def consultar(self, numero=None, codigo=None):
        return self.client.post(
            URL_CONSULTA,
            {'numero': numero or self.cargo['numero'], 'codigo': codigo or self.cargo['codigo_verificacion']},
            content_type='application/json',
        )

    def test_consulta_correcta(self):
        r = self.consultar()
        self.assertEqual(r.status_code, 200)
        cuerpo = r.json()
        self.assertEqual(cuerpo['estado'], 'Recibido')
        self.assertEqual(len(cuerpo['historial']), 1)
        self.assertNotIn('00000001', str(cuerpo))

    def test_codigo_en_minusculas_se_acepta(self):
        self.assertEqual(self.consultar(codigo=self.cargo['codigo_verificacion'].lower()).status_code, 200)

    def test_codigo_incorrecto_y_numero_inexistente_dan_la_misma_respuesta(self):
        a = self.consultar(codigo='AAAAAAAA')
        b = self.consultar(numero='2026-999999', codigo='AAAAAAAA')
        self.assertEqual(a.status_code, 404)
        self.assertEqual(b.status_code, 404)
        self.assertEqual(a.json(), b.json())

    def test_faltan_datos(self):
        r = self.client.post(URL_CONSULTA, {'numero': '2026-000001'}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_limite_de_intentos(self):
        codigos = [self.consultar(codigo='AAAAAAAA').status_code for _ in range(32)]
        self.assertIn(429, codigos)
