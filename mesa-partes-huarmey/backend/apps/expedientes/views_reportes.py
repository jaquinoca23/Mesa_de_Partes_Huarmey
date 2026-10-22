"""Panel de resumen, reportes y exportación CSV (ETAPA 8). Todo se limita a lo que el usuario puede ver."""
import csv

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.servicios import registrar
from apps.core.paginacion import PaginacionEstandar
from apps.core.permisos import requiere
from apps.derivaciones.models import Derivacion

from . import servicios

VER = requiere('expedientes.view_expediente')
VER_REPORTES = requiere('expedientes.view_expediente', 'expedientes.ver_reportes')
MAX_FILAS_CSV = 10000


def filtrar(consulta, params):
    """Filtros comunes de los reportes. Lanza ErrorDeRegla(400) si una fecha no es válida."""
    if params.get('estado'):
        consulta = consulta.filter(estado_actual__codigo=params['estado'])
    if params.get('tipo'):
        consulta = consulta.filter(tipo_documental__codigo=params['tipo'])
    if params.get('area', '').isdigit():
        consulta = consulta.filter(area_actual_id=int(params['area']))
    for parametro, filtro in (('desde', 'fecha_recepcion__date__gte'), ('hasta', 'fecha_recepcion__date__lte')):
        if params.get(parametro):
            fecha = parse_date(params[parametro])
            if fecha is None:
                raise servicios.ErrorDeRegla(f'La fecha "{parametro}" no es válida (use AAAA-MM-DD).', 400)
            consulta = consulta.filter(**{filtro: fecha})
    return consulta


def _grupo(consulta, campo, nombre_vacio=None):
    filas = consulta.values(campo).annotate(total=Count('id')).order_by('-total')
    return [{'nombre': f[campo] or nombre_vacio or 'Sin dato', 'total': f['total']} for f in filas]


class DashboardView(APIView):
    """GET /api/panel/dashboard/ — resumen rápido para la pantalla de inicio."""

    permission_classes = [VER]

    def get(self, request):
        consulta = servicios.expedientes_visibles(request.user)
        por_recibir = 0
        if request.user.area_id:
            por_recibir = Derivacion.objects.filter(
                area_destino_id=request.user.area_id, estado_recepcion=Derivacion.EstadoRecepcion.PENDIENTE
            ).count()
        recientes = consulta.select_related('estado_actual').order_by('-fecha_recepcion', '-id')[:5]
        return Response(
            {
                'total': consulta.count(),
                'por_recibir': por_recibir,
                'por_estado': _grupo(consulta, 'estado_actual__nombre'),
                'recientes': [
                    {'uuid': str(e.uuid), 'numero': e.numero, 'asunto': e.asunto, 'estado': e.estado_actual.nombre}
                    for e in recientes
                ],
            }
        )


class ReporteResumenView(APIView):
    """GET /api/panel/reportes/resumen/?desde=&hasta=&estado=&tipo=&area="""

    permission_classes = [VER_REPORTES]

    def get(self, request):
        try:
            consulta = filtrar(servicios.expedientes_visibles(request.user), request.query_params)
        except servicios.ErrorDeRegla as error:
            return Response({'ok': False, 'mensaje': error.mensaje}, status=error.estado)
        por_mes = (
            consulta.annotate(mes=TruncMonth('fecha_recepcion')).values('mes').annotate(total=Count('id')).order_by('mes')
        )
        return Response(
            {
                'total': consulta.count(),
                'por_estado': _grupo(consulta, 'estado_actual__nombre'),
                'por_tipo': _grupo(consulta, 'tipo_documental__nombre'),
                'por_area': _grupo(consulta, 'area_actual__nombre', 'Mesa de partes'),
                'por_mes': [{'nombre': m['mes'].strftime('%Y-%m'), 'total': m['total']} for m in por_mes],
                'nota': 'Conteos informativos. Los plazos de atención no se calculan: están pendientes de validar con la municipalidad.',
            }
        )


