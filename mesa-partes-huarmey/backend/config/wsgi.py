"""Punto de entrada WSGI (lo usarán los servidores de producción más adelante)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
