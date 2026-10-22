from rest_framework import serializers, viewsets

from apps.core.mixins import AuditaCambiosMixin
from apps.core.permisos import PermisosModelo

from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True, default='')

    class Meta:
        model = Area
        fields = ['id', 'nombre', 'siglas', 'tipo', 'padre', 'padre_nombre', 'activo', 'es_ficticia']

    def validate_padre(self, padre):
        # Evita ciclos: un área no puede depender de sí misma ni de una de sus propias dependencias.
        if padre and self.instance:
            actual = padre
            visitadas = set()
            while actual is not None and actual.pk not in visitadas:
                if actual.pk == self.instance.pk:
                    raise serializers.ValidationError('Un área no puede depender de sí misma ni de una de sus dependencias.')
                visitadas.add(actual.pk)
                actual = actual.padre
        return padre


class AreaViewSet(AuditaCambiosMixin, viewsets.ModelViewSet):
    """/api/panel/areas/ — organigrama provisional (se edita con permisos; no se elimina)."""

    serializer_class = AreaSerializer
    permission_classes = [PermisosModelo]
    queryset = Area.objects.select_related('padre').order_by('nombre')
    pagination_class = None
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
