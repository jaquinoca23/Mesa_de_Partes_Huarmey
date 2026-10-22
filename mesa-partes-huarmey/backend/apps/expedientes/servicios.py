"""
Lógica de negocio del registro de expedientes (ETAPA 5).

Regla de oro: una solicitud solo se considera REGISTRADA cuando la base de datos ya la guardó.
Si algo falla, se lanza un error y NO se devuelve ningún cargo.
"""
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from apps.catalogos.models import EstadoExpediente
from apps.derivaciones.models import Actuacion, Derivacion
from apps.documentos.servicios import guardar_adjunto

from .models import Expediente, HistorialEstado, Solicitante

# Advertencias que SIEMPRE acompañan al cargo (redacción provisional, por validar con la municipalidad).
ADVERTENCIAS_CARGO = [
    'Este cargo es una constancia informativa de recepción de la versión de demostración.',
    'No es una firma digital ni una constancia legal con validez oficial.',
    'Los plazos de atención dependen de la normativa vigente y aún no están configurados en este sistema.',
    'Conserva tu número de expediente y tu código de verificación: los necesitarás para consultar tu trámite.',
]


class ErrorDeConfiguracion(Exception):
    """El sistema no está listo para registrar (por ejemplo, falta el estado inicial)."""


def enmascarar_documento(numero):
    """Muestra solo los 2 últimos caracteres del documento: 12345678 -> ******78."""
    numero = str(numero or '')
    if len(numero) <= 2:
        return '*' * len(numero)
    return '*' * (len(numero) - 2) + numero[-2:]


def _estado_inicial():
    estado = EstadoExpediente.objects.filter(es_inicial=True, activo=True).first()
    if estado is None:
        raise ErrorDeConfiguracion('No hay un estado inicial configurado. Ejecuta cargar_datos_ficticios.')
    return estado


def _crear(datos, archivos, estado_inicial):
    """Crea todo en UNA transacción: o se guarda todo, o no se guarda nada."""
    with transaction.atomic():
        persona_datos = {
            'tipo_persona': datos['tipo_persona'],
            'nombres': datos.get('nombres', ''),
            'apellidos': datos.get('apellidos', ''),
            'razon_social': datos.get('razon_social', ''),
            'email': datos['email'],
            'telefono': datos.get('telefono', ''),
        }
        # Si el documento ya existe se reutiliza el solicitante SIN sobrescribir sus datos guardados
        # (un tercero no puede alterar los datos de otra persona enviando un formulario).
        solicitante, _ = Solicitante.objects.get_or_create(
            tipo_documento_identidad=datos['tipo_documento_identidad'],
            numero_documento=datos['numero_documento'],
            defaults=persona_datos,
        )
        expediente = Expediente.objects.create(
            clave_envio=datos['clave_envio'],
            solicitante=solicitante,
            tipo_documental=datos['tipo_documental'],
            estado_actual=estado_inicial,
            asunto=datos['asunto'],
            descripcion=datos.get('descripcion', ''),
            email_contacto=datos['email'],
            telefono_contacto=datos.get('telefono', ''),
        )
        HistorialEstado.objects.create(
            expediente=expediente,
            estado_anterior=None,
            estado_nuevo=estado_inicial,
            observacion='Solicitud recibida por la Mesa de Partes Digital.',
        )
        for archivo in archivos:
            guardar_adjunto(expediente, archivo)
        return expediente


def registrar_solicitud(datos, archivos):
    """
    Registra una solicitud ya validada. Devuelve (expediente, creado).

    Idempotente: si el mismo envío (misma clave_envio) llega dos veces — doble clic, reintento por
    mala conexión — no se crea otro expediente: se devuelve el primero y creado=False.
    """
    clave = datos['clave_envio']
    existente = Expediente.objects.filter(clave_envio=clave).first()
    if existente:
        return existente, False

    estado_inicial = _estado_inicial()
    try:
        return _crear(datos, archivos, estado_inicial), True
    except IntegrityError:
        # Dos envíos idénticos simultáneos: el segundo choca con la restricción de unicidad.
        existente = Expediente.objects.filter(clave_envio=clave).first()
        if existente:
            return existente, False
        raise


