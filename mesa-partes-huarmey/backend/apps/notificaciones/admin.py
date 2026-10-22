from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Solo lectura."""

    list_display = ('fecha', 'tipo', 'estado', 'expediente', 'asunto')
    list_filter = ('tipo', 'estado')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
