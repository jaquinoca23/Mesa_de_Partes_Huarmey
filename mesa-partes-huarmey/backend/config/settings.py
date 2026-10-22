"""
Configuración de Django para Mesa de Partes Digital (Municipalidad Provincial de Huarmey).

Los valores sensibles o que cambian según el entorno se leen del archivo ".env"
(variables de entorno). Nunca se escriben secretos en este archivo.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# backend/ (la carpeta donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del archivo backend/.env (si existe).
load_dotenv(BASE_DIR / '.env')


def env_list(name, default=''):
    """Convierte 'a,b,c' en ['a', 'b', 'c'] ignorando espacios y vacíos."""
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


# ---------------------------------------------------------------------------
# Seguridad básica
# ---------------------------------------------------------------------------
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Falta DJANGO_SECRET_KEY. Copia backend/.env.example como backend/.env "
        "y vuelve a intentarlo."
    )
if not DEBUG and SECRET_KEY.startswith('dev-only'):
    raise ImproperlyConfigured(
        "Con DJANGO_DEBUG=False debes usar una DJANGO_SECRET_KEY propia y secreta."
    )

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')

# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    'corsheaders',
    # Propias
    'apps.core',
    'apps.organizacion',
    'apps.usuarios',
    'apps.catalogos',
    'apps.expedientes',
    'apps.documentos',
    'apps.derivaciones',
    'apps.auditoria',
    'apps.notificaciones',
    'apps.identidad',
]

# Modelo de usuario propio (personal municipal). Debe definirse antes de la primera migración.
AUTH_USER_MODEL = 'usuarios.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # debe ir antes de CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
# PostgreSQL es la base de datos objetivo (DB_ENGINE=postgresql en el archivo .env).
# SQLite queda solo como alternativa temporal de emergencia para pruebas rápidas.
DB_ENGINE = os.getenv('DB_ENGINE', 'postgresql').lower()

if DB_ENGINE == 'postgresql':
    if not os.getenv('DB_PASSWORD'):
        raise ImproperlyConfigured(
            "Falta DB_PASSWORD en backend/.env (contraseña del usuario de PostgreSQL)."
        )
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'mesa_partes_huarmey'),
            'USER': os.getenv('DB_USER', 'mesa_partes_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
elif DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured("DB_ENGINE debe ser 'postgresql' o 'sqlite'.")

# ---------------------------------------------------------------------------
# Validación de contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Idioma y zona horaria
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True  # las fechas se guardan en UTC y se muestran en hora de Lima

# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # La API responde solo en JSON.
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    # Por seguridad, todo endpoint exige sesión iniciada salvo que se indique lo
    # contrario. /api/health/ es público de forma explícita.
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    # El panel usa sesión (cookie) + protección CSRF. Los endpoints públicos la desactivan a propósito.
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    # Límite básico contra abuso de usuarios anónimos.
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'],
    # 'solicitudes' limita los intentos de envío del formulario público (por dirección IP).
    # 'consulta' limita los intentos de la consulta pública (evita adivinar códigos por fuerza bruta).
    'DEFAULT_THROTTLE_RATES': {'anon': '120/minute', 'solicitudes': '30/hour', 'consulta': '30/hour', 'login': '10/minute', 'identidad': '20/hour'},
}

# ---------------------------------------------------------------------------
# CORS: qué sitios web pueden llamar a la API desde el navegador
# ---------------------------------------------------------------------------
# Lista restrictiva: solo el frontend local de desarrollo (configurable en .env).
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
)

# ---------------------------------------------------------------------------
# Archivos adjuntos del formulario ciudadano (límites configurables en .env)
# ---------------------------------------------------------------------------
# Valores PROVISIONALES: los tipos y tamaños definitivos los debe aprobar la municipalidad.
def env_numero(name, default):
    """Lee un número desde .env; si no es un número válido, avisa con un mensaje claro."""
    try:
        return float(os.getenv(name, default))
    except ValueError:
        raise ImproperlyConfigured(f"{name} debe ser un número.")


UPLOAD_MAX_FILES = int(env_numero('UPLOAD_MAX_FILES', 5))
UPLOAD_MAX_FILE_SIZE_MB = env_numero('UPLOAD_MAX_FILE_SIZE_MB', 10)
UPLOAD_ALLOWED_EXTENSIONS = [
    e.lower().lstrip('.') for e in env_list('UPLOAD_ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,docx')
]

# Máximo de campos de archivo por petición (un poco más que UPLOAD_MAX_FILES; el validador pone el límite real).
DATA_UPLOAD_MAX_NUMBER_FILES = UPLOAD_MAX_FILES + 5

# ---------------------------------------------------------------------------
# Almacenamiento PRIVADO de adjuntos (fuera de cualquier carpeta pública)
# ---------------------------------------------------------------------------
PRIVATE_MEDIA_ROOT = Path(os.getenv('PRIVATE_MEDIA_ROOT', str(BASE_DIR / 'storage_privado')))

# ---------------------------------------------------------------------------
# Correo (notificaciones). En desarrollo el correo se IMPRIME en la terminal de Django.
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(env_numero('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'mesa-partes-demo@example.com')

# ---------------------------------------------------------------------------
# Cabeceras de seguridad básicas
# ---------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ---------------------------------------------------------------------------
# Sesión y CSRF (inicio de sesión del personal, ETAPA 6)
# ---------------------------------------------------------------------------
# El frontend de desarrollo (Vite) llama a la API desde otro "origen": hay que autorizarlo también para CSRF.
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SESSION_COOKIE_HTTPONLY = True          # JavaScript no puede leer la cookie de sesión
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # la sesión termina al cerrar el navegador
SESSION_COOKIE_AGE = int(env_numero('SESSION_HORAS', 8) * 3600)  # y caduca sola tras N horas

# DJANGO_HTTPS=True solo cuando el sitio se publique con HTTPS (certificado instalado).
DJANGO_HTTPS = os.getenv('DJANGO_HTTPS', 'False').lower() == 'true'
if DJANGO_HTTPS:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600  # súbelo gradualmente cuando todo funcione (p. ej. 31536000)

# ---------------------------------------------------------------------------
# Verificación de DNI (servicio externo; ver apps/identidad). Sin token, la función queda desactivada.
# ---------------------------------------------------------------------------
IDENTIDAD_API_URL = os.getenv('IDENTIDAD_API_URL', 'https://dniruc.apisperu.com/api/v1/dni')
IDENTIDAD_API_TOKEN = os.getenv('IDENTIDAD_API_TOKEN', '')
IDENTIDAD_TIMEOUT = env_numero('IDENTIDAD_TIMEOUT', 8)
