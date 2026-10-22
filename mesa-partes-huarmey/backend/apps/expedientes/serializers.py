import re

from rest_framework import serializers

from apps.catalogos.models import TipoDocumental

from .models import Solicitante

# Reglas PROVISIONALES de formato del documento de identidad (por validar con la municipalidad).
# DNI (8 dígitos) y RUC (11 dígitos) tienen formato fijo; para carné de extranjería y
# pasaporte se acepta un rango razonable de letras y números.
REGLAS_DOCUMENTO_IDENTIDAD = {
    'DNI': (re.compile(r'^\d{8}$'), 'El DNI debe tener 8 dígitos.'),
    'RUC': (re.compile(r'^\d{11}$'), 'El RUC debe tener 11 dígitos.'),
    'CE': (re.compile(r'^[A-Z0-9]{8,12}$'), 'El carné de extranjería debe tener entre 8 y 12 letras o números.'),
    'PASAPORTE': (re.compile(r'^[A-Z0-9]{6,12}$'), 'El pasaporte debe tener entre 6 y 12 letras o números.'),
}
PATRON_TELEFONO = re.compile(r'^[0-9+\-\s()]{6,20}$')

OBLIGATORIO = 'Este campo es obligatorio.'
MENSAJES_BASE = {'required': OBLIGATORIO, 'null': OBLIGATORIO, 'blank': OBLIGATORIO}
MENSAJES_TEXTO = {
    **MENSAJES_BASE,
    'min_length': 'Escribe al menos {min_length} caracteres.',
    'max_length': 'No puede superar los {max_length} caracteres.',
}
MENSAJES_OPCION = {**MENSAJES_BASE, 'invalid_choice': 'Selecciona una opción válida.'}


class SolicitudSerializer(serializers.Serializer):
    """
    Reglas de validación de una solicitud de mesa de partes (datos de texto).
    Los archivos adjuntos se validan aparte (apps/documentos).

    El servidor es quien manda: aunque React ya valide, aquí se vuelve a comprobar todo.
    """

    # Identifica un envío del formulario; la ETAPA 5 la usará para impedir envíos duplicados.
    clave_envio = serializers.UUIDField(
        error_messages={**MENSAJES_BASE, 'invalid': 'La clave de envío no es válida.'}
    )
    tipo_persona = serializers.ChoiceField(
        choices=Solicitante.TipoPersona.choices, error_messages=MENSAJES_OPCION
    )
    tipo_documento_identidad = serializers.ChoiceField(
        choices=Solicitante.TipoDocumentoIdentidad.choices, error_messages=MENSAJES_OPCION
    )
    numero_documento = serializers.CharField(max_length=20, error_messages=MENSAJES_TEXTO)
    nombres = serializers.CharField(
        max_length=150, required=False, allow_blank=True, error_messages=MENSAJES_TEXTO
    )
    apellidos = serializers.CharField(
        max_length=150, required=False, allow_blank=True, error_messages=MENSAJES_TEXTO
    )
    razon_social = serializers.CharField(
        max_length=200, required=False, allow_blank=True, error_messages=MENSAJES_TEXTO
    )
    email = serializers.EmailField(
        max_length=254, error_messages={**MENSAJES_TEXTO, 'invalid': 'Ingresa un correo electrónico válido.'}
    )
    telefono = serializers.CharField(
        max_length=20, required=False, allow_blank=True, error_messages=MENSAJES_TEXTO
    )
    # Se elige por su código; solo se aceptan tipos activos.
    tipo_documental = serializers.SlugRelatedField(
        slug_field='codigo',
        queryset=TipoDocumental.objects.filter(activo=True),
        error_messages={
            **MENSAJES_BASE,
            'does_not_exist': 'El tipo de documento seleccionado no es válido.',
            'invalid': 'El tipo de documento seleccionado no es válido.',
        },
    )
    asunto = serializers.CharField(max_length=300, min_length=5, error_messages=MENSAJES_TEXTO)
    descripcion = serializers.CharField(
        max_length=5000, required=False, allow_blank=True, error_messages=MENSAJES_TEXTO
    )
    acepta_politica_privacidad = serializers.BooleanField(error_messages=MENSAJES_BASE)
    declara_veracidad = serializers.BooleanField(error_messages=MENSAJES_BASE)

    def validate_telefono(self, valor):
        if valor and not PATRON_TELEFONO.match(valor):
            raise serializers.ValidationError(
                'Ingresa un teléfono válido (entre 6 y 20 caracteres: números, espacios y + - ( ) ).'
            )
        return valor

    def validate_acepta_politica_privacidad(self, valor):
        if not valor:
            raise serializers.ValidationError('Debes aceptar la política de privacidad.')
        return valor

    def validate_declara_veracidad(self, valor):
        if not valor:
            raise serializers.ValidationError('Debes marcar la declaración de veracidad.')
        return valor

    def validate(self, datos):
        """Reglas que dependen de varios campos a la vez."""
        errores = {}

        tipo_documento = datos['tipo_documento_identidad']
        numero = datos['numero_documento'].replace(' ', '').upper()
        patron, mensaje = REGLAS_DOCUMENTO_IDENTIDAD[tipo_documento]
        if patron.match(numero):
            datos['numero_documento'] = numero
        else:
            errores['numero_documento'] = mensaje

        if datos['tipo_persona'] == Solicitante.TipoPersona.NATURAL:
            if not datos.get('nombres'):
                errores['nombres'] = OBLIGATORIO
            if not datos.get('apellidos'):
                errores['apellidos'] = OBLIGATORIO
        else:
            if not datos.get('razon_social'):
                errores['razon_social'] = OBLIGATORIO
            if tipo_documento != Solicitante.TipoDocumentoIdentidad.RUC:
                errores['tipo_documento_identidad'] = 'Una persona jurídica debe identificarse con RUC.'

        if errores:
            raise serializers.ValidationError(errores)
        return datos
