import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

// Protege las pantallas del panel. Si no hay sesión, envía al inicio de sesión.
// Si se indica "permiso", además exige ese permiso (el servidor lo vuelve a comprobar siempre).
export default function RutaProtegida({ permiso }) {
  const { usuario, cargando, tiene } = useAuth();
  const ubicacion = useLocation();

  if (cargando) return <p className="state-msg" role="status">Verificando sesión…</p>;
  if (!usuario) return <Navigate to="/panel/login" replace state={{ desde: ubicacion.pathname }} />;
  if (permiso && !tiene(permiso)) {
    return (
      <div className="notice notice--error" role="alert">
        <div>
          <h2 className="notice__title">Sin permiso</h2>
          <p>Tu rol no tiene acceso a esta sección.</p>
        </div>
      </div>
    );
  }
  return <Outlet />;
}
