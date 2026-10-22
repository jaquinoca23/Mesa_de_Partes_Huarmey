import secrets
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

# Letras y números sin caracteres confusos (sin 0/O, 1/I/L) para el código de verificación.
ALFABETO_CODIGO = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


def generar_codigo_verificacion(longitud=8):
    """Código aleatorio criptográficamente seguro que el ciudadano usará para consultar."""
    return ''.join(secrets.choice(ALFABETO_CODIGO) for _ in range(longitud))


def formatear_numero(anio, correlativo):
    """
    Formato PROVISIONAL del número de expediente: AAAA-NNNNNN (ej. 2026-000001).
    La regla oficial de numeración debe ser validada con la municipalidad.
    """
    return f'{anio}-{correlativo:06d}'


class SecuenciaExpediente(models.Model):
    """
    Contador de números de expediente, uno por año.
    Se incrementa bloqueando la fila (select_for_update) para que dos solicitudes
    simultáneas jamás reciban el mismo número.
    """

    anio = models.PositiveSmallIntegerField(unique=True)
    ultimo_numero = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'secuencia de expedientes'
        verbose_name_plural = 'secuencias de expedientes'

    def __str__(self):
        return f'{self.anio}: {self.ultimo_numero}'


def siguiente_numero(anio):
    """Devuelve el siguiente correlativo del año, sin duplicados."""
    with transaction.atomic():
        secuencia, _ = SecuenciaExpediente.objects.select_for_update().get_or_create(anio=anio)
        secuencia.ultimo_numero += 1
        secuencia.save(update_fields=['ultimo_numero'])
        return secuencia.ultimo_numero


class Solicitante(models.Model):
    """
    Persona natural o jurídica que presenta un documento.
    Los tipos de documento de identidad son PROVISIONALES (por validar con la municipalidad).
    En desarrollo solo se usan datos ficticios.
    """

    class TipoPersona(models.TextChoices):
        NATURAL = 'NATURAL', 'Persona natural'
        JURIDICA = 'JURIDICA', 'Persona jurídica'

    class TipoDocumentoIdentidad(models.TextChoices):
        DNI = 'DNI', 'DNI'
        CE = 'CE', 'Carné de extranjería'
        PASAPORTE = 'PASAPORTE', 'Pasaporte'
        RUC = 'RUC', 'RUC'

    tipo_persona = models.CharField(max_length=10, choices=TipoPersona.choices)
    tipo_documento_identidad = models.CharField(max_length=10, choices=TipoDocumentoIdentidad.choices)
    numero_documento = models.CharField(max_length=20)
    nombres = models.CharField(max_length=150, blank=True, help_text='Obligatorio para persona natural.')
    apellidos = models.CharField(max_length=150, blank=True)
    razon_social = models.CharField(max_length=200, blank=True, help_text='Obligatorio para persona jurídica.')
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'solicitante'
        verbose_name_plural = 'solicitantes'
        constraints = [
            # Regla anti-duplicados: un mismo documento de identidad = un solo solicitante.
            models.UniqueConstraint(
                fields=['tipo_documento_identidad', 'numero_documento'],
                name='solicitante_documento_unico',
            ),
            # Persona natural exige nombres; persona jurídica exige razón social.
            models.CheckConstraint(
                condition=(
                    (Q(tipo_persona='NATURAL') & ~Q(nombres=''))
                    | (Q(tipo_persona='JURIDICA') & ~Q(razon_social=''))
                ),
                name='solicitante_nombre_segun_tipo',
            ),
        ]

    @property
    def nombre_para_mostrar(self):
        if self.tipo_persona == self.TipoPersona.JURIDICA:
            return self.razon_social
        return f'{self.nombres} {self.apellidos}'.strip()

    def __str__(self):
        return self.nombre_para_mostrar


