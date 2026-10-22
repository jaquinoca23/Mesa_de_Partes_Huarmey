from django.db import models
from django.utils import timezone


class Notificacion(models.Model):
    """
    Registro de cada correo que el sistema intenta enviar. Se guarda el asunto y el resultado,
    pero NO el cuerpo del mensaje (puede incluir el código de verificación del ciudadano).
    """

    class Tipo(models.TextChoices):
        CARGO = 'CARGO', 'Cargo de recepción'
        CAMBIO_ESTADO = 'CAMBIO_ESTADO', 'Cambio de estado'

    class Estado(models.TextChoices):
        ENVIADA = 'ENVIADA', 'Enviada'
        FALLIDA = 'FALLIDA', 'Fallida'

    expediente = models.ForeignKey(
        'expedientes.Expediente',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='notificaciones',
    )
    destinatario = models.EmailField(blank=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    asunto = models.CharField(max_length=200)
    estado = models.CharField(max_length=10, choices=Estado.choices)
    error = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'notificación'
        verbose_name_plural = 'notificaciones'

    def __str__(self):
        return f'{self.tipo} -> {self.estado}'
