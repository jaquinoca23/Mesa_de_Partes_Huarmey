from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoloAgregarMixin


class RegistroAuditoria(SoloAgregarMixin):
    """
    Bitácora de acciones relevantes. Solo se agrega: no se modifica ni se elimina.
    IMPORTANTE: el campo "detalle" NO debe contener datos personales ni contraseñas.
    """

    class Accion(models.TextChoices):
        LOGIN = 'LOGIN', 'Inicio de sesión'
        LOGIN_FALLIDO = 'LOGIN_FALLIDO', 'Intento de inicio de sesión fallido'
        LOGOUT = 'LOGOUT', 'Cierre de sesión'
        EXPEDIENTE_REGISTRADO = 'EXPEDIENTE_REGISTRADO', 'Expediente registrado'
        ESTADO_CAMBIADO = 'ESTADO_CAMBIADO', 'Estado cambiado'
        DERIVACION_CREADA = 'DERIVACION_CREADA', 'Derivación creada'
        DERIVACION_RECIBIDA = 'DERIVACION_RECIBIDA', 'Derivación recibida'
        ACTUACION_REGISTRADA = 'ACTUACION_REGISTRADA', 'Actuación registrada'
        ADJUNTO_DESCARGADO = 'ADJUNTO_DESCARGADO', 'Adjunto descargado'
        USUARIO_CREADO = 'USUARIO_CREADO', 'Usuario creado'
        USUARIO_MODIFICADO = 'USUARIO_MODIFICADO', 'Usuario modificado'
        CATALOGO_CREADO = 'CATALOGO_CREADO', 'Registro de catálogo creado'
        CATALOGO_MODIFICADO = 'CATALOGO_MODIFICADO', 'Registro de catálogo modificado'
        REPORTE_EXPORTADO = 'REPORTE_EXPORTADO', 'Reporte exportado'

    fecha = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Vacío cuando la acción la hace un ciudadano o el sistema.',
    )
    accion = models.CharField(max_length=40, choices=Accion.choices)
    objeto_tipo = models.CharField(max_length=60, blank=True)
    objeto_id = models.CharField(max_length=40, blank=True)
    detalle = models.CharField(max_length=300, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'
        indexes = [models.Index(fields=['accion', '-fecha'], name='aud_accion_fecha_idx')]

    def __str__(self):
        return f'{self.fecha:%Y-%m-%d %H:%M} {self.accion}'
