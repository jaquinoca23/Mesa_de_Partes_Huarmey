from django.db import models
from django.db.models import Q


class TipoDocumental(models.Model):
    """
    Categoría de documento que presenta el ciudadano (Solicitud, Oficio, etc.).

    Los valores iniciales son PROPUESTAS DE PRUEBA, no una lista oficial de la
    Municipalidad Provincial de Huarmey. Por eso es_provisional vale True por defecto.
    """

    codigo = models.SlugField(max_length=60, unique=True, help_text='Identificador interno, sin espacios.')
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    # No todos los tipos corresponden a procedimientos del TUPA; este campo permite distinguirlos.
    es_procedimiento_tupa = models.BooleanField(
        default=False,
        help_text='Marcar solo si corresponde a un procedimiento del TUPA vigente (por validar).',
    )
    es_provisional = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'tipo documental'
        verbose_name_plural = 'tipos documentales'

    def __str__(self):
        return self.nombre


class EstadoExpediente(models.Model):
    """
    Estado en el que puede estar un expediente (Recibido, En atención, etc.).

    Los estados iniciales son PROVISIONALES: no son reglas oficiales hasta validar el
    procedimiento documentario vigente de la municipalidad.
    """

    codigo = models.SlugField(max_length=60, unique=True)
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True, help_text='Qué significa este estado.')
    # Estado con el que nace todo expediente nuevo. Solo puede haber uno.
    es_inicial = models.BooleanField(default=False)
    # Estado que cierra el trámite (Atendido, Archivado).
    es_final = models.BooleanField(default=False)
    es_provisional = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'estado de expediente'
        verbose_name_plural = 'estados de expediente'
        constraints = [
            # La base de datos garantiza que exista como máximo un estado inicial.
            models.UniqueConstraint(
                fields=['es_inicial'],
                condition=Q(es_inicial=True),
                name='un_solo_estado_inicial',
            ),
        ]

    def __str__(self):
        return self.nombre
