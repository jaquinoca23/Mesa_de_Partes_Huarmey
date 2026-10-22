import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notificacion

logger = logging.getLogger(__name__)


def enviar_notificacion(expediente, tipo, asunto, cuerpo):
    """
    Envía un correo al contacto del expediente y deja constancia del resultado.
    Un fallo de correo NUNCA debe impedir el registro ni el cambio de estado: se anota y se sigue.
    En desarrollo el correo no sale a internet: se imprime en la terminal de Django.
    """
    destinatario = expediente.email_contacto
    notificacion = Notificacion(expediente=expediente, destinatario=destinatario, tipo=tipo, asunto=asunto[:200])
    if not destinatario:
        notificacion.estado = Notificacion.Estado.FALLIDA
        notificacion.error = 'El expediente no tiene correo de contacto.'
    else:
        try:
            send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [destinatario], fail_silently=False)
            notificacion.estado = Notificacion.Estado.ENVIADA
        except Exception as error:  # noqa: BLE001 - cualquier fallo de correo se registra y no detiene el trámite
            logger.warning('No se pudo enviar la notificación del expediente %s: %s', expediente.pk, type(error).__name__)
            notificacion.estado = Notificacion.Estado.FALLIDA
            notificacion.error = type(error).__name__
    notificacion.save()
    return notificacion


def notificar_registro(expediente):
    """Correo con el número de expediente y el código de verificación."""
    recepcion = timezone.localtime(expediente.fecha_recepcion).strftime('%d/%m/%Y %H:%M:%S')
    cuerpo = (
        'Hola,\n\n'
        'Tu solicitud fue registrada en la Mesa de Partes Digital (versión de demostración).\n\n'
        f'Número de expediente: {expediente.numero}\n'
        f'Código de verificación: {expediente.codigo_verificacion}\n'
        f'Fecha de recepción: {recepcion} (hora de Lima)\n\n'
        'Con el número y el código puedes consultar el estado de tu trámite en el portal.\n'
        'Este mensaje es de demostración y no constituye una constancia oficial.\n'
    )
    return enviar_notificacion(
        expediente,
        Notificacion.Tipo.CARGO,
        f'Cargo de recepción - Expediente {expediente.numero}',
        cuerpo,
    )


def notificar_cambio_estado(expediente):
    """Correo informando el nuevo estado (sin el código de verificación)."""
    cuerpo = (
        'Hola,\n\n'
        f'El expediente {expediente.numero} cambió de estado.\n'
        f'Estado actual: {expediente.estado_actual.nombre}\n\n'
        'Puedes consultar el detalle en el portal con tu número de expediente y tu código de verificación.\n'
        'Este mensaje es de demostración.\n'
    )
    return enviar_notificacion(
        expediente,
        Notificacion.Tipo.CAMBIO_ESTADO,
        f'Actualización de tu expediente {expediente.numero}',
        cuerpo,
    )
