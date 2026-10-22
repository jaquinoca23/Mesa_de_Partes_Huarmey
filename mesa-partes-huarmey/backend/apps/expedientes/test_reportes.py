"""Pruebas de la ETAPA 8: resumen, reportes, exportación CSV y auditoría."""
import csv
import io

from django.contrib.auth.models import Group, Permission
from rest_framework.test import APIClient

from apps.auditoria.models import RegistroAuditoria
from apps.catalogos.models import EstadoExpediente

from .models import Expediente
from .test_panel import BasePanel, post, sesion


def texto_csv(respuesta):
    return respuesta.content.decode('utf-8-sig')


class DashboardTests(BasePanel):
    def test_anonimo_no_accede(self):
        for url in ['/api/panel/dashboard/', '/api/panel/reportes/resumen/', '/api/panel/reportes/exportar.csv', '/api/panel/auditoria/']:
            self.assertIn(APIClient().get(url).status_code, (401, 403), url)

    def test_dashboard_limitado_a_lo_visible(self):
        mesa = sesion('mesa.demo').get('/api/panel/dashboard/').json()
        self.assertEqual(mesa['total'], 3)
        self.assertEqual(mesa['por_estado'][0]['total'], 3)
        self.assertEqual(sesion('area1.demo').get('/api/panel/dashboard/').json()['total'], 0)

    def test_dashboard_cuenta_pendientes_por_recibir(self):
        post(sesion('mesa.demo'), self.url(self.exp, 'derivar/'), {'area': self.area1.pk, 'motivo': 'x'})
        datos = sesion('area1.demo').get('/api/panel/dashboard/').json()
        self.assertEqual(datos['por_recibir'], 1)
        self.assertEqual(datos['total'], 1)


class ReportesTests(BasePanel):
    def test_resumen_exige_permiso_de_reportes(self):
        self.assertEqual(sesion('area1.demo').get('/api/panel/reportes/resumen/').status_code, 403)
        self.assertEqual(sesion('mesa.demo').get('/api/panel/reportes/resumen/').status_code, 403)  # sin ver_reportes
        r = sesion('auditor.demo').get('/api/panel/reportes/resumen/')
        self.assertEqual(r.status_code, 200)
        datos = r.json()
        self.assertEqual(datos['total'], 3)
        self.assertTrue(datos['por_tipo'])
        self.assertTrue(datos['por_mes'])

    def test_resumen_respeta_filtros_y_fecha_invalida(self):
        auditor = sesion('auditor.demo')
        self.assertEqual(auditor.get('/api/panel/reportes/resumen/?estado=atendido').json()['total'], 0)
        self.assertEqual(auditor.get('/api/panel/reportes/resumen/?desde=ayer').status_code, 400)

    def test_funcionario_con_permiso_de_reportes_solo_ve_su_area(self):
        grupo = Group.objects.get(name='Funcionario de área')
        grupo.permissions.add(Permission.objects.get(codename='ver_reportes'))
        self.assertEqual(sesion('area1.demo').get('/api/panel/reportes/resumen/').json()['total'], 0)
        self.assertEqual(sesion('area1.demo').get('/api/panel/reportes/exportar.csv').content.decode('utf-8-sig').count('\n'), 1)

    def test_csv_correcto_sin_datos_personales_y_con_auditoria(self):
        r = sesion('auditor.demo').get('/api/panel/reportes/exportar.csv')
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/csv', r['Content-Type'])
        self.assertIn('attachment', r['Content-Disposition'])
        self.assertTrue(r.content.startswith('﻿'.encode('utf-8')))
        filas = list(csv.reader(io.StringIO(texto_csv(r))))
        self.assertEqual(len(filas), 4)  # encabezado + 3 expedientes
        contenido = texto_csv(r)
        self.assertNotIn('example.com', contenido)
        self.assertNotIn('00000001', contenido)
        self.assertTrue(RegistroAuditoria.objects.filter(accion='REPORTE_EXPORTADO').exists())

    def test_csv_neutraliza_formulas(self):
        Expediente.objects.filter(pk=self.exp.pk).update(asunto='=HYPERLINK("http://malo.example","clic")')
        filas = list(csv.reader(io.StringIO(texto_csv(sesion('auditor.demo').get('/api/panel/reportes/exportar.csv')))))
        asuntos = [f[3] for f in filas[1:]]
        self.assertIn('\'=HYPERLINK("http://malo.example","clic")', asuntos)
        self.assertFalse(any(a.startswith('=') for a in asuntos))

    def test_csv_con_fecha_invalida(self):
        self.assertEqual(sesion('auditor.demo').get('/api/panel/reportes/exportar.csv?hasta=x').status_code, 400)

    def test_celda_segura(self):
        from .views_reportes import celda_segura
        for peligroso in ('=1+1', '+1', '-1', '@SUM(A1)', '\tx'):
            self.assertTrue(celda_segura(peligroso).startswith("'"))
        self.assertEqual(celda_segura('Texto normal'), 'Texto normal')
        self.assertEqual(celda_segura(None), '')


class AuditoriaPanelTests(BasePanel):
    def test_permisos(self):
        self.assertEqual(sesion('area1.demo').get('/api/panel/auditoria/').status_code, 403)
        self.assertEqual(sesion('mesa.demo').get('/api/panel/auditoria/').status_code, 403)
        self.assertEqual(sesion('auditor.demo').get('/api/panel/auditoria/').status_code, 200)
        self.assertEqual(sesion('admin.demo').get('/api/panel/auditoria/').status_code, 200)

    def test_lista_filtra_y_no_expone_contrasenas(self):
        sesion('mesa.demo')  # genera un LOGIN
        auditor = sesion('auditor.demo')
        datos = auditor.get('/api/panel/auditoria/?accion=LOGIN').json()
        self.assertGreaterEqual(datos['count'], 2)
        self.assertTrue(all(f['accion'] == 'Inicio de sesión' for f in datos['results']))
        self.assertNotIn('Clave-Segura', str(datos))
        self.assertEqual(auditor.get('/api/panel/auditoria/?desde=zz').status_code, 400)

    def test_es_solo_lectura(self):
        auditor = sesion('auditor.demo')
        for metodo in (auditor.post, auditor.put, auditor.patch, auditor.delete):
            self.assertEqual(metodo('/api/panel/auditoria/', {}, format='json', HTTP_X_CSRFTOKEN=auditor.cookies['csrftoken'].value).status_code, 405)

    def test_cambio_de_estado_aparece_en_la_bitacora(self):
        post(sesion('mesa.demo'), self.url(self.exp, 'cambiar-estado/'), {'estado': 'pendiente-revision'})
        datos = sesion('auditor.demo').get('/api/panel/auditoria/?accion=ESTADO_CAMBIADO').json()
        self.assertEqual(datos['count'], 1)
        self.assertIn('Recibido', datos['results'][0]['detalle'])
