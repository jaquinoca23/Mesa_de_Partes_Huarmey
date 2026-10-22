from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Personal municipal que usará el panel administrativo.

    Se define ahora (aunque el inicio de sesión se construye en la ETAPA 6) porque
    Django exige elegir el modelo de usuario ANTES de crear las tablas por primera
    vez; cambiarlo después es muy difícil.

    Hereda de AbstractUser: contraseña con hash seguro, permisos y grupos de Django.
    Los roles y permisos propios se diseñarán en la ETAPA 6.
    """

    area = models.ForeignKey(
        'organizacion.Area',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='usuarios',
        help_text='Área a la que pertenece el usuario.',
    )
    cargo = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.get_full_name() or self.username
