from rest_framework import serializers, viewsets

from apps.core.mixins import AuditaCambiosMixin
from apps.core.permisos import PermisosModelo

from .models import EstadoExpediente, TipoDocumental


class TipoDocumentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumental
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'es_procedimiento_tupa', 'es_provisional', 'activo', 'orden']


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoExpediente
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'es_inicial', 'es_final', 'es_provisional', 'activo', 'orden']

    def validate(self, datos):
        # Solo puede haber UN estado inicial (la base de datos también lo garantiza).
        if datos.get('es_inicial'):
            otros = EstadoExpediente.objects.filter(es_inicial=True)
            if self.instance:
                otros = otros.exclude(pk=self.instance.pk)
            if otros.exists():
                raise serializers.ValidationError({'es_inicial': 'Ya existe otro estado inicial.'})
        return datos


class _CatalogoViewSet(AuditaCambiosMixin, viewsets.ModelViewSet):
    permission_classes = [PermisosModelo]
    pagination_class = None
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']  # sin eliminar


class TipoDocumentalViewSet(_CatalogoViewSet):
    serializer_class = TipoDocumentalSerializer
    queryset = TipoDocumental.objects.all()


class EstadoViewSet(_CatalogoViewSet):
    serializer_class = EstadoSerializer
    queryset = EstadoExpediente.objects.all()
