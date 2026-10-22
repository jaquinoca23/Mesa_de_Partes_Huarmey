"""API del panel para el personal: bandeja, detalle y acciones sobre expedientes (ETAPA 7)."""
import re

from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils.dateparse import parse_date
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar
from apps.catalogos.models import EstadoExpediente, TipoDocumental
from apps.core.paginacion import PaginacionEstandar
from apps.core.permisos import requiere
from apps.derivaciones.models import Actuacion, Derivacion
from apps.documentos.models import Adjunto
from apps.notificaciones.servicios import notificar_cambio_estado
from apps.organizacion.models import Area
from apps.usuarios.models import Usuario

from . import servicios
from .models import Expediente
from .presentacion import a_detalle, a_lista

VER = requiere('expedientes.view_expediente')


def _responder_error(error):
    return Response({'ok': False, 'mensaje': error.mensaje}, status=error.estado)


def _expediente_visible_o_404(request, uuid):
    expediente = (
        servicios.expedientes_visibles(request.user)
        .select_related('estado_actual', 'tipo_documental', 'solicitante', 'area_actual')
        .filter(uuid=uuid)
        .first()
    )
    if expediente is None:
        raise Http404  # no se distingue "no existe" de "no es de tu área"
    return expediente


class OpcionesView(APIView):
    """GET /api/panel/expedientes/opciones/ — listas para filtros y formularios."""

    permission_classes = [VER]

    def get(self, request):
        areas = Area.objects.filter(activo=True).order_by('nombre')
        return Response(
            {
                'estados': [{'valor': e.codigo, 'etiqueta': e.nombre, 'id': e.pk} for e in EstadoExpediente.objects.filter(activo=True)],
                'tipos': [{'valor': t.codigo, 'etiqueta': t.nombre} for t in TipoDocumental.objects.filter(activo=True)],
                'areas': [{'valor': a.pk, 'etiqueta': a.nombre} for a in areas],
                've_todos': servicios.ve_todos(request.user),
                'tipos_actuacion': [{'valor': v, 'etiqueta': e} for v, e in Actuacion.Tipo.choices],
            }
        )


class BandejaView(APIView):
    """
    GET /api/panel/expedientes/?q=&estado=&tipo=&area=&pendientes=1&desde=&hasta=&page=
    Solo devuelve los expedientes que el usuario puede ver.
    """

    permission_classes = [VER]

    def get(self, request):
        p = request.query_params
        consulta = servicios.expedientes_visibles(request.user).select_related(
            'estado_actual', 'tipo_documental', 'solicitante', 'area_actual'
        )
        q = p.get('q', '').strip()[:100]
        if q:
            consulta = consulta.filter(
                Q(numero__icontains=q) | Q(asunto__icontains=q) | Q(solicitante__nombres__icontains=q)
                | Q(solicitante__apellidos__icontains=q) | Q(solicitante__razon_social__icontains=q)
                | Q(solicitante__numero_documento=q)
            )
        if p.get('estado'):
            consulta = consulta.filter(estado_actual__codigo=p['estado'])
        if p.get('tipo'):
            consulta = consulta.filter(tipo_documental__codigo=p['tipo'])
        if p.get('area', '').isdigit():
            consulta = consulta.filter(area_actual_id=int(p['area']))
        if p.get('pendientes') == '1' and request.user.area_id:
            consulta = consulta.filter(
                derivaciones__estado_recepcion=Derivacion.EstadoRecepcion.PENDIENTE,
                derivaciones__area_destino_id=request.user.area_id,
            )
        for parametro, filtro in (('desde', 'fecha_recepcion__date__gte'), ('hasta', 'fecha_recepcion__date__lte')):
            if p.get(parametro):
                fecha = parse_date(p[parametro])
                if fecha is None:
                    return Response({'ok': False, 'mensaje': f'La fecha "{parametro}" no es válida.'}, status=400)
                consulta = consulta.filter(**{filtro: fecha})

        paginador = PaginacionEstandar()
        pagina = paginador.paginate_queryset(consulta.order_by('-fecha_recepcion', '-id'), request)
        ids = [e.pk for e in pagina]
        pendientes = {
            d.expediente_id: d
            for d in Derivacion.objects.filter(expediente_id__in=ids, estado_recepcion=Derivacion.EstadoRecepcion.PENDIENTE)
        }
        return paginador.get_paginated_response([a_lista(e, request.user, pendientes) for e in pagina])


class DetalleView(APIView):
    """GET /api/panel/expedientes/<uuid>/"""

    permission_classes = [VER]

    def get(self, request, uuid):
        return Response(a_detalle(_expediente_visible_o_404(request, uuid), request.user))


class CambiarEstadoSerializer(serializers.Serializer):
    estado = serializers.SlugRelatedField(slug_field='codigo', queryset=EstadoExpediente.objects.filter(activo=True))
    observacion = serializers.CharField(max_length=1000, required=False, allow_blank=True, default='')


