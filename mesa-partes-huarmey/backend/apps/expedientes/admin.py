from django.contrib import admin

from .models import Expediente, HistorialEstado, Solicitante


class SoloLecturaAdmin(admin.ModelAdmin):
    """Muestra los datos sin permitir crear, editar ni borrar desde el administrador."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    can_delete = False
    fields = ('fecha', 'estado_anterior', 'estado_nuevo', 'usuario', 'observacion')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expediente)
class ExpedienteAdmin(SoloLecturaAdmin):
    list_display = ('numero', 'asunto', 'tipo_documental', 'estado_actual', 'solicitante', 'fecha_recepcion')
    list_filter = ('estado_actual', 'tipo_documental')
    search_fields = ('numero', 'asunto')
    inlines = [HistorialInline]


@admin.register(Solicitante)
class SolicitanteAdmin(SoloLecturaAdmin):
    list_display = ('nombre_para_mostrar', 'tipo_persona', 'tipo_documento_identidad', 'numero_documento', 'email')
    list_filter = ('tipo_persona',)
    search_fields = ('numero_documento', 'nombres', 'apellidos', 'razon_social', 'email')
