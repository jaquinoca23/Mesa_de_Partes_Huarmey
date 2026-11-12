"""Estructura proporcionada por el propietario del sistema."""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.organizacion.models import Area

OFICINAS = {
    'Atención al Ciudadano y Gestión Documentaria': [
        'Comunicaciones e Imagen Institucional', 'Archivo Central', 'Trámite Documentario',
    ],
    'Administración': ['Contabilidad', 'Abastecimiento', 'Tesorería', 'Gestión de Recursos Humanos'],
    'Asesoría Jurídica': [],
    'Planeamiento y Presupuesto': [
        'Planeamiento, Modernización e Inversiones', 'Tecnologías de la Información', 'Presupuesto',
    ],
}
GERENCIAS = {
    'Administración Tributaria': ['Rentas', 'Fiscalización Tributaria y Ejecución Coactiva'],
    'Desarrollo Económico': ['Desarrollo Económico y Turismo', 'Promoción Comercial y Fiscalización'],
    'Infraestructura': ['Obras Públicas', 'Estudios y Proyectos'],
    'Gestión Territorial': ['Formalización y Obras Privadas', 'Gestión de Riesgos de Desastres'],
    'Servicios a la Ciudad y Gestión Ambiental': [
        'Transportes', 'Gestión Ambiental', 'Seguridad Ciudadana', 'Servicios Municipales',
    ],
    'Desarrollo Social': ['Servicios Sociales y Participación Vecinal', 'Programas Sociales'],
}
ORGANOS = [
    'Concejo Municipal', 'Alcaldía', 'Órgano de Control Institucional',
    'Procuraduría Pública Municipal', 'Consejo de Coordinación Local Provincial',
    'Junta de Delegados Vecinales',
]
AREAS_EJEMPLO = [
    'Municipalidad de Ejemplo (FICTICIO)', 'Gerencia de Ejemplo 1 (FICTICIO)',
    'Gerencia de Ejemplo 2 (FICTICIO)', 'Subgerencia de Ejemplo 1.1 (FICTICIO)',
    'Oficina de Ejemplo A (FICTICIO)', 'Unidad de Ejemplo A.1 (FICTICIO)',
]


class Command(BaseCommand):
    help = 'Carga las áreas de Huarmey indicadas por el propietario y desactiva las seis áreas de ejemplo sin eliminar su historial.'

    @transaction.atomic
    def handle(self, *args, **options):
        def guardar(nombre, tipo, padre=None):
            area, _ = Area.objects.update_or_create(
                nombre=nombre,
                defaults={'tipo': tipo, 'padre': padre, 'activo': True, 'es_ficticia': False},
            )
            return area

        municipalidad = guardar('Municipalidad Provincial de Huarmey', Area.TipoArea.MUNICIPALIDAD)
        municipal = guardar('Gerencia Municipal', Area.TipoArea.GERENCIA, municipalidad)
        for nombre, dependencias in OFICINAS.items():
            general = guardar(f'Oficina General de {nombre}', Area.TipoArea.OFICINA, municipal)
            for dependencia in dependencias:
                guardar(f'Oficina de {dependencia}', Area.TipoArea.OFICINA, general)
        for nombre, dependencias in GERENCIAS.items():
            gerencia = guardar(f'Gerencia de {nombre}', Area.TipoArea.GERENCIA, municipal)
            for dependencia in dependencias:
                guardar(f'Subgerencia de {dependencia}', Area.TipoArea.SUBGERENCIA, gerencia)
        for nombre in ORGANOS:
            guardar(nombre, Area.TipoArea.ORGANO, municipalidad)

        desactivadas = Area.objects.filter(nombre__in=AREAS_EJEMPLO, activo=True).update(activo=False)
        self.stdout.write(self.style.SUCCESS(
            f'Estructura de Huarmey cargada: 42 áreas; {desactivadas} áreas de ejemplo desactivadas. '
            'Se conservaron los documentos, las derivaciones y las asignaciones anteriores.'
        ))