class CambiarEstadoView(APIView):
    """POST /api/panel/expedientes/<uuid>/cambiar-estado/ {estado, observacion}"""

    permission_classes = [requiere('expedientes.view_expediente', 'expedientes.cambiar_estado_expediente')]

    def post(self, request, uuid):
        expediente = _expediente_visible_o_404(request, uuid)
        serializador = CambiarEstadoSerializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        anterior = expediente.estado_actual.nombre
        try:
            servicios.cambiar_estado(expediente, request.user, serializador.validated_data['estado'], serializador.validated_data['observacion'])
        except servicios.ErrorDeRegla as error:
            return _responder_error(error)
        registrar(request, RegistroAuditoria.Accion.ESTADO_CAMBIADO, expediente, f'{anterior} -> {expediente.estado_actual.nombre}')
        notificar_cambio_estado(expediente)
        return Response({'ok': True, 'mensaje': 'Estado actualizado.'})


class DerivarSerializer(serializers.Serializer):
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.filter(activo=True))
    motivo = serializers.CharField(max_length=200)
    observaciones = serializers.CharField(max_length=2000, required=False, allow_blank=True, default='')
    receptor = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(is_active=True), required=False, allow_null=True, default=None)


class DerivarView(APIView):
    """POST /api/panel/expedientes/<uuid>/derivar/ {area, motivo, observaciones, receptor}"""

    permission_classes = [requiere('expedientes.view_expediente', 'expedientes.derivar_expediente')]

    def post(self, request, uuid):
        expediente = _expediente_visible_o_404(request, uuid)
        serializador = DerivarSerializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        d = serializador.validated_data
        try:
            derivacion = servicios.derivar(expediente, request.user, d['area'], d['motivo'], d['observaciones'], d['receptor'])
        except servicios.ErrorDeRegla as error:
            return _responder_error(error)
        registrar(request, RegistroAuditoria.Accion.DERIVACION_CREADA, derivacion, f'Expediente {expediente.numero} -> {d["area"].nombre}')
        antes = expediente.estado_actual_id
        expediente.refresh_from_db()
        if expediente.estado_actual_id != antes:  # solo se avisa al ciudadano si el estado cambió de verdad
            notificar_cambio_estado(expediente)
        return Response({'ok': True, 'mensaje': f'Expediente derivado a {d["area"].nombre}. Queda pendiente de recepción.'}, status=201)


class RecibirDerivacionView(APIView):
    """POST /api/panel/derivaciones/<id>/recibir/"""

    permission_classes = [VER]

    def post(self, request, pk):
        estado_antes = Expediente.objects.filter(derivaciones__pk=pk).values_list('estado_actual_id', flat=True).first()
        try:
            derivacion = servicios.recibir_derivacion(pk, request.user)
        except servicios.ErrorDeRegla as error:
            return _responder_error(error)
        registrar(request, RegistroAuditoria.Accion.DERIVACION_RECIBIDA, derivacion, f'Expediente {derivacion.expediente.numero}')
        expediente = Expediente.objects.select_related('estado_actual').get(pk=derivacion.expediente_id)
        if expediente.estado_actual_id != estado_antes:
            notificar_cambio_estado(expediente)
        return Response({'ok': True, 'mensaje': 'Derivación recibida. El expediente ahora es de tu área.'})


class ActuacionSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Actuacion.Tipo.choices)
    texto = serializers.CharField(max_length=5000, min_length=3)


class ActuacionView(APIView):
    """POST /api/panel/expedientes/<uuid>/actuaciones/ {tipo, texto}"""

    permission_classes = [requiere('expedientes.view_expediente', 'expedientes.registrar_actuacion')]

    def post(self, request, uuid):
        expediente = _expediente_visible_o_404(request, uuid)
        serializador = ActuacionSerializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        try:
            actuacion = servicios.registrar_actuacion(expediente, request.user, **serializador.validated_data)
        except servicios.ErrorDeRegla as error:
            return _responder_error(error)
        registrar(request, RegistroAuditoria.Accion.ACTUACION_REGISTRADA, actuacion, f'Expediente {expediente.numero}')
        return Response({'ok': True, 'mensaje': 'Registrado.'}, status=201)


class DescargarAdjuntoView(APIView):
    """
    GET /api/panel/adjuntos/<id>/descargar/
    El archivo vive en una carpeta privada: solo sale por aquí, con sesión, permiso y registro de auditoría.
    """

    permission_classes = [VER]

    def get(self, request, pk):
        adjunto = (
            Adjunto.objects.select_related('expediente')
            .filter(pk=pk, expediente__in=servicios.expedientes_visibles(request.user))
            .first()
        )
        if adjunto is None:
            raise Http404
        try:
            archivo = adjunto.archivo.open('rb')
        except (FileNotFoundError, ValueError):
            raise Http404
        registrar(request, RegistroAuditoria.Accion.ADJUNTO_DESCARGADO, adjunto, f'Expediente {adjunto.expediente.numero}')
        nombre = re.sub(r'[^A-Za-z0-9._ -]', '_', adjunto.nombre_original) or 'adjunto'
        respuesta = FileResponse(archivo, as_attachment=True, filename=nombre, content_type='application/octet-stream')
        respuesta['X-Content-Type-Options'] = 'nosniff'
        respuesta['Cache-Control'] = 'private, no-store'
        return respuesta
