from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar


class AuditaCambiosMixin:
    """Para ModelViewSet: deja registro de auditoría cada vez que se crea o modifica algo."""

    accion_creacion = RegistroAuditoria.Accion.CATALOGO_CREADO
    accion_modificacion = RegistroAuditoria.Accion.CATALOGO_MODIFICADO

    def perform_create(self, serializer):
        objeto = serializer.save()
        registrar(self.request, self.accion_creacion, objeto)

    def perform_update(self, serializer):
        objeto = serializer.save()
        registrar(self.request, self.accion_modificacion, objeto)
