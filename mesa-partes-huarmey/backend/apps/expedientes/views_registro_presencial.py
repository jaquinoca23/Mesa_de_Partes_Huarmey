"""Registro autenticado de documentos recibidos en la mesa de partes física."""
from django.db import transaction
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar
from apps.core.permisos import requiere
from apps.documentos.servicios import validar_archivos_subidos, guardar_adjunto
from apps.organizacion.models import Area
from apps.usuarios.models import Usuario
from .models import Expediente
from .serializers import SolicitudSerializer
from . import servicios


class RegistroPresencialSerializer(SolicitudSerializer):
    acepta_politica_privacidad = None
    declara_veracidad = None
    email = serializers.EmailField(max_length=254, required=False, allow_blank=True, default='')
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.filter(activo=True))
    mensaje = serializers.CharField(max_length=2000, required=False, allow_blank=True, default='')


class RegistroPresencialView(APIView):
    permission_classes = [requiere('expedientes.add_expediente', 'expedientes.view_expediente', 'expedientes.derivar_expediente')]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializador = RegistroPresencialSerializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        datos = serializador.validated_data
        principales = request.FILES.getlist('documento')
        anexos = request.FILES.getlist('anexos')
        errores = {}
        if len(principales) != 1:
            errores['documento'] = ['Adjunta un único documento principal escaneado.']
        elif principales[0].name.rsplit('.', 1)[-1].lower() not in ('pdf', 'jpg', 'jpeg', 'png'):
            errores['documento'] = ['El escaneo debe ser PDF, JPG o PNG.']
        problemas = validar_archivos_subidos(principales + anexos)
        if problemas:
            errores['anexos'] = problemas
        if request.user.area_id == datos['area'].pk:
            errores['area'] = ['Selecciona un área de destino diferente al área de origen.']
        if not request.user.area_id and not servicios.ve_todos(request.user):
            return Response({'mensaje': 'Necesitas un área asignada para registrar documentos.'}, status=403)
        if errores:
            return Response(errores, status=400)
        guardados = []
        try:
            with transaction.atomic():
                # Serializa los reintentos del mismo trabajador, incluso si llegan a la vez.
                Usuario.objects.select_for_update().get(pk=request.user.pk)
                existente = Expediente.objects.filter(clave_envio=datos['clave_envio']).first()
                if existente:
                    if not existente.historial.filter(usuario=request.user, estado_anterior__isnull=True).exists():
                        return Response({'mensaje': 'La clave de envío ya está en uso. Inicia un registro nuevo.'}, status=409)
                    return Response({'uuid': str(existente.uuid), 'numero': existente.numero, 'duplicado': True})
                expediente = servicios._crear(datos, [], servicios._estado_inicial(), usuario=request.user)
                for i, archivo in enumerate(principales + anexos):
                    adjunto = guardar_adjunto(expediente, archivo)
                    guardados.append(adjunto.archivo)
                    if i == 0:
                        adjunto.es_principal = True
                        adjunto.save(update_fields=['es_principal'])
                derivacion = servicios.derivar(expediente, request.user, datos['area'], 'Atención de documento recibido en mesa de partes física', datos['mensaje'])
                registrar(request, RegistroAuditoria.Accion.EXPEDIENTE_REGISTRADO, expediente, 'Registro presencial digitalizado.')
                registrar(request, RegistroAuditoria.Accion.DERIVACION_CREADA, derivacion, f'Expediente {expediente.numero}')
        except Exception as error:
            for archivo in guardados:
                archivo.delete(save=False)
            if isinstance(error, servicios.ErrorDeRegla):
                return Response({'mensaje': error.mensaje}, status=error.estado)
            if isinstance(error, servicios.ErrorDeConfiguracion):
                return Response({'mensaje': 'No hay un estado inicial configurado para registrar documentos.'}, status=503)
            raise
        return Response({'uuid': str(expediente.uuid), 'numero': expediente.numero, 'duplicado': False}, status=201)
