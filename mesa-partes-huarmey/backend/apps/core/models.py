from django.core.exceptions import ValidationError
from django.db import models


class SoloAgregarMixin(models.Model):
    """
    Base para registros que solo se pueden AGREGAR: una vez guardados no se modifican
    ni se eliminan (historiales, actuaciones, auditoría). Así se conserva la trazabilidad.

    Es una clase "abstracta": no crea ninguna tabla por sí sola.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('Este registro no se puede modificar.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Este registro no se puede eliminar.')
