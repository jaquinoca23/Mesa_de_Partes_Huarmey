from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario
from .politica import es_administrador_unico


admin.site.has_permission = lambda request: es_administrador_unico(request.user) and request.user.is_staff


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    def has_add_permission(self, request):
        return False  # Las altas se realizan desde el panel, con DNI y validación de roles.

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = UserAdmin.fieldsets + (('Datos municipales', {'fields': ('area', 'cargo')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Datos municipales', {'fields': ('area', 'cargo')}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'area', 'is_staff')
    list_filter = UserAdmin.list_filter + ('area',)
