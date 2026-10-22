"""Conversión de expedientes a JSON para el panel (lista y detalle)."""
from django.utils import timezone

from .servicios import derivacion_pendiente, puede_gestionar, puede_recibir


def _fecha(valor):
    return timezone.localtime(valor).isoformat() if valor else None


def _nombre_usuario(usuario):
    return (usuario.get_full_name() or usuario.username) if usuario else 'Sistema'


def a_lista(expediente, usuario, pendientes_por_expediente):
    """Fila de la bandeja. 'pendientes_por_expediente' = {expediente_id: derivación pendiente} (sin consultas extra)."""
    pendiente = pendientes_por_expediente.get(expediente.pk)
    return {
        'uuid': str(expediente.uuid),
        'numero': expediente.numero,
        'asunto': expediente.asunto,
        'tipo_documental': expediente.tipo_documental.nombre,
        'estado': expediente.estado_actual.nombre,
        'estado_codigo': expediente.estado_actual.codigo,
        'area_actual': expediente.area_actual.nombre if expediente.area_actual_id else None,
        'solicitante': expediente.solicitante.nombre_para_mostrar,
        'fecha_recepcion': _fecha(expediente.fecha_recepcion),
        'por_recibir': bool(pendiente and puede_recibir(usuario, pendiente)),
        'derivacion_pendiente': pendiente is not None,
    }


def a_detalle(expediente, usuario):
    solicitante = expediente.solicitante
    pendiente = derivacion_pendiente(expediente)
    gestiona = puede_gestionar(usuario, expediente)
    final = expediente.estado_actual.es_final
    return {
        'uuid': str(expediente.uuid),
        'numero': expediente.numero,
        'asunto': expediente.asunto,
        'descripcion': expediente.descripcion,
        'tipo_documental': expediente.tipo_documental.nombre,
        'estado': expediente.estado_actual.nombre,
        'estado_final': final,
        'area_actual': expediente.area_actual.nombre if expediente.area_actual_id else None,
        'fecha_recepcion': _fecha(expediente.fecha_recepcion),
        'solicitante': {
            'nombre': solicitante.nombre_para_mostrar,
            'tipo_persona': solicitante.get_tipo_persona_display(),
            'documento': f'{solicitante.tipo_documento_identidad} {solicitante.numero_documento}',
            'email': expediente.email_contacto,
            'telefono': expediente.telefono_contacto,
        },
        # Lo que React puede mostrar u ocultar. El servidor vuelve a comprobarlo al ejecutar cada acción.
        'acciones': {
            'cambiar_estado': bool(gestiona and not final and not pendiente and usuario.has_perm('expedientes.cambiar_estado_expediente')),
            'derivar': bool(gestiona and not final and not pendiente and usuario.has_perm('expedientes.derivar_expediente')),
            'actuar': bool(gestiona and usuario.has_perm('expedientes.registrar_actuacion')),
            'recibir_derivacion_id': pendiente.pk if pendiente and puede_recibir(usuario, pendiente) else None,
        },
        'derivacion_pendiente': (
            {'area_destino': pendiente.area_destino.nombre, 'motivo': pendiente.motivo} if pendiente else None
        ),
        'adjuntos': [
            {
                'id': a.pk,
                'nombre': a.nombre_original,
                'extension': a.extension,
                'tamano': a.tamano,
                'sha256': a.sha256,
            }
            for a in expediente.adjuntos.all()
        ],
        'historial': [
            {
                'estado_anterior': h.estado_anterior.nombre if h.estado_anterior_id else None,
                'estado': h.estado_nuevo.nombre,
                'usuario': _nombre_usuario(h.usuario),
                'observacion': h.observacion,
                'fecha': _fecha(h.fecha),
            }
            for h in expediente.historial.select_related('estado_anterior', 'estado_nuevo', 'usuario')
        ],
        'derivaciones': [
            {
                'id': d.pk,
                'origen': d.area_origen.nombre if d.area_origen_id else 'Mesa de partes',
                'destino': d.area_destino.nombre,
                'motivo': d.motivo,
                'observaciones': d.observaciones,
                'remitente': _nombre_usuario(d.usuario_remitente),
                'receptor_designado': _nombre_usuario(d.usuario_receptor) if d.usuario_receptor_id else None,
                'estado': d.get_estado_recepcion_display(),
                'fecha': _fecha(d.fecha),
                'fecha_recepcion': _fecha(d.fecha_recepcion),
                'recibido_por': _nombre_usuario(d.recibido_por) if d.recibido_por_id else None,
            }
            for d in expediente.derivaciones.select_related('area_origen', 'area_destino', 'usuario_remitente', 'usuario_receptor', 'recibido_por')
        ],
        'actuaciones': [
            {
                'tipo': a.get_tipo_display(),
                'texto': a.texto,
                'usuario': _nombre_usuario(a.usuario),
                'fecha': _fecha(a.fecha),
            }
            for a in expediente.actuaciones.select_related('usuario')
        ],
        # Solo el resultado del envío, nunca el contenido de los correos.
        'notificaciones': [
            {'tipo': n.get_tipo_display(), 'estado': n.get_estado_display(), 'fecha': _fecha(n.fecha)}
            for n in expediente.notificaciones.all()
        ],
    }
