from .models import RegistroAuditoria


def registrar(request, accion, objeto=None, detalle='', usuario=None):
    """
    Deja constancia de una acción importante.

    - request: la petición actual (de ahí salen el usuario y la dirección IP). Puede ser None.
    - accion: un valor de RegistroAuditoria.Accion.
    - objeto: el registro afectado (se guarda su tipo y su identificador, no sus datos).
    - detalle: texto corto SIN datos personales.
    """
    if usuario is None and request is not None:
        candidato = getattr(request, 'user', None)
        if candidato is not None and candidato.is_authenticated:
            usuario = candidato
    ip = request.META.get('REMOTE_ADDR') if request is not None else None
    return RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        objeto_tipo=objeto.__class__.__name__ if objeto is not None else '',
        objeto_id=str(objeto.pk) if objeto is not None else '',
        detalle=str(detalle)[:300],
        ip=ip or None,
    )
