import { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';

// Tarjetas con los números clave, calculados por el servidor sobre lo que ESTE usuario puede ver.
function Resumen() {
  const { datos, cargando, error } = useCarga(useCallback(() => api.get('/panel/dashboard/'), []));
  if (cargando) return <p className="state-msg" role="status">Cargando resumen…</p>;
  if (error) return <p className="field__error" role="alert">{error}</p>;
  return (
    <>
      <div className="tarjetas">
        <div className="tarjeta">
          <span className="tarjeta__numero">{datos.total}</span>
          <span>Expedientes visibles</span>
        </div>
        <div className="tarjeta tarjeta--alerta">
          <span className="tarjeta__numero">{datos.por_recibir}</span>
          <span>Por recibir en mi área</span>
          {datos.por_recibir > 0 && <Link to="/panel/expedientes">Ir a la bandeja</Link>}
        </div>
        {datos.por_estado.map((e) => (
          <div className="tarjeta" key={e.nombre}>
            <span className="tarjeta__numero">{e.total}</span>
            <span>{e.nombre}</span>
          </div>
        ))}
      </div>
      <h2 className="form-section__subtitle">Últimos expedientes</h2>
      {datos.recientes.length === 0 ? (
        <p>No hay expedientes para mostrar.</p>
      ) : (
        <ul>
          {datos.recientes.map((e) => (
            <li key={e.uuid}>
              <Link to={`/panel/expedientes/${e.uuid}`}>{e.numero}</Link> — {e.asunto} ({e.estado})
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default function InicioPanelPage() {
  const { usuario, tiene } = useAuth();
  return (
    <section>
      <h1 className="page-title">Bienvenido, {usuario.nombre}</h1>
      <dl className="result__datos">
        <dt>Roles</dt>
        <dd>{usuario.roles.length ? usuario.roles.join(', ') : 'Sin rol asignado'}</dd>
        <dt>Área</dt>
        <dd>{usuario.area ? usuario.area.nombre : 'Sin área asignada'}</dd>
        <dt>Cargo</dt>
        <dd>{usuario.cargo || '—'}</dd>
      </dl>
      {tiene('expedientes.view_expediente') && <Resumen />}
    </section>
  );
}
