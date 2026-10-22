import { useEffect, useState } from 'react';
import { getHealth } from '../services/api.js';

/**
 * Indicador de diagnóstico: muestra si React logra comunicarse con Django.
 * Solo se ve durante el desarrollo (npm run dev); no aparece en la versión compilada.
 */
export default function BackendStatus() {
  const [estado, setEstado] = useState('comprobando'); // comprobando | ok | error

  useEffect(() => {
    let cancelado = false;
    getHealth()
      .then((datos) => {
        if (!cancelado) setEstado(datos.status === 'ok' ? 'ok' : 'error');
      })
      .catch(() => {
        if (!cancelado) setEstado('error');
      });
    return () => {
      cancelado = true;
    };
  }, []);

  if (!import.meta.env.DEV) return null;

  const textos = {
    comprobando: 'Comprobando conexión con el backend…',
    ok: 'Backend conectado',
    error: 'Backend no disponible (¿está corriendo Django?)',
  };

  return (
    <p className={`backend-status backend-status--${estado}`} role="status">
      <span className="backend-status__dot" aria-hidden="true" />
      Diagnóstico de desarrollo: {textos[estado]}
    </p>
  );
}
