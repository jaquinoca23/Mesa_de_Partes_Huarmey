from django.contrib import admin

from .models import EstadoExpediente, TipoDocumental


@admin.register(TipoDocumental)
class TipoDocumentalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'es_procedimiento_tupa', 'es_provisional', 'activo', 'orden')
    list_filter = ('activo', 'es_provisional', 'es_procedimiento_tupa')
    search_fields = ('nombre', 'codigo')


@admin.register(EstadoExpediente)
class EstadoExpedienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'es_inicial', 'es_final', 'es_provisional', 'activo', 'orden')
    list_filter = ('activo', 'es_provisional', 'es_final')
    search_fields = ('nombre', 'codigo')
