"""Pruebas de la consulta de DNI. El proveedor externo se SIMULA: no se hacen llamadas reales."""
import json
import urllib.error
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings

from . import servicios

CONFIG = dict(IDENTIDAD_API_URL='https://proveedor.example/api/v1/dni', IDENTIDAD_API_TOKEN='TOKEN-SECRETO-DE-PRUEBA', IDENTIDAD_TIMEOUT=3)
URL = '/api/identidad/dni/12345678/'


class RespuestaFalsa:
    def __init__(self, cuerpo):
        self._cuerpo = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo).encode()

    def read(self, n=-1):
        return self._cuerpo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def error_http(codigo):
    return urllib.error.HTTPError('https://proveedor.example', codigo, 'x', {}, None)


@override_settings(**CONFIG)
class ConsultaDniTests(TestCase):
    def setUp(self):
        cache.clear()

    @mock.patch('apps.identidad.servicios._abrir')
    def test_respuesta_correcta_une_apellidos(self, abrir):
        abrir.return_value = RespuestaFalsa({'dni': '12345678', 'nombres': 'ANA MARIA', 'apellidoPaterno': 'EJEMPLO', 'apellidoMaterno': 'UNO', 'codVerifica': '1'})
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'ok': True, 'nombres': 'ANA MARIA', 'apellidos': 'EJEMPLO UNO'})
        self.assertEqual(r['Cache-Control'], 'no-store')
        self.assertNotIn('codVerifica', r.json())

    @mock.patch('apps.identidad.servicios._abrir')
    def test_el_token_va_en_la_cabecera_y_no_en_la_url(self, abrir):
        abrir.return_value = RespuestaFalsa({'nombres': 'ANA', 'apellidoPaterno': 'X', 'apellidoMaterno': ''})
        self.client.get(URL)
        solicitud = abrir.call_args[0][0]
        self.assertEqual(solicitud.get_header('Authorization'), 'Bearer TOKEN-SECRETO-DE-PRUEBA')
        self.assertNotIn('TOKEN-SECRETO', solicitud.full_url)
        self.assertTrue(solicitud.full_url.endswith('/12345678'))

    def test_dni_invalido_no_llega_al_proveedor(self):
        with mock.patch('apps.identidad.servicios._abrir') as abrir:
            for malo in ('1234567', '123456789', 'abcdefgh', '1234567a'):
                self.assertEqual(self.client.get(f'/api/identidad/dni/{malo}/').status_code, 400, malo)
            abrir.assert_not_called()

    @mock.patch('apps.identidad.servicios._abrir')
    def test_dni_no_encontrado(self, abrir):
        abrir.side_effect = error_http(404)
        self.assertEqual(self.client.get(URL).status_code, 404)
        abrir.side_effect = None
        abrir.return_value = RespuestaFalsa({'success': False, 'message': 'no existe'})
        self.assertEqual(self.client.get(URL).status_code, 404)

    @mock.patch('apps.identidad.servicios._abrir')
    def test_fallos_del_proveedor_dan_503_sin_filtrar_detalles(self, abrir):
        for efecto in (error_http(401), error_http(429), error_http(500), error_http(302), urllib.error.URLError('x'), TimeoutError(), RespuestaFalsa(b'no es json')):
            if isinstance(efecto, Exception):
                abrir.side_effect, abrir.return_value = efecto, None
            else:
                abrir.side_effect, abrir.return_value = None, efecto
            r = self.client.get(URL)
            self.assertEqual(r.status_code, 503, repr(efecto))
            self.assertNotIn('TOKEN', r.content.decode())
            self.assertNotIn('proveedor.example', r.content.decode())
            cache.clear()

    @override_settings(IDENTIDAD_API_TOKEN='')
    def test_sin_token_la_funcion_esta_desactivada(self):
        self.assertEqual(self.client.get(URL).status_code, 503)
        self.assertFalse(servicios.esta_configurado())
        self.assertFalse(self.client.get('/api/solicitudes/configuracion/').json()['verificacion_dni'])

    @override_settings(IDENTIDAD_API_URL='http://inseguro.example/dni')
    def test_exige_https(self):
        self.assertFalse(servicios.esta_configurado())
        self.assertEqual(self.client.get(URL).status_code, 503)

    def test_configuracion_publica_avisa_que_esta_activa(self):
        self.assertTrue(self.client.get('/api/solicitudes/configuracion/').json()['verificacion_dni'])
        self.assertNotIn('TOKEN-SECRETO', self.client.get('/api/solicitudes/configuracion/').content.decode())

    @mock.patch('apps.identidad.servicios._abrir')
    def test_limite_de_consultas(self, abrir):
        abrir.return_value = RespuestaFalsa({'nombres': 'ANA', 'apellidoPaterno': 'X', 'apellidoMaterno': 'Y'})
        codigos = [self.client.get(URL).status_code for _ in range(25)]
        self.assertIn(429, codigos)

    @mock.patch('apps.identidad.servicios._abrir')
    def test_texto_se_limpia(self, abrir):
        abrir.return_value = RespuestaFalsa({'nombres': '  ANA   MARIA ', 'apellidoPaterno': 'A' * 400, 'apellidoMaterno': None})
        datos = self.client.get(URL).json()
        self.assertEqual(datos['nombres'], 'ANA MARIA')
        self.assertEqual(len(datos['apellidos']), 150)

    def test_no_sigue_redirecciones(self):
        handler = servicios._SinRedireccion()
        self.assertIsNone(handler.redirect_request(None, None, 302, 'x', {}, 'http://otro.example'))
