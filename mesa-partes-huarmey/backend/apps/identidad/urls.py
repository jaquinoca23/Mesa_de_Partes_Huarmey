from django.urls import path

from . import views

urlpatterns = [
    path('dni/<str:dni>/', views.ConsultarDniView.as_view(), name='identidad-dni'),
]
