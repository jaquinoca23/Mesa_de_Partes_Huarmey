"""
Carga datos de PRUEBA (ficticios) para desarrollo:  python manage.py cargar_datos_ficticios

Se puede ejecutar varias veces sin duplicar nada.
Ningún dato de este archivo es oficial ni real: los tipos documentales, los estados y las
áreas son propuestas provisionales hasta validarlas con la Municipalidad Provincial de Huarmey.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogos.models import EstadoExpediente, TipoDocumental
from apps.expedientes.models import Expediente, HistorialEstado, Solicitante
from apps.organizacion.models import Area

# (código, nombre, ¿es procedimiento del TUPA?)  -> TUPA siempre False hasta validar.
TIPOS_DOCUMENTALES = [
    ('solicitud', 'Solicitud'),
    ('escrito', 'Escrito'),
    ('carta', 'Carta'),
    ('oficio', 'Oficio'),
    ('informe', 'Informe'),
    ('recurso-administrativo', 'Recurso administrativo'),
    ('queja-reclamo', 'Queja o reclamo'),
    ('acceso-informacion-publica', 'Solicitud de acceso a la información pública'),
    ('comunicacion-persona-juridica', 'Comunicación de una persona jurídica'),
    ('otros', 'Otros documentos'),
]

# (código, nombre, significado, ¿inicial?, ¿final?)
ESTADOS = [
    ('recibido', 'Recibido', 'El documento fue registrado por el sistema.', True, False),
    ('pendiente-revision', 'Pendiente de revisión', 'Espera ser revisado por el personal de mesa de partes.', False, False),
    ('en-derivacion', 'En derivación', 'Fue enviado a un área y aún no ha sido recibido por ella.', False, False),
    ('en-atencion', 'En atención', 'Un área está trabajando en el trámite.', False, False),
    ('pendiente-informacion', 'Pendiente de información', 'Se espera información o documentos adicionales del solicitante.', False, False),
    ('atendido', 'Atendido', 'El trámite fue resuelto.', False, True),
    ('archivado', 'Archivado', 'El expediente fue archivado.', False, True),
]

# (nombre, tipo, nombre del área superior). Nombres genéricos a propósito.
AREAS = [
    ('Municipalidad de Ejemplo (FICTICIO)', Area.TipoArea.MUNICIPALIDAD, None),
    ('Gerencia de Ejemplo 1 (FICTICIO)', Area.TipoArea.GERENCIA, 'Municipalidad de Ejemplo (FICTICIO)'),
    ('Gerencia de Ejemplo 2 (FICTICIO)', Area.TipoArea.GERENCIA, 'Municipalidad de Ejemplo (FICTICIO)'),
    ('Subgerencia de Ejemplo 1.1 (FICTICIO)', Area.TipoArea.SUBGERENCIA, 'Gerencia de Ejemplo 1 (FICTICIO)'),
    ('Oficina de Ejemplo A (FICTICIO)', Area.TipoArea.OFICINA, 'Municipalidad de Ejemplo (FICTICIO)'),
    ('Unidad de Ejemplo A.1 (FICTICIO)', Area.TipoArea.UNIDAD, 'Oficina de Ejemplo A (FICTICIO)'),
]

# Solicitantes y expedientes de demostración. Documentos y correos obviamente falsos.
EXPEDIENTES_DEMO = [
    {
        'persona': dict(tipo_persona='NATURAL', tipo_documento_identidad='DNI', numero_documento='00000001',
                        nombres='Ana', apellidos='Ejemplo Uno', email='ana.ejemplo@example.com', telefono='900000001'),
        'tipo': 'solicitud',
        'asunto': 'Solicitud de prueba 1 (FICTICIO)',
        'descripcion': 'Expediente de demostración con datos ficticios.',
    },
    {
        'persona': dict(tipo_persona='NATURAL', tipo_documento_identidad='DNI', numero_documento='00000002',
                        nombres='Luis', apellidos='Ejemplo Dos', email='luis.ejemplo@example.com', telefono='900000002'),
        'tipo': 'queja-reclamo',
        'asunto': 'Queja de prueba 2 (FICTICIO)',
        'descripcion': 'Expediente de demostración con datos ficticios.',
    },
    {
        'persona': dict(tipo_persona='JURIDICA', tipo_documento_identidad='RUC', numero_documento='00000000001',
                        razon_social='Empresa de Ejemplo S.A.C. (FICTICIA)', email='contacto@example.com', telefono='900000003'),
        'tipo': 'comunicacion-persona-juridica',
        'asunto': 'Comunicación de prueba 3 (FICTICIO)',
        'descripcion': 'Expediente de demostración con datos ficticios.',
    },
]


class Command(BaseCommand):
    help = 'Carga catálogos, áreas y expedientes FICTICIOS para desarrollo (se puede repetir sin duplicar).'

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Tipos documentales
        for orden, (codigo, nombre) in enumerate(TIPOS_DOCUMENTALES, start=1):
            TipoDocumental.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': 'Categoría de prueba (por validar con la municipalidad).',
                    'es_procedimiento_tupa': False,
                    'es_provisional': True,
                    'orden': orden,
                },
            )

        # 2. Estados
        for orden, (codigo, nombre, descripcion, inicial, final) in enumerate(ESTADOS, start=1):
            EstadoExpediente.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'es_inicial': inicial,
                    'es_final': final,
                    'es_provisional': True,
                    'orden': orden,
                },
            )

        # 3. Áreas (en orden: primero las superiores)
        areas = {}
        for nombre, tipo, nombre_padre in AREAS:
            area, _ = Area.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'tipo': tipo,
                    'padre': areas.get(nombre_padre),
                    'es_ficticia': True,
                },
            )
            areas[nombre] = area

        # 4. Expedientes de demostración (solo si todavía no existen)
        estado_inicial = EstadoExpediente.objects.get(es_inicial=True)
        creados = 0
        for datos in EXPEDIENTES_DEMO:
            persona_datos = dict(datos['persona'])
            persona, _ = Solicitante.objects.get_or_create(
                tipo_documento_identidad=persona_datos.pop('tipo_documento_identidad'),
                numero_documento=persona_datos.pop('numero_documento'),
                defaults=persona_datos,
            )
            if Expediente.objects.filter(solicitante=persona, asunto=datos['asunto']).exists():
                continue
            expediente = Expediente.objects.create(
                solicitante=persona,
                tipo_documental=TipoDocumental.objects.get(codigo=datos['tipo']),
                estado_actual=estado_inicial,
                asunto=datos['asunto'],
                descripcion=datos['descripcion'],
                email_contacto=persona.email,
                telefono_contacto=persona.telefono,
            )
            HistorialEstado.objects.create(
                expediente=expediente,
                estado_anterior=None,
                estado_nuevo=estado_inicial,
                observacion='Registro inicial (dato ficticio).',
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Datos ficticios listos: {TipoDocumental.objects.count()} tipos documentales, '
            f'{EstadoExpediente.objects.count()} estados, {Area.objects.count()} áreas, '
            f'{creados} expedientes nuevos.'
        ))
