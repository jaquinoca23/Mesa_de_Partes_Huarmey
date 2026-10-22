from django.contrib import admin

from .models import Actuacion, Derivacion


class SoloLectura(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Derivacion)
class DerivacionAdmin(SoloLectura):
    list_display = ('expediente', 'area_origen', 'area_destino', 'estado_recepcion', 'fecha')
    list_filter = ('estado_recepcion',)


@admin.register(Actuacion)
class ActuacionAdmin(SoloLectura):
    list_display = ('expediente', 'tipo', 'usuario', 'fecha')
    list_filter = ('tipo',)
