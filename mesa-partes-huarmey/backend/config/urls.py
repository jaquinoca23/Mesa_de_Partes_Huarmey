"""Rutas principales del backend."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Todas las rutas de la API empiezan con /api/
    path('api/', include('apps.core.urls')),
    path('api/catalogos/', include('apps.catalogos.urls')),
    path('api/solicitudes/', include('apps.expedientes.urls')),
    path('api/auth/', include('apps.usuarios.urls_auth')),
    path('api/panel/', include('config.urls_panel')),
    path('api/identidad/', include('apps.identidad.urls')),
    path('api/seguimiento/', include('apps.expedientes.urls_seguimiento')),
]