def construir_cargo(expediente):
    """Datos del cargo de recepción. Solo muestra datos mínimos (documento enmascarado)."""
    solicitante = expediente.solicitante
    return {
        'numero': expediente.numero,
        'codigo_verificacion': expediente.codigo_verificacion,
        'fecha_recepcion': timezone.localtime(expediente.fecha_recepcion).isoformat(),
        'zona_horaria': 'America/Lima',
        'estado': expediente.estado_actual.nombre,
        'tipo_documental': expediente.tipo_documental.nombre,
        'asunto': expediente.asunto,
        'solicitante': solicitante.nombre_para_mostrar,
        'documento_identidad': f'{solicitante.tipo_documento_identidad} {enmascarar_documento(solicitante.numero_documento)}',
        'adjuntos': [
            {'nombre': a.nombre_original, 'tamano': a.tamano, 'sha256': a.sha256}
            for a in expediente.adjuntos.all()
        ],
        'advertencias': ADVERTENCIAS_CARGO,
    }


# ---------------------------------------------------------------------------
# ETAPA 7: bandejas por área, derivación y recepción
# ---------------------------------------------------------------------------
# Códigos de estado que, si existen en el catálogo, se aplican automáticamente (son PROVISIONALES).
CODIGO_ESTADO_DERIVACION = 'en-derivacion'
CODIGO_ESTADO_RECEPCION = 'en-atencion'


class ErrorDeRegla(Exception):
    """Una regla del trámite impide la acción. 'estado' es el código HTTP sugerido."""

    def __init__(self, mensaje, estado=409):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.estado = estado


def ve_todos(usuario):
    return usuario.has_perm('expedientes.ver_todos_expedientes')


def expedientes_visibles(usuario):
    """
    Qué expedientes puede ver este usuario (se aplica en TODAS las consultas del panel):
    - con el permiso "ver todos": todos;
    - los demás: los que tiene su área hoy, más los que le han derivado y aún no recibió.
    Un usuario sin área no ve ninguno.
    """
    consulta = Expediente.objects.all()
    if ve_todos(usuario):
        return consulta
    if not usuario.area_id:
        return consulta.none()
    pendientes = Derivacion.objects.filter(
        area_destino_id=usuario.area_id, estado_recepcion=Derivacion.EstadoRecepcion.PENDIENTE
    ).values('expediente_id')
    return consulta.filter(Q(area_actual_id=usuario.area_id) | Q(pk__in=pendientes))


def puede_gestionar(usuario, expediente):
    """Quién puede actuar sobre un expediente: quien ve todo, o el área que lo tiene hoy."""
    if ve_todos(usuario):
        return True
    return bool(usuario.area_id and expediente.area_actual_id == usuario.area_id)


def derivacion_pendiente(expediente):
    return expediente.derivaciones.filter(estado_recepcion=Derivacion.EstadoRecepcion.PENDIENTE).first()


def puede_recibir(usuario, derivacion):
    if derivacion.estado_recepcion != Derivacion.EstadoRecepcion.PENDIENTE or not usuario.is_active:
        return False
    if usuario.is_superuser:
        return True
    if derivacion.usuario_receptor_id:
        return derivacion.usuario_receptor_id == usuario.pk
    return bool(usuario.area_id and usuario.area_id == derivacion.area_destino_id)


def _estado_por_codigo(codigo):
    return EstadoExpediente.objects.filter(codigo=codigo, activo=True).first()


def cambiar_estado(expediente, usuario, nuevo_estado, observacion=''):
    if not puede_gestionar(usuario, expediente):
        raise ErrorDeRegla('Este expediente no está en tu área.', 403)
    if not nuevo_estado.activo:
        raise ErrorDeRegla('Ese estado no está activo.', 400)
    if derivacion_pendiente(expediente):
        raise ErrorDeRegla('El expediente tiene una derivación pendiente de recepción. El área de destino debe recibirlo primero.')
    if expediente.estado_actual.es_final:
        raise ErrorDeRegla('El expediente ya está en un estado final y no se puede modificar.')
    if nuevo_estado.pk == expediente.estado_actual_id:
        raise ErrorDeRegla('El expediente ya se encuentra en ese estado.', 400)
    expediente.cambiar_estado(nuevo_estado, usuario=usuario, observacion=observacion)
    return expediente


