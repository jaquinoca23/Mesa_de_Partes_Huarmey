from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import TipoDocumental


@api_view(['GET'])
@authentication_classes([])  # público: el ciudadano no tiene cuenta (ver nota en apps/expedientes/views.py)
@permission_classes([AllowAny])
def tipos_documentales(request):
    """
    GET /api/catalogos/tipos-documentales/
    Lista los tipos de documento ACTIVOS para el formulario. Solo expone los datos necesarios.
    """
    tipos = (
        TipoDocumental.objects.filter(activo=True)
        .order_by('orden', 'nombre')
        .values('codigo', 'nombre', 'descripcion')
    )
    return Response(list(tipos))
