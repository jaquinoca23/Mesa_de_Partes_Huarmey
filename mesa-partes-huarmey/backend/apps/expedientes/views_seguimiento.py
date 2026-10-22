import secrets

from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Expediente
from .servicios import construir_cargo

NO_ENCONTRADO = {
    'ok': False,
    'mensaje': 'No encontramos un expediente con esos datos. Revisa el número y el código de verificación.',
}


class ConsultaSerializer(serializers.Serializer):
    numero = serializers.CharField(max_length=20)
    codigo = serializers.CharField(max_length=12)


class ConsultarExpedienteView(APIView):
    """
    POST /api/seguimiento/consultar/   { "numero": "2026-000001", "codigo": "ABCD2345" }

    Consulta pública. Exige DOS datos (número + código aleatorio) y limita los intentos.
    Si algo no coincide responde SIEMPRE lo mismo (404 genérico): no revela si el número existe.
    Solo devuelve datos básicos y el historial de estados (nunca datos personales ni notas internas).
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'consulta'

    def post(self, request):
        serializador = ConsultaSerializer(data=request.data)
        if not serializador.is_valid():
            return Response({'ok': False, 'mensaje': 'Ingresa el número de expediente y el código de verificación.'}, status=400)

        numero = serializador.validated_data['numero'].strip()
        codigo = serializador.validated_data['codigo'].strip().upper()

        expediente = (
            Expediente.objects.select_related('estado_actual', 'tipo_documental', 'solicitante')
            .filter(numero=numero)
            .first()
        )
        # Se compara siempre (aunque no exista) con tiempo constante para no filtrar información.
        esperado = expediente.codigo_verificacion if expediente else 'XXXXXXXX'
        coincide = secrets.compare_digest(codigo.encode(), esperado.encode())
        if expediente is None or not coincide:
            return Response(NO_ENCONTRADO, status=404)

        historial = [
            {
                'estado': h.estado_nuevo.nombre,
                'fecha': timezone.localtime(h.fecha).isoformat(),
            }
            for h in expediente.historial.select_related('estado_nuevo')
        ]
        cargo = construir_cargo(expediente)
        return Response(
            {
                'ok': True,
                'numero': expediente.numero,
                'estado': expediente.estado_actual.nombre,
                'estado_descripcion': expediente.estado_actual.descripcion,
                'tipo_documental': expediente.tipo_documental.nombre,
                'asunto': expediente.asunto,
                'fecha_recepcion': cargo['fecha_recepcion'],
                'historial': historial,
                'cargo': cargo,
            }
        )
