from django.contrib import admin

from .models import Area


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'padre', 'activo', 'es_ficticia')
    list_filter = ('tipo', 'activo', 'es_ficticia')
    search_fields = ('nombre', 'siglas')
