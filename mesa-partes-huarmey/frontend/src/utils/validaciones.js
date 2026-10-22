// Validaciones del formulario en el navegador.
// Sirven para dar respuesta rápida al ciudadano, pero NO son la seguridad real:
// el servidor (Django) vuelve a validar todo y tiene la última palabra.
// Estas reglas deben mantenerse iguales a las de backend/apps/expedientes/serializers.py.

export const REGLAS_DOCUMENTO = {
  DNI: { patron: /^\d{8}$/, mensaje: 'El DNI debe tener 8 dígitos.' },
  RUC: { patron: /^\d{11}$/, mensaje: 'El RUC debe tener 11 dígitos.' },
  CE: {
    patron: /^[A-Za-z0-9]{8,12}$/,
    mensaje: 'El carné de extranjería debe tener entre 8 y 12 letras o números.',
  },
  PASAPORTE: {
    patron: /^[A-Za-z0-9]{6,12}$/,
    mensaje: 'El pasaporte debe tener entre 6 y 12 letras o números.',
  },
};

const PATRON_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PATRON_TELEFONO = /^[0-9+\-\s()]{6,20}$/;
const OBLIGATORIO = 'Este campo es obligatorio.';

/** Devuelve la extensión en minúsculas ("Informe.PDF" -> "pdf"). Vacío si no tiene. */
export function extensionDe(nombre) {
  const posicion = nombre.lastIndexOf('.');
  return posicion === -1 ? '' : nombre.slice(posicion + 1).toLowerCase();
}

/** Convierte bytes en texto legible ("2.5 MB"). */
export function formatearTamano(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Revisa un archivo según los límites que entrega el servidor. Devuelve un mensaje o null. */
export function validarArchivo(archivo, config) {
  const { extensiones_permitidas: permitidas, max_tamano_mb: maxMb } = config.archivos;
  if (!permitidas.includes(extensionDe(archivo.name))) {
    const lista = permitidas.map((e) => e.toUpperCase()).join(', ');
    return `${archivo.name}: tipo de archivo no permitido. Permitidos: ${lista}.`;
  }
  if (archivo.size === 0) return `${archivo.name}: el archivo está vacío.`;
  if (archivo.size > maxMb * 1024 * 1024) return `${archivo.name}: supera el tamaño máximo de ${maxMb} MB.`;
  return null;
}

/** Revisa la lista completa de archivos. Devuelve una lista de mensajes (vacía si todo está bien). */
export function validarArchivos(archivos, config) {
  const errores = [];
  const maximo = config.archivos.max_archivos;
  if (archivos.length > maximo) {
    errores.push(`Puedes adjuntar como máximo ${maximo} archivos (seleccionaste ${archivos.length}).`);
  }
  archivos.forEach((archivo) => {
    const mensaje = validarArchivo(archivo, config);
    if (mensaje) errores.push(mensaje);
  });
  return errores;
}

/**
 * Revisa todo el formulario. Devuelve un objeto { campo: mensaje }.
 * Si está vacío, no hay errores. Para "archivos" el valor es una lista de mensajes.
 */
export function validarSolicitud(valores, archivos, config) {
  const errores = {};
  const texto = (campo) => String(valores[campo] ?? '').trim();

  // Documento de identidad
  const numero = texto('numero_documento').replace(/\s/g, '');
  const regla = REGLAS_DOCUMENTO[valores.tipo_documento_identidad];
  if (!numero) {
    errores.numero_documento = OBLIGATORIO;
  } else if (regla && !regla.patron.test(numero)) {
    errores.numero_documento = regla.mensaje;
  }

  // Datos según el tipo de solicitante
  if (valores.tipo_persona === 'JURIDICA') {
    if (valores.tipo_documento_identidad !== 'RUC') {
      errores.tipo_documento_identidad = 'Una persona jurídica debe identificarse con RUC.';
    }
    if (!texto('razon_social')) errores.razon_social = OBLIGATORIO;
  } else {
    if (!texto('nombres')) errores.nombres = OBLIGATORIO;
    if (!texto('apellidos')) errores.apellidos = OBLIGATORIO;
  }

  // Contacto
  if (!texto('email')) {
    errores.email = OBLIGATORIO;
  } else if (!PATRON_EMAIL.test(texto('email'))) {
    errores.email = 'Ingresa un correo electrónico válido.';
  }
  if (texto('telefono') && !PATRON_TELEFONO.test(texto('telefono'))) {
    errores.telefono = 'Ingresa un teléfono válido (entre 6 y 20 caracteres: números, espacios y + - ( ) ).';
  }

  // Documento que se presenta
  if (!texto('tipo_documental')) errores.tipo_documental = 'Selecciona el tipo de documento.';
  if (!texto('asunto')) {
    errores.asunto = OBLIGATORIO;
  } else if (texto('asunto').length < 5) {
    errores.asunto = 'Escribe al menos 5 caracteres.';
  } else if (texto('asunto').length > 300) {
    errores.asunto = 'No puede superar los 300 caracteres.';
  }
  if (texto('descripcion').length > 5000) errores.descripcion = 'No puede superar los 5000 caracteres.';

  // Archivos y declaraciones
  const erroresArchivos = validarArchivos(archivos, config);
  if (erroresArchivos.length > 0) errores.archivos = erroresArchivos;
  if (!valores.acepta_politica_privacidad) {
    errores.acepta_politica_privacidad = 'Debes aceptar la política de privacidad.';
  }
  if (!valores.declara_veracidad) {
    errores.declara_veracidad = 'Debes marcar la declaración de veracidad.';
  }

  return errores;
}
