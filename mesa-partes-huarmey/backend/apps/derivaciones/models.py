from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import SoloAgregarMixin


class Derivacion(models.Model):
    """
    Envío de un expediente de un área a otra.

    Mientras está PENDIENTE, el expediente sigue en el área de origen. Cuando el área destino
    confirma la recepción, el expediente pasa a ser suyo. Nunca se borra: queda como historial.
    """

    class EstadoRecepcion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de recepción'
        RECIBIDA = 'RECIBIDA', 'Recibida'

    expediente = models.ForeignKey('expedientes.Expediente', on_delete=models.PROTECT, related_name='derivaciones')
    area_origen = models.ForeignKey(
        'organizacion.Area', null=True, blank=True, on_delete=models.PROTECT, related_name='derivaciones_enviadas'
    )
    area_destino = models.ForeignKey('organizacion.Area', on_delete=models.PROTECT, related_name='derivaciones_recibidas')
    usuario_remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    usuario_receptor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Opcional: si se indica, solo esa persona puede recibir la derivación.',
    )
    motivo = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True)
    estado_recepcion = models.CharField(
        max_length=10, choices=EstadoRecepcion.choices, default=EstadoRecepcion.PENDIENTE
    )
    fecha = models.DateTimeField(default=timezone.now, editable=False)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    recibido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='+'
    )

    class Meta:
        ordering = ['fecha', 'id']
        verbose_name = 'derivación'
        verbose_name_plural = 'derivaciones'
        indexes = [models.Index(fields=['area_destino', 'estado_recepcion'], name='der_destino_estado_idx')]
        constraints = [
            # La base de datos impide tener dos derivaciones pendientes del mismo expediente.
            models.UniqueConstraint(
                fields=['expediente'],
                condition=Q(estado_recepcion='PENDIENTE'),
                name='una_derivacion_pendiente_por_expediente',
            ),
        ]

    def __str__(self):
        return f'{self.expediente_id} -> {self.area_destino_id} ({self.estado_recepcion})'


class Actuacion(SoloAgregarMixin):
    """Observación o actuación registrada por el personal sobre un expediente. Solo se agrega."""

    class Tipo(models.TextChoices):
        OBSERVACION = 'OBSERVACION', 'Observación'
        ACTUACION = 'ACTUACION', 'Actuación'

    expediente = models.ForeignKey('expedientes.Expediente', on_delete=models.PROTECT, related_name='actuaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['fecha', 'id']
        verbose_name = 'actuación'
        verbose_name_plural = 'actuaciones'

    def __str__(self):
        return f'{self.tipo} del expediente {self.expediente_id}'
