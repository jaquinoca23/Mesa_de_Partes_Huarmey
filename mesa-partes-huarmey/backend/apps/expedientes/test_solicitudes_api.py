import uuid

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.catalogos.models import TipoDocumental

from .models import Expediente, Solicitante

PDF_VALIDO = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n'
URL_VALIDAR = '/api/solicitudes/validar/'


def datos_validos(**cambios):
    """Datos mínimos correctos (todos ficticios). 'cambios' sobrescribe o agrega campos."""
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


def pdf(nombre='oficio.pdf', contenido=PDF_VALIDO):
    return SimpleUploadedFile(nombre, contenido, content_type='application/pdf')


class SolicitudesApiBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        TipoDocumental.objects.create(codigo='solicitud', nombre='Solicitud', orden=1)
        TipoDocumental.objects.create(codigo='viejo', nombre='Tipo inactivo', activo=False, orden=2)

    def setUp(self):
        cache.clear()  # reinicia el contador de límite de intentos entre pruebas

    def enviar(self, **cambios):
        return self.client.post(URL_VALIDAR, datos_validos(**cambios))


class CatalogosYConfiguracionTests(SolicitudesApiBase):
    def test_tipos_documentales_solo_activos_y_sin_datos_internos(self):
        respuesta = self.client.get('/api/catalogos/tipos-documentales/')
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual([t['codigo'] for t in datos], ['solicitud'])
        self.assertEqual(set(datos[0]), {'codigo', 'nombre', 'descripcion'})

    def test_configuracion_publica_incluye_limites(self):
        respuesta = self.client.get('/api/solicitudes/configuracion/')
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertIn('pdf', datos['archivos']['extensiones_permitidas'])
        self.assertGreater(datos['archivos']['max_tamano_mb'], 0)
        self.assertTrue(datos['tipos_persona'])
        self.assertTrue(datos['tipos_documento_identidad'])


class ValidarSolicitudTests(SolicitudesApiBase):
    def test_datos_correctos_se_validan_pero_no_se_registran(self):
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertTrue(cuerpo['ok'])
        self.assertFalse(cuerpo['registrado'])
        # En la ETAPA 4 el servidor NO guarda nada.
        self.assertEqual(Expediente.objects.count(), 0)
        self.assertEqual(Solicitante.objects.count(), 0)

    def test_campos_obligatorios(self):
        respuesta = self.client.post(URL_VALIDAR, {})
        self.assertEqual(respuesta.status_code, 400)
        cuerpo = respuesta.json()
        self.assertFalse(cuerpo['ok'])
        self.assertFalse(cuerpo['registrado'])
        for campo in ('email', 'asunto', 'tipo_documental', 'numero_documento', 'acepta_politica_privacidad'):
            self.assertIn(campo, cuerpo['errores'])

    def test_dni_con_formato_incorrecto(self):
        respuesta = self.enviar(numero_documento='123')
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('numero_documento', respuesta.json()['errores'])

    def test_persona_natural_exige_nombres_y_apellidos(self):
        respuesta = self.enviar(nombres='', apellidos='')
        errores = respuesta.json()['errores']
        self.assertIn('nombres', errores)
        self.assertIn('apellidos', errores)

    def test_persona_juridica_exige_ruc_y_razon_social(self):
        respuesta = self.enviar(tipo_persona='JURIDICA', tipo_documento_identidad='DNI', razon_social='')
        errores = respuesta.json()['errores']
        self.assertIn('razon_social', errores)
        self.assertIn('tipo_documento_identidad', errores)

    def test_persona_juridica_correcta(self):
        respuesta = self.enviar(
            tipo_persona='JURIDICA',
            tipo_documento_identidad='RUC',
            numero_documento='00000000001',
            razon_social='Empresa de Ejemplo S.A.C. (FICTICIA)',
            nombres='',
            apellidos='',
        )
        self.assertEqual(respuesta.status_code, 200)

    def test_exige_aceptar_politica_y_veracidad(self):
        respuesta = self.enviar(acepta_politica_privacidad='false', declara_veracidad='false')
        errores = respuesta.json()['errores']
        self.assertIn('acepta_politica_privacidad', errores)
        self.assertIn('declara_veracidad', errores)

    def test_correo_invalido(self):
        respuesta = self.enviar(email='no-es-un-correo')
        self.assertIn('email', respuesta.json()['errores'])

    def test_tipo_documental_inactivo_o_inexistente(self):
        for codigo in ('viejo', 'no-existe'):
            respuesta = self.enviar(tipo_documental=codigo)
            self.assertEqual(respuesta.status_code, 400, codigo)
            self.assertIn('tipo_documental', respuesta.json()['errores'])

    def test_no_acepta_get(self):
        self.assertEqual(self.client.get(URL_VALIDAR).status_code, 405)

    def test_los_errores_no_revelan_informacion_interna(self):
        texto = self.client.post(URL_VALIDAR, {'tipo_persona': 'X'}).content.decode()
        for palabra in ('Traceback', 'settings.py', 'SECRET_KEY', 'psycopg'):
            self.assertNotIn(palabra, texto)


class ArchivosAdjuntosTests(SolicitudesApiBase):
    def test_pdf_valido_aceptado(self):
        respuesta = self.enviar(archivos=[pdf()])
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['archivos_validados'], 1)

    def test_ejecutable_disfrazado_de_pdf_rechazado(self):
        falso = pdf('informe.pdf', b'MZ\x90\x00\x03\x00\x00\x00')
        respuesta = self.enviar(archivos=[falso])
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('archivos', respuesta.json()['errores'])

    def test_extension_enganosa_rechazada(self):
        respuesta = self.enviar(archivos=[pdf('informe.exe.pdf')])
        self.assertEqual(respuesta.status_code, 400)
        self.assertTrue(any('engañosa' in m for m in respuesta.json()['errores']['archivos']))

    def test_extension_no_permitida_rechazada(self):
        malo = SimpleUploadedFile('programa.exe', b'MZ\x90\x00', content_type='application/octet-stream')
        respuesta = self.enviar(archivos=[malo])
        self.assertEqual(respuesta.status_code, 400)

    @override_settings(UPLOAD_MAX_FILES=2)
    def test_demasiados_archivos(self):
        respuesta = self.enviar(archivos=[pdf('a.pdf'), pdf('b.pdf'), pdf('c.pdf')])
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('archivos', respuesta.json()['errores'])

    @override_settings(UPLOAD_MAX_FILE_SIZE_MB=0.00001)  # unos 10 bytes
    def test_archivo_demasiado_grande(self):
        respuesta = self.enviar(archivos=[pdf()])
        self.assertEqual(respuesta.status_code, 400)
        self.assertTrue(any('tamaño máximo' in m for m in respuesta.json()['errores']['archivos']))

    def test_errores_de_datos_y_de_archivos_se_informan_juntos(self):
        respuesta = self.enviar(asunto='', archivos=[pdf('malo.exe')])
        errores = respuesta.json()['errores']
        self.assertIn('asunto', errores)
        self.assertIn('archivos', errores)
