"""Rutas del panel administrativo: /api/panel/..."""
from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.catalogos.views_panel import EstadoViewSet, TipoDocumentalViewSet
from apps.organizacion.views_panel import AreaViewSet
from apps.expedientes import views_panel as exp
from apps.expedientes import views_reportes as rep
from apps.usuarios.views_panel import RolesView, UsuarioViewSet

router = SimpleRouter()
router.register('usuarios', UsuarioViewSet, basename='panel-usuarios')
router.register('areas', AreaViewSet, basename='panel-areas')
router.register('tipos-documentales', TipoDocumentalViewSet, basename='panel-tipos-documentales')
router.register('estados', EstadoViewSet, basename='panel-estados')

urlpatterns = [
    path('roles/', RolesView.as_view(), name='panel-roles'),
    path('expedientes/', exp.BandejaView.as_view(), name='panel-bandeja'),
    path('expedientes/opciones/', exp.OpcionesView.as_view(), name='panel-exp-opciones'),
    path('expedientes/<uuid:uuid>/', exp.DetalleView.as_view(), name='panel-exp-detalle'),
    path('expedientes/<uuid:uuid>/cambiar-estado/', exp.CambiarEstadoView.as_view(), name='panel-exp-estado'),
    path('expedientes/<uuid:uuid>/derivar/', exp.DerivarView.as_view(), name='panel-exp-derivar'),
    path('expedientes/<uuid:uuid>/actuaciones/', exp.ActuacionView.as_view(), name='panel-exp-actuacion'),
    path('derivaciones/<int:pk>/recibir/', exp.RecibirDerivacionView.as_view(), name='panel-der-recibir'),
    path('adjuntos/<int:pk>/descargar/', exp.DescargarAdjuntoView.as_view(), name='panel-adjunto'),
    path('dashboard/', rep.DashboardView.as_view(), name='panel-dashboard'),
    path('reportes/resumen/', rep.ReporteResumenView.as_view(), name='panel-reporte-resumen'),
    path('reportes/exportar.csv', rep.ReporteCsvView.as_view(), name='panel-reporte-csv'),
    path('auditoria/', rep.AuditoriaView.as_view(), name='panel-auditoria'),
    path('auditoria/acciones/', rep.AuditoriaAccionesView.as_view(), name='panel-auditoria-acciones'),
    *router.urls,
]
