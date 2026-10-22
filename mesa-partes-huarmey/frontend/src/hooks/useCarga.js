import { useCallback, useEffect, useState } from 'react';

// Ejecuta una función asíncrona al abrir la pantalla y controla "cargando" y "error".
export default function useCarga(funcion) {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);

  const cargar = useCallback(async () => {
    setCargando(true);
    setError('');
    try {
      setDatos(await funcion());
    } catch (e) {
      setError(e.message || 'No se pudo cargar la información.');
    } finally {
      setCargando(false);
    }
  }, [funcion]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  return { datos, error, cargando, recargar: cargar };
}