def derivar(expediente, usuario, area_destino, motivo, observaciones='', receptor=None):
    if not puede_gestionar(usuario, expediente):
        raise ErrorDeRegla('Este expediente no está en tu área.', 403)
    if expediente.estado_actual.es_final:
        raise ErrorDeRegla('No se puede derivar un expediente en estado final.')
    if not area_destino.activo:
        raise ErrorDeRegla('El área de destino no está activa.', 400)
    if expediente.area_actual_id == area_destino.pk:
        raise ErrorDeRegla('El expediente ya está en esa área.', 400)
    if receptor is not None and (not receptor.is_active or receptor.area_id != area_destino.pk):
        raise ErrorDeRegla('La persona receptora debe estar activa y pertenecer al área de destino.', 400)
    try:
        with transaction.atomic():
            # Se bloquea el expediente: dos derivaciones simultáneas no pueden coexistir.
            Expediente.objects.select_for_update().get(pk=expediente.pk)
            if derivacion_pendiente(expediente):
                raise ErrorDeRegla('Ya existe una derivación pendiente de recepción.')
            derivacion = Derivacion.objects.create(
                expediente=expediente,
                area_origen=expediente.area_actual,
                area_destino=area_destino,
                usuario_remitente=usuario,
                usuario_receptor=receptor,
                motivo=motivo,
                observaciones=observaciones,
            )
            estado = _estado_por_codigo(CODIGO_ESTADO_DERIVACION)
            if estado and estado.pk != expediente.estado_actual_id:
                expediente.cambiar_estado(estado, usuario=usuario, observacion=f'Derivado a {area_destino.nombre}.')
            return derivacion
    except IntegrityError:
        raise ErrorDeRegla('Ya existe una derivación pendiente de recepción.')


def recibir_derivacion(derivacion_id, usuario):
    """El área de destino confirma la recepción: el expediente pasa a ser suyo."""
    with transaction.atomic():
        derivacion = (
            Derivacion.objects.select_for_update().select_related('expediente', 'area_destino').filter(pk=derivacion_id).first()
        )
        if derivacion is None or not expedientes_visibles(usuario).filter(pk=derivacion.expediente_id).exists():
            raise ErrorDeRegla('No se encontró la derivación.', 404)
        if derivacion.estado_recepcion != Derivacion.EstadoRecepcion.PENDIENTE:
            raise ErrorDeRegla('Esta derivación ya fue recibida.')
        if not puede_recibir(usuario, derivacion):
            raise ErrorDeRegla('No puedes recibir esta derivación.', 403)
        derivacion.estado_recepcion = Derivacion.EstadoRecepcion.RECIBIDA
        derivacion.fecha_recepcion = timezone.now()
        derivacion.recibido_por = usuario
        derivacion.save(update_fields=['estado_recepcion', 'fecha_recepcion', 'recibido_por'])
        expediente = derivacion.expediente
        expediente.area_actual = derivacion.area_destino
        expediente.save(update_fields=['area_actual', 'actualizado'])
        estado = _estado_por_codigo(CODIGO_ESTADO_RECEPCION)
        if estado and estado.pk != expediente.estado_actual_id:
            expediente.cambiar_estado(estado, usuario=usuario, observacion=f'Recibido por {derivacion.area_destino.nombre}.')
        return derivacion


def registrar_actuacion(expediente, usuario, tipo, texto):
    if not puede_gestionar(usuario, expediente):
        raise ErrorDeRegla('Este expediente no está en tu área.', 403)
    return Actuacion.objects.create(expediente=expediente, usuario=usuario, tipo=tipo, texto=texto)
