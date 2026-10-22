from django.urls import path

from . import views_auth

urlpatterns = [
    path('csrf/', views_auth.CsrfView.as_view(), name='auth-csrf'),
    path('login/', views_auth.LoginView.as_view(), name='auth-login'),
    path('logout/', views_auth.LogoutView.as_view(), name='auth-logout'),
    path('me/', views_auth.SesionView.as_view(), name='auth-me'),
]
