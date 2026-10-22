// Fecha y hora en hora de Lima, con formato legible.
export function formatearFecha(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    dateStyle: 'long',
    timeStyle: 'medium',
  });
}

export function formatearTamano(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