def celda_segura(valor):
    """
    Evita la "inyección de fórmulas": si un texto empieza con = + - @ (o tabulación/retorno), Excel
    podría ejecutarlo como fórmula al abrir el CSV. Se le antepone un apóstrofo para que sea texto.
    """
    texto = '' if valor is None else str(valor)
    if texto[:1] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + texto
    return texto


class ReporteCsvView(APIView):
    """GET /api/panel/reportes/exportar.csv — mismos filtros. No incluye datos personales del solicitante."""

    permission_classes = [VER_REPORTES]

    def get(self, request):
        try:
            consulta = filtrar(servicios.expedientes_visibles(request.user), request.query_params)
        except servicios.ErrorDeRegla as error:
            return Response({'ok': False, 'mensaje': error.mensaje}, status=error.estado)
        consulta = consulta.select_related('estado_actual', 'tipo_documental', 'area_actual').order_by('-fecha_recepcion', '-id')

        respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
        respuesta['Content-Disposition'] = 'attachment; filename="expedientes.csv"'
        respuesta['X-Content-Type-Options'] = 'nosniff'
        respuesta['Cache-Control'] = 'private, no-store'
        respuesta.write('﻿')  # BOM: Excel reconoce las tildes
        escritor = csv.writer(respuesta)
        escritor.writerow(['Número', 'Fecha de recepción', 'Tipo de documento', 'Asunto', 'Estado', 'Área actual'])
        filas = 0
        for e in consulta[:MAX_FILAS_CSV]:
            escritor.writerow(
                [
                    celda_segura(e.numero),
                    timezone.localtime(e.fecha_recepcion).strftime('%Y-%m-%d %H:%M'),
                    celda_segura(e.tipo_documental.nombre),
                    celda_segura(e.asunto),
                    celda_segura(e.estado_actual.nombre),
                    celda_segura(e.area_actual.nombre if e.area_actual_id else 'Mesa de partes'),
                ]
            )
            filas += 1
        registrar(request, RegistroAuditoria.Accion.REPORTE_EXPORTADO, detalle=f'{filas} filas. Filtros: {dict(request.query_params.items())}')
        return respuesta


class AuditoriaView(APIView):
    """GET /api/panel/auditoria/?accion=&desde=&hasta=&page= — bitácora (solo lectura)."""

    permission_classes = [requiere('auditoria.view_registroauditoria')]

    def get(self, request):
        p = request.query_params
        consulta = RegistroAuditoria.objects.select_related('usuario')
        if p.get('accion') in RegistroAuditoria.Accion.values:
            consulta = consulta.filter(accion=p['accion'])
        for parametro, filtro in (('desde', 'fecha__date__gte'), ('hasta', 'fecha__date__lte')):
            if p.get(parametro):
                fecha = parse_date(p[parametro])
                if fecha is None:
                    return Response({'ok': False, 'mensaje': f'La fecha "{parametro}" no es válida.'}, status=400)
                consulta = consulta.filter(**{filtro: fecha})
        paginador = PaginacionEstandar()
        pagina = paginador.paginate_queryset(consulta, request)
        return paginador.get_paginated_response(
            [
                {
                    'fecha': timezone.localtime(r.fecha).isoformat(),
                    'usuario': (r.usuario.get_full_name() or r.usuario.username) if r.usuario_id else 'Ciudadano / sistema',
                    'accion': r.get_accion_display(),
                    'objeto': f'{r.objeto_tipo} {r.objeto_id}'.strip(),
                    'detalle': r.detalle,
                    'ip': r.ip,
                }
                for r in pagina
            ]
        )


class AuditoriaAccionesView(APIView):
    """GET /api/panel/auditoria/acciones/ — opciones del filtro."""

    permission_classes = [requiere('auditoria.view_registroauditoria')]

    def get(self, request):
        return Response([{'valor': v, 'etiqueta': e} for v, e in RegistroAuditoria.Accion.choices])
