import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .almacenamiento import almacenamiento_privado


def ruta_adjunto(instancia, nombre):
    """
    Ruta de almacenamiento: adjuntos/AAAA/MM/<identificador-aleatorio>.<extensión>
    El nombre original del ciudadano NUNCA se usa como nombre de archivo en el disco.
    """
    extension = nombre.rsplit('.', 1)[-1].lower() if '.' in nombre else 'bin'
    return f'adjuntos/{timezone.now():%Y/%m}/{uuid.uuid4().hex}.{extension}'


class Adjunto(models.Model):
    """Archivo adjunto a un expediente. El contenido va a disco (carpeta privada), no a la base de datos."""

    expediente = models.ForeignKey('expedientes.Expediente', on_delete=models.PROTECT, related_name='adjuntos')
    archivo = models.FileField(upload_to=ruta_adjunto, storage=almacenamiento_privado, max_length=200)
    nombre_original = models.CharField(max_length=150)
    es_principal = models.BooleanField(default=False)
    extension = models.CharField(max_length=10)
    tamano = models.PositiveIntegerField(help_text='Tamaño en bytes.')
    sha256 = models.CharField(max_length=64, help_text='Huella del contenido, para verificar que no cambió.')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'adjunto'
        verbose_name_plural = 'adjuntos'

    def __str__(self):
        return self.nombre_original

    def delete(self, *args, **kwargs):
        raise ValidationError('Los adjuntos no se pueden eliminar.')