class Expediente(models.Model):
    """
    Documento presentado por un ciudadano y su seguimiento.

    - 'numero' lo asigna SIEMPRE el servidor (nunca el usuario).
    - 'uuid' es el identificador que se usará en direcciones web: no es secuencial,
      por lo que no se puede adivinar el expediente de otra persona.
    - 'codigo_verificacion' es el segundo dato que el ciudadano necesita para consultar.
    - Nada se borra: las relaciones usan PROTECT y los cambios de estado quedan en el historial.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    numero = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    codigo_verificacion = models.CharField(
        max_length=12, editable=False, default=generar_codigo_verificacion
    )
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT, related_name='expedientes')
    tipo_documental = models.ForeignKey(
        'catalogos.TipoDocumental', on_delete=models.PROTECT, related_name='expedientes'
    )
    estado_actual = models.ForeignKey(
        'catalogos.EstadoExpediente', on_delete=models.PROTECT, related_name='expedientes'
    )
    asunto = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    # Guardada con zona horaria (se almacena en UTC; se muestra en hora de Lima).
    # Hora provisional del servidor hasta validar la regla oficial de hora de recepción.
    fecha_recepcion = models.DateTimeField(default=timezone.now, editable=False)
    # Identifica el envío del formulario. Es única: si el mismo envío llega dos veces
    # (doble clic, reintento por mala conexión) NO se crea un segundo expediente.
    clave_envio = models.UUIDField(null=True, blank=True, unique=True, editable=False)
    # Datos de contacto con los que se presentó ESTA solicitud (para notificarle).
    email_contacto = models.EmailField(blank=True, default='', editable=False)
    telefono_contacto = models.CharField(max_length=20, blank=True, default='', editable=False)
    # Área que tiene el expediente en este momento (cambia cuando se recibe una derivación).
    area_actual = models.ForeignKey(
        'organizacion.Area',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='expedientes_actuales',
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_recepcion']
        verbose_name = 'expediente'
        verbose_name_plural = 'expedientes'
        # Permisos propios del panel administrativo (se asignan mediante roles).
        permissions = [
            ('ver_todos_expedientes', 'Puede ver los expedientes de todas las áreas'),
            ('cambiar_estado_expediente', 'Puede cambiar el estado de un expediente'),
            ('derivar_expediente', 'Puede derivar expedientes a otra área'),
            ('registrar_actuacion', 'Puede registrar observaciones y actuaciones'),
            ('ver_reportes', 'Puede ver y exportar reportes'),
        ]
        indexes = [
            models.Index(fields=['estado_actual', '-fecha_recepcion'], name='exp_estado_fecha_idx'),
            models.Index(fields=['fecha_recepcion'], name='exp_fecha_idx'),
        ]
        constraints = [
            models.CheckConstraint(condition=~Q(asunto=''), name='expediente_asunto_no_vacio'),
        ]

    def __str__(self):
        return f'{self.numero} - {self.asunto[:50]}'

    def save(self, *args, **kwargs):
        # Un solo bloque atómico: si el guardado falla, el número tampoco se consume.
        with transaction.atomic():
            if not self.numero:
                anio = timezone.localtime(self.fecha_recepcion).year
                self.numero = formatear_numero(anio, siguiente_numero(anio))
            super().save(*args, **kwargs)

    def cambiar_estado(self, nuevo_estado, usuario=None, observacion=''):
        """
        Cambia el estado y deja registro en el historial (el historial anterior se conserva).
        Devuelve el registro de historial creado.
        """
        if nuevo_estado.pk == self.estado_actual_id:
            raise ValueError('El expediente ya se encuentra en ese estado.')
        with transaction.atomic():
            estado_anterior = self.estado_actual
            self.estado_actual = nuevo_estado
            self.save(update_fields=['estado_actual', 'actualizado'])
            return HistorialEstado.objects.create(
                expediente=self,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario=usuario,
                observacion=observacion,
            )


class HistorialEstado(models.Model):
    """
    Registro de cada cambio de estado de un expediente. Solo se agrega: no se modifica
    ni se elimina, para conservar la trazabilidad.
    """

    expediente = models.ForeignKey(Expediente, on_delete=models.PROTECT, related_name='historial')
    estado_anterior = models.ForeignKey(
        'catalogos.EstadoExpediente',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Vacío en el primer registro del expediente.',
    )
    estado_nuevo = models.ForeignKey(
        'catalogos.EstadoExpediente', on_delete=models.PROTECT, related_name='+'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Vacío cuando el cambio lo hace el sistema (por ejemplo, al recibir la solicitud).',
    )
    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['fecha', 'id']
        verbose_name = 'historial de estado'
        verbose_name_plural = 'historial de estados'
        indexes = [models.Index(fields=['expediente', 'fecha'], name='hist_exp_fecha_idx')]

    def __str__(self):
        return f'{self.expediente.numero}: {self.estado_nuevo}'

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('El historial de estados no se puede modificar.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('El historial de estados no se puede eliminar.')
