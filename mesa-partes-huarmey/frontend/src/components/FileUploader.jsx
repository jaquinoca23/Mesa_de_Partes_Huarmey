import { useRef } from 'react';
import { Paperclip, X } from 'lucide-react';
import { formatearTamano } from '../utils/validaciones.js';

// Identifica un archivo para no agregarlo dos veces.
const claveDe = (archivo) => `${archivo.name}|${archivo.size}|${archivo.lastModified}`;

/**
 * Selector de archivos adjuntos (opcionales) con lista y botón para quitar cada uno.
 * - archivos: lista actual (File[]); onChange recibe la lista nueva.
 * - config: límites que entrega el servidor.
 * - errores: lista de mensajes (o vacío).
 */
export default function FileUploader({ id, archivos, onChange, config, errores = [] }) {
  const entradaRef = useRef(null);
  const { extensiones_permitidas: permitidas, max_archivos: maxArchivos, max_tamano_mb: maxMb } = config.archivos;
  const lista = Array.isArray(errores) ? errores : errores ? [errores] : [];
  const idAyuda = `${id}-ayuda`;
  const idError = `${id}-error`;

  function alElegir(evento) {
    const elegidos = Array.from(evento.target.files || []);
    const yaAgregados = new Set(archivos.map(claveDe));
    const nuevos = elegidos.filter((archivo) => !yaAgregados.has(claveDe(archivo)));
    onChange([...archivos, ...nuevos]);
    // Se vacía la selección del navegador para poder elegir el mismo archivo otra vez.
    evento.target.value = '';
  }

  function quitar(indice) {
    onChange(archivos.filter((_, i) => i !== indice));
  }

  return (
    <div className={`field${lista.length > 0 ? ' field--error' : ''}`}>
      <label htmlFor={id} className="field__label">
        Documentos adjuntos <span className="field__optional">(opcional)</span>
      </label>
      <p id={idAyuda} className="field__hint">
        Hasta {maxArchivos} archivos de {maxMb} MB cada uno. Tipos permitidos:{' '}
        {permitidas.map((e) => e.toUpperCase()).join(', ')}.
      </p>
      <input
        ref={entradaRef}
        id={id}
        name={id}
        type="file"
        multiple
        accept={permitidas.map((e) => `.${e}`).join(',')}
        onChange={alElegir}
        className="file-input"
        aria-describedby={lista.length > 0 ? `${idAyuda} ${idError}` : idAyuda}
        aria-invalid={lista.length > 0 ? 'true' : undefined}
      />

      {archivos.length > 0 && (
        <ul className="file-list">
          {archivos.map((archivo, indice) => (
            <li key={claveDe(archivo)} className="file-list__item">
              <Paperclip size={16} aria-hidden="true" />
              <span className="file-list__name">{archivo.name}</span>
              <span className="file-list__size">{formatearTamano(archivo.size)}</span>
              <button
                type="button"
                className="icon-btn"
                onClick={() => quitar(indice)}
                aria-label={`Quitar ${archivo.name}`}
              >
                <X size={16} aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {lista.length > 0 && (
        <ul id={idError} className="field__error file-errors">
          {lista.map((mensaje) => (
            <li key={mensaje}>{mensaje}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
