// Guarda el cargo SOLO en la pestaña actual (sessionStorage): se borra al cerrar la pestaña.
// Así no queda el código de verificación guardado de forma permanente en el navegador.
const CLAVE = 'mesa-partes:ultimo-cargo';

export function guardarCargo(cargo) {
  try {
    sessionStorage.setItem(CLAVE, JSON.stringify(cargo));
  } catch {
    // Si el navegador no permite guardar, el cargo se pierde al recargar; el ciudadano también lo recibe por correo.
  }
}

export function leerCargo() {
  try {
    const texto = sessionStorage.getItem(CLAVE);
    return texto ? JSON.parse(texto) : null;
  } catch {
    return null;
  }
}

export function borrarCargo() {
  try {
    sessionStorage.removeItem(CLAVE);
  } catch {
    // sin acción
  }
}
