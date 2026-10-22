import hashlib
from functools import partial

from django.conf import settings
from django.core.files.base import ContentFile

from . import validadores
from .models import Adjunto


def _leer_todo(archivo):
    """Lee el contenido completo de un archivo subido y lo deja listo para volver a leerse."""
    archivo.seek(0)
    contenido = archivo.read()
    archivo.seek(0)
    return contenido


def validar_archivos_subidos(archivos):
    """
    Valida los archivos recibidos en una petición con los límites de settings.py
    (UPLOAD_MAX_FILES, UPLOAD_MAX_FILE_SIZE_MB, UPLOAD_ALLOWED_EXTENSIONS).
    Devuelve una lista de mensajes de error (vacía = todo correcto).
    """
    return validadores.validar_lista(
        [(a.name, a.size, partial(_leer_todo, a)) for a in archivos],
        extensiones_permitidas=settings.UPLOAD_ALLOWED_EXTENSIONS,
        tamano_max_bytes=settings.UPLOAD_MAX_FILE_SIZE_MB * 1024 * 1024,
        max_archivos=settings.UPLOAD_MAX_FILES,
    )


def guardar_adjunto(expediente, archivo_subido):
    """
    Guarda un archivo YA VALIDADO en la carpeta privada y crea su registro en la base de datos.
    Se calcula su huella SHA-256 para poder comprobar después que no fue alterado.
    """
    contenido = _leer_todo(archivo_subido)
    adjunto = Adjunto(
        expediente=expediente,
        nombre_original=validadores.sanear_nombre(archivo_subido.name),
        extension=archivo_subido.name.rsplit('.', 1)[-1].lower(),
        tamano=len(contenido),
        sha256=hashlib.sha256(contenido).hexdigest(),
    )
    adjunto.archivo.save(archivo_subido.name, ContentFile(contenido), save=False)
    adjunto.save()
    return adjunto
