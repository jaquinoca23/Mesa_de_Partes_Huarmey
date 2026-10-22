from django.urls import path

from . import views

urlpatterns = [
    # GET /api/health/
    path('health/', views.health, name='health'),
]
