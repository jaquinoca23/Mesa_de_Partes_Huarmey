from django.urls import path

from . import views

urlpatterns = [
    # GET /api/catalogos/tipos-documentales/
    path('tipos-documentales/', views.tipos_documentales, name='tipos-documentales'),
]
