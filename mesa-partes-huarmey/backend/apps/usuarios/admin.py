from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Datos municipales', {'fields': ('area', 'cargo')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Datos municipales', {'fields': ('area', 'cargo')}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'area', 'is_staff')
    list_filter = UserAdmin.list_filter + ('area',)
