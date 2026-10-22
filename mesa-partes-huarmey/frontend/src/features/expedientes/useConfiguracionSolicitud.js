import { useCallback, useEffect, useState } from 'react';
import { getConfiguracionSolicitud, getTiposDocumentales } from '../../services/api.js';

/**
 * Carga desde el servidor lo que necesita el formulario:
 * los límites de archivos/opciones y la lista de tipos de documento.
 * Devuelve { cargando, error, config, tipos, recargar }.
 */
export default function useConfiguracionSolicitud() {
  const [estado, setEstado] = useState({ cargando: true, error: '', config: null, tipos: [] });
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let cancelado = false;
    setEstado({ cargando: true, error: '', config: null, tipos: [] });

    Promise.all([getConfiguracionSolicitud(), getTiposDocumentales()])
      .then(([config, tipos]) => {
        if (!cancelado) setEstado({ cargando: false, error: '', config, tipos });
      })
      .catch((error) => {
        if (!cancelado) {
          setEstado({
            cargando: false,
            error: error.message || 'No se pudo cargar el formulario.',
            config: null,
            tipos: [],
          });
        }
      });

    // Si el componente desaparece antes de terminar, se ignora el resultado.
    return () => {
      cancelado = true;
    };
  }, [intento]);

  const recargar = useCallback(() => setIntento((n) => n + 1), []);

  return { ...estado, recargar };
}
