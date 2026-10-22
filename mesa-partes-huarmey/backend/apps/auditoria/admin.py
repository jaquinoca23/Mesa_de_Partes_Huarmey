from django.contrib import admin

from .models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    """Solo lectura: la auditoría no se edita desde ningún lugar."""

    list_display = ('fecha', 'accion', 'usuario', 'objeto_tipo', 'objeto_id', 'detalle')
    list_filter = ('accion',)
    search_fields = ('detalle', 'objeto_id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
