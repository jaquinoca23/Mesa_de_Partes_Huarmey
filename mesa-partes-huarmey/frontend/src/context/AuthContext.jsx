import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { cerrarSesion, iniciarSesion, obtenerSesion } from '../services/api.js';

const AuthContext = createContext(null);

// Guarda quién tiene la sesión iniciada. OJO: esto solo sirve para armar el menú.
// La seguridad real (permisos) la aplica siempre el servidor Django en cada petición.
export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let activo = true;
    obtenerSesion()
      .then((u) => activo && setUsuario(u))
      .catch(() => activo && setUsuario(null))
      .finally(() => activo && setCargando(false));
    return () => {
      activo = false;
    };
  }, []);

  const entrar = useCallback(async (username, password) => {
    const u = await iniciarSesion(username, password);
    setUsuario(u);
    return u;
  }, []);

  const salir = useCallback(async () => {
    try {
      await cerrarSesion();
    } finally {
      setUsuario(null);
    }
  }, []);

  const tiene = useCallback((permiso) => Boolean(usuario && (usuario.es_superusuario || usuario.permisos.includes(permiso))), [usuario]);

  const valor = useMemo(() => ({ usuario, cargando, entrar, salir, tiene }), [usuario, cargando, entrar, salir, tiene]);
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error('useAuth debe usarse dentro de <AuthProvider>.');
  return contexto;
}
