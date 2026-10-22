import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class AlmacenamientoPrivado(FileSystemStorage):
    """
    Guarda en la carpeta PRIVADA (settings.PRIVATE_MEDIA_ROOT), leyendo el ajuste en cada uso
    (así las pruebas pueden usar una carpeta temporal).
    No está dentro de ninguna carpeta pública ni tiene dirección web: los archivos solo se
    entregan a través de un endpoint que exige sesión y permisos (ETAPA 6 en adelante).
    """

    @property
    def base_location(self):
        return str(settings.PRIVATE_MEDIA_ROOT)

    @property
    def location(self):
        return os.path.abspath(self.base_location)


def almacenamiento_privado():
    return AlmacenamientoPrivado()
