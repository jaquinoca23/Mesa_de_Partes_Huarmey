from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from . import servicios


class ConsultarDniView(APIView):
    """
    GET /api/identidad/dni/<dni>/  ->  { ok, nombres, apellidos }

    Solo ayuda a completar el formulario: NO es una constancia de identidad.
    Es público (el formulario lo es), por eso tiene un límite estricto de consultas por IP.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'identidad'

    def get(self, request, dni):
        try:
            datos = servicios.consultar_dni(dni)
        except servicios.ErrorIdentidad as error:
            return Response({'ok': False, 'mensaje': error.mensaje}, status=error.estado)
        respuesta = Response({'ok': True, **datos})
        respuesta['Cache-Control'] = 'no-store'
        return respuesta
