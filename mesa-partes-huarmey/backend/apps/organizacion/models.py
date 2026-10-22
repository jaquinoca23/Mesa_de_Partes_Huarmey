from django.db import models
from django.db.models import F, Q


class Area(models.Model):
    """
    Dependencia de la municipalidad (gerencia, oficina, etc.), organizada en jerarquía.

    IMPORTANTE: la estructura real depende del ROF vigente de la Municipalidad
    Provincial de Huarmey, que todavía no ha sido verificado. Por eso los datos de
    prueba se marcan con es_ficticia=True y los tipos son configurables.
    """

    class TipoArea(models.TextChoices):
        MUNICIPALIDAD = 'MUNICIPALIDAD', 'Municipalidad'
        ORGANO = 'ORGANO', 'Órgano'
        GERENCIA = 'GERENCIA', 'Gerencia'
        SUBGERENCIA = 'SUBGERENCIA', 'Subgerencia'
        OFICINA = 'OFICINA', 'Oficina'
        UNIDAD = 'UNIDAD', 'Unidad'
        OTRO = 'OTRO', 'Otra dependencia'

    nombre = models.CharField(max_length=200, unique=True)
    siglas = models.CharField(max_length=20, blank=True)
    tipo = models.CharField(max_length=20, choices=TipoArea.choices)
    # Área de la que depende. Vacío = nivel más alto. PROTECT impide borrar un área
    # que todavía tiene áreas dependientes.
    padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='dependencias',
    )
    activo = models.BooleanField(default=True)
    es_ficticia = models.BooleanField(
        default=True,
        help_text='Dato de prueba. Desmarcar solo cuando el área esté confirmada por el ROF vigente.',
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'área'
        verbose_name_plural = 'áreas'
        constraints = [
            # Un área no puede depender de sí misma.
            models.CheckConstraint(
                condition=~Q(padre=F('id')),
                name='area_no_es_su_propio_padre',
            ),
        ]

    def __str__(self):
        return self.nombre
