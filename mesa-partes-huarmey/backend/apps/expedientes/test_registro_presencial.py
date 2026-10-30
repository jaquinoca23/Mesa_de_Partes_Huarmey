"""Registro presencial: permisos, archivos, derivación y reintentos."""
import uuid
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.auditoria.models import RegistroAuditoria
from apps.derivaciones.models import Derivacion
from .models import Expediente
from .servicios import ErrorDeRegla
from .test_panel import BasePanel, PDF, sesion


class RegistroPresencialTests(BasePanel):
    ruta = '/api/panel/expedientes/registrar/'

    def datos(self, clave=None, **cambios):
        return {
            'clave_envio': str(clave or uuid.uuid4()), 'tipo_persona': 'NATURAL',
            'tipo_documento_identidad': 'DNI', 'numero_documento': '87654321',
            'nombres': 'Persona', 'apellidos': 'De Prueba',
            'tipo_documental': self.exp.tipo_documental.codigo,
            'asunto': 'Documento recibido presencialmente',
            'area': self.area1.pk, 'mensaje': 'Por favor revisar los anexos.',
            'documento': SimpleUploadedFile('escaneo.pdf', PDF, content_type='application/pdf'),
            'anexos': [SimpleUploadedFile('anexo.pdf', PDF, content_type='application/pdf')],
            **cambios,
        }

    def enviar(self, cliente, datos):
        return cliente.post(self.ruta, datos, format='multipart', HTTP_X_CSRFTOKEN=cliente.cookies['csrftoken'].value)

    def test_registro_guarda_principal_anexos_mensaje_y_trazabilidad(self):
        cliente = sesion('mesa.demo')
        r = self.enviar(cliente, self.datos())
        self.assertEqual(r.status_code, 201, r.content)
        exp = Expediente.objects.get(uuid=r.json()['uuid'])
        self.assertEqual(exp.adjuntos.count(), 2)
        self.assertEqual(exp.adjuntos.get(es_principal=True).nombre_original, 'escaneo.pdf')
        self.assertEqual(exp.email_contacto, '')
        derivacion = exp.derivaciones.get()
        self.assertEqual(derivacion.area_destino_id, self.area1.pk)
        self.assertEqual(derivacion.observaciones, 'Por favor revisar los anexos.')
        self.assertEqual(derivacion.estado_recepcion, Derivacion.EstadoRecepcion.PENDIENTE)
        self.assertEqual(exp.historial.first().usuario.username, 'mesa.demo')
        self.assertIn('física', exp.historial.first().observacion)
        self.assertTrue(RegistroAuditoria.objects.filter(accion='EXPEDIENTE_REGISTRADO', objeto_id=str(exp.pk)).exists())
        detalle = cliente.get(self.url(exp)).json()
        self.assertTrue(detalle['adjuntos'][0]['es_principal'])
        self.assertEqual(sesion('area1.demo').get(self.url(exp)).status_code, 200)

    def test_reintento_no_duplica_documentos_ni_derivaciones(self):
        cliente = sesion('mesa.demo')
        clave = uuid.uuid4()
        primero = self.enviar(cliente, self.datos(clave)).json()
        segundo = self.enviar(cliente, self.datos(clave))
        self.assertEqual(segundo.status_code, 200, segundo.content)
        self.assertEqual(primero['uuid'], segundo.json()['uuid'])
        exp = Expediente.objects.get(uuid=primero['uuid'])
        self.assertEqual(exp.adjuntos.count(), 2)
        self.assertEqual(exp.derivaciones.count(), 1)

    def test_exige_permiso_y_csrf(self):
        self.assertIn(APIClient().post(self.ruta).status_code, (401, 403))
        self.assertEqual(self.enviar(sesion('area1.demo'), self.datos()).status_code, 403)
        self.assertEqual(sesion('mesa.demo').post(self.ruta, self.datos(), format='multipart').status_code, 403)

    def test_rechaza_archivos_invalidos_y_falta_de_documento(self):
        cliente = sesion('mesa.demo')
        antes = Expediente.objects.count()
        d = self.datos()
        del d['documento']
        self.assertEqual(self.enviar(cliente, d).status_code, 400)
        r = self.enviar(cliente, self.datos(documento=SimpleUploadedFile('falso.pdf', b'no es pdf')))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Expediente.objects.count(), antes)

    def test_derivacion_fallida_revierte_registro_y_archivos(self):
        cliente = sesion('mesa.demo')
        antes = Expediente.objects.count()
        archivos = set(Path(self._carpeta).rglob('*.*'))
        with patch('apps.expedientes.servicios.derivar', side_effect=ErrorDeRegla('No se pudo derivar.')):
            r = self.enviar(cliente, self.datos())
        self.assertEqual(r.status_code, 409)
        self.assertEqual(Expediente.objects.count(), antes)
        self.assertEqual(set(Path(self._carpeta).rglob('*.*')), archivos)

    def test_area_inactiva_y_limites_no_guardan_expediente(self):
        cliente = sesion('mesa.demo')
        antes = Expediente.objects.count()
        self.area1.activo = False
        self.area1.save()
        self.assertEqual(self.enviar(cliente, self.datos()).status_code, 400)
        self.area1.activo = True
        self.area1.save()
        from django.test import override_settings
        with override_settings(UPLOAD_MAX_FILES=1):
            self.assertEqual(self.enviar(cliente, self.datos()).status_code, 400)
        self.assertEqual(Expediente.objects.count(), antes)
