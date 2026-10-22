from django.urls import path

from . import views_seguimiento

urlpatterns = [
    # POST /api/seguimiento/consultar/
    path('consultar/', views_seguimiento.ConsultarExpedienteView.as_view(), name='seguimiento-consultar'),
]
