from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.core.roles import ROLES

from .models import Usuario

ROL_ADMIN = 'Administrador'


class UsuarioSerializer(serializers.ModelSerializer):
    """Personal municipal. La contraseña solo se escribe: nunca se devuelve."""

    roles = serializers.SlugRelatedField(
        source='groups',
        many=True,
        slug_field='name',
        queryset=Group.objects.filter(name__in=list(ROLES)),
        required=False,
    )
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default='')
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, trim_whitespace=False)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'cargo',
            'area', 'area_nombre', 'is_active', 'roles', 'password', 'last_login',
        ]
        read_only_fields = ['last_login']

    def _es_admin(self):
        usuario = self.context['request'].user
        return usuario.is_superuser or usuario.groups.filter(name=ROL_ADMIN).exists()

    def validate_roles(self, grupos):
        # Solo un administrador puede dar (o quitar) el rol de administrador: evita escalar privilegios.
        if not self._es_admin() and any(g.name == ROL_ADMIN for g in grupos):
            raise serializers.ValidationError('No puedes asignar el rol de Administrador.')
        if self.instance and not self._es_admin():
            era_admin = self.instance.groups.filter(name=ROL_ADMIN).exists()
            if era_admin:
                raise serializers.ValidationError('No puedes modificar los roles de un Administrador.')
        return grupos

    def validate_is_active(self, valor):
        solicitante = self.context['request'].user
        if self.instance and self.instance.pk == solicitante.pk and not valor:
            raise serializers.ValidationError('No puedes desactivar tu propio usuario.')
        return valor

    def validate_email(self, valor):
        if not valor:
            raise serializers.ValidationError('Este campo es obligatorio.')
        return valor

    def validate(self, datos):
        password = datos.get('password')
        if not self.instance and not password:
            raise serializers.ValidationError({'password': 'La contraseña es obligatoria al crear un usuario.'})
        if password:
            candidato = self.instance or Usuario(
                username=datos.get('username', ''),
                first_name=datos.get('first_name', ''),
                last_name=datos.get('last_name', ''),
                email=datos.get('email', ''),
            )
            try:
                validate_password(password, candidato)
            except Exception as error:  # noqa: BLE001 - ValidationError de Django -> mensajes de DRF
                raise serializers.ValidationError({'password': list(getattr(error, 'messages', [str(error)]))})
        return datos

    def create(self, datos):
        grupos = datos.pop('groups', [])
        password = datos.pop('password')
        usuario = Usuario(**datos)
        usuario.set_password(password)
        usuario.save()
        usuario.groups.set(grupos)
        return usuario

    def update(self, instancia, datos):
        grupos = datos.pop('groups', None)
        password = datos.pop('password', '')
        for campo, valor in datos.items():
            setattr(instancia, campo, valor)
        if password:
            instancia.set_password(password)
        instancia.save()
        if grupos is not None:
            instancia.groups.set(grupos)
        return instancia
