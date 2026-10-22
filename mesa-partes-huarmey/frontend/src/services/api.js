// Cliente para hablar con la API de Django.
// En desarrollo, Vite reenvía "/api" a http://127.0.0.1:8000 (ver vite.config.js).

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/** Error de la API. Si el servidor rechazó los datos (código 400), "errores" trae el detalle por campo. */
export class ApiError extends Error {
  constructor(mensaje, { status = 0, errores = null } = {}) {
    super(mensaje);
    this.name = 'ApiError';
    this.status = status;
    this.errores = errores;
  }
}

// Lee una cookie por nombre (se usa para el token CSRF que entrega Django).
function leerCookie(nombre) {
  const par = document.cookie.split('; ').find((c) => c.startsWith(`${nombre}=`));
  return par ? decodeURIComponent(par.split('=')[1]) : '';
}

// Función base: hace la petición y convierte los fallos en ApiError con mensajes comprensibles.
async function solicitar(ruta, opciones = {}) {
  const metodo = (opciones.method || 'GET').toUpperCase();
  const cabeceras = { Accept: 'application/json', ...(opciones.headers || {}) };
  // Las peticiones que modifican datos llevan el token CSRF (protege la sesión del personal).
  if (!['GET', 'HEAD', 'OPTIONS'].includes(metodo)) {
    const token = leerCookie('csrftoken');
    if (token) cabeceras['X-CSRFToken'] = token;
  }
  let respuesta;
  try {
    respuesta = await fetch(`${API_BASE_URL}${ruta}`, {
      credentials: 'same-origin',
      ...opciones,
      headers: cabeceras,
    });
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Verifica tu conexión e inténtalo de nuevo.');
  }

  let datos = null;
  try {
    datos = await respuesta.json();
  } catch {
    // La respuesta no traía JSON; se maneja más abajo según el código.
  }

  if (!respuesta.ok) {
    if (respuesta.status === 400 && datos && datos.errores) {
      throw new ApiError(datos.mensaje || 'Revisa los datos ingresados.', {
        status: 400,
        errores: datos.errores,
      });
    }
    // Errores de validación del panel (Django REST Framework): { campo: ["mensaje"] }.
    if (respuesta.status === 400 && datos && typeof datos === 'object' && !datos.mensaje && !Array.isArray(datos)) {
      throw new ApiError('Revisa los datos ingresados.', { status: 400, errores: datos });
    }
    if (respuesta.status === 404 && !(datos && datos.mensaje)) {
      throw new ApiError('No se encontró el registro, o no tienes acceso a él.', { status: 404 });
    }
    if (respuesta.status === 403 && !(datos && datos.mensaje)) {
      throw new ApiError('No tienes permiso para realizar esta acción.', { status: 403 });
    }
    if (respuesta.status === 429) {
      throw new ApiError('Has realizado demasiados intentos. Espera un momento e inténtalo de nuevo.', {
        status: 429,
      });
    }
    // Si el servidor explica el problema en "mensaje", se muestra tal cual.
    const mensaje =
      datos && typeof datos.mensaje === 'string'
        ? datos.mensaje
        : `El servidor no pudo procesar la solicitud (código ${respuesta.status}).`;
    throw new ApiError(mensaje, { status: respuesta.status });
  }
  return datos;
}

/** GET /api/health/ -> { status, service, version, server_time } */
export function getHealth() {
  return solicitar('/health/');
}

/** GET /api/solicitudes/configuracion/ -> límites de archivos y opciones del formulario */
export function getConfiguracionSolicitud() {
  return solicitar('/solicitudes/configuracion/');
}

/** GET /api/catalogos/tipos-documentales/ -> [{ codigo, nombre, descripcion }] */
export function getTiposDocumentales() {
  return solicitar('/catalogos/tipos-documentales/');
}

/**
 * POST /api/solicitudes/validar/ (ETAPA 4: el servidor solo verifica, NO registra).
 * Recibe un FormData (texto + archivos). No se fija Content-Type: el navegador lo hace solo.
 */
export function verificarSolicitud(formData) {
  return solicitar('/solicitudes/validar/', { method: 'POST', body: formData });
}

/**
 * POST /api/solicitudes/ (ETAPA 5): registra la solicitud.
 * Devuelve { registrado, duplicado, cargo }. Solo si "registrado" es true existe el expediente.
 */
export function registrarSolicitud(formData) {
  return solicitar('/solicitudes/', { method: 'POST', body: formData });
}

/** POST /api/seguimiento/consultar/ -> datos y historial del expediente (404 si no coincide). */
export function consultarExpediente(numero, codigo) {
  return solicitar('/seguimiento/consultar/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ numero, codigo }),
  });
}

// ---------- Sesión del personal (ETAPA 6) ----------

/** GET /api/auth/csrf/ -> deja la cookie CSRF lista en el navegador. */
export function obtenerCsrf() {
  return solicitar('/auth/csrf/');
}

/** POST /api/auth/login/ -> { usuario } o ApiError con mensaje genérico. */
export async function iniciarSesion(username, password) {
  await obtenerCsrf();
  const datos = await enviarJson('/auth/login/', 'POST', { username, password });
  return datos.usuario;
}

/** POST /api/auth/logout/ */
export function cerrarSesion() {
  return solicitar('/auth/logout/', { method: 'POST' });
}

/** GET /api/auth/me/ -> usuario, o null si no hay sesión. */
export async function obtenerSesion() {
  try {
    const datos = await solicitar('/auth/me/');
    return datos.usuario;
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) return null;
    throw error;
  }
}

// ---------- Llamadas JSON genéricas del panel ----------

function enviarJson(ruta, metodo, cuerpo) {
  return solicitar(ruta, {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cuerpo),
  });
}

export const api = {
  get: (ruta) => solicitar(ruta),
  post: (ruta, cuerpo) => enviarJson(ruta, 'POST', cuerpo),
  patch: (ruta, cuerpo) => enviarJson(ruta, 'PATCH', cuerpo),
};

/** GET /api/identidad/dni/<dni>/ -> { nombres, apellidos }. Solo ayuda a completar el formulario. */
export function consultarDni(dni) {
  return solicitar(`/identidad/dni/${encodeURIComponent(dni)}/`);
}
