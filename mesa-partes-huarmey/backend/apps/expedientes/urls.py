from django.urls import path

from . import views

urlpatterns = [
    # POST /api/solicitudes/  (registra la solicitud y devuelve el cargo)
    path('', views.RegistrarSolicitudView.as_view(), name='solicitudes-registrar'),
    # GET /api/solicitudes/configuracion/
    path('configuracion/', views.configuracion, name='solicitudes-configuracion'),
    # POST /api/solicitudes/validar/  (solo verifica, no guarda)
    path('validar/', views.ValidarSolicitudView.as_view(), name='solicitudes-validar'),
]
