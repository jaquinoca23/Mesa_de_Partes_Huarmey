"""
Consulta de nombres por número de DNI en un servicio externo (por defecto APIsPERU).

- El token vive SOLO en backend/.env (IDENTIDAD_API_TOKEN). Nunca llega al navegador, ni a los logs.
- No se guarda nada: el resultado se devuelve para autocompletar el formulario y se descarta.
- No se siguen redirecciones (así el token no puede enviarse a otro servidor por error).
- Es un servicio de TERCEROS no oficial: para producción corresponde un convenio con RENIEC / PIDE.
"""
import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)
PATRON_DNI = re.compile(r'^\d{8}$')


class ErrorIdentidad(Exception):
    """Fallo de la consulta. 'estado' es el código HTTP que se devolverá a React."""

    def __init__(self, mensaje, estado):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.estado = estado


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # una redirección se trata como error (HTTPError)


def esta_configurado():
    return bool(settings.IDENTIDAD_API_TOKEN and settings.IDENTIDAD_API_URL.startswith('https://'))


def _abrir(solicitud, timeout):
    """Separado en una función para poder simularlo en las pruebas."""
    return urllib.request.build_opener(_SinRedireccion).open(solicitud, timeout=timeout)


def _texto(valor):
    return ' '.join(str(valor or '').split())[:150]


def consultar_dni(dni):
    """Devuelve {'nombres': ..., 'apellidos': ...} o lanza ErrorIdentidad."""
    if not PATRON_DNI.match(dni or ''):
        raise ErrorIdentidad('El DNI debe tener 8 dígitos.', 400)
    if not esta_configurado():
        raise ErrorIdentidad('La verificación de DNI no está disponible en este momento. Escribe tus datos manualmente.', 503)

    solicitud = urllib.request.Request(
        f"{settings.IDENTIDAD_API_URL.rstrip('/')}/{dni}",
        headers={'Authorization': f'Bearer {settings.IDENTIDAD_API_TOKEN}', 'Accept': 'application/json'},
    )
    no_disponible = ErrorIdentidad('La verificación de DNI no está disponible en este momento. Escribe tus datos manualmente.', 503)
    try:
        with _abrir(solicitud, settings.IDENTIDAD_TIMEOUT) as respuesta:
            datos = json.loads(respuesta.read(65536).decode('utf-8'))
    except urllib.error.HTTPError as error:
        if error.code in (404, 422):
            raise ErrorIdentidad('No se encontró información para ese DNI.', 404)
        # 401/403 (token inválido), 429 (límite del plan), redirecciones, 5xx...: es un problema nuestro o del proveedor.
        logger.error('Proveedor de DNI respondió con código %s.', error.code)
        raise no_disponible
    except (urllib.error.URLError, TimeoutError, OSError):
        logger.error('No se pudo conectar con el proveedor de DNI.')
        raise no_disponible
    except (ValueError, UnicodeDecodeError):
        logger.error('El proveedor de DNI devolvió una respuesta ilegible.')
        raise no_disponible

    if not isinstance(datos, dict) or not _texto(datos.get('nombres')):
        raise ErrorIdentidad('No se encontró información para ese DNI.', 404)
    apellidos = f"{_texto(datos.get('apellidoPaterno'))} {_texto(datos.get('apellidoMaterno'))}".strip()
    return {'nombres': _texto(datos['nombres']), 'apellidos': apellidos}
