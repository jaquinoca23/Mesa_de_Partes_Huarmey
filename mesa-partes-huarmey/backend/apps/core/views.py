from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

API_VERSION = '0.1.0'


@api_view(['GET'])
@permission_classes([AllowAny])  # público a propósito: solo confirma que el servidor responde
def health(request):
    """
    Comprobación de estado del backend.
    No expone datos internos (rutas, configuración, usuarios ni base de datos).
    """
    return Response(
        {
            'status': 'ok',
            'service': 'mesa-partes-huarmey-api',
            'version': API_VERSION,
            'server_time': timezone.now().isoformat(),
        }
    )
