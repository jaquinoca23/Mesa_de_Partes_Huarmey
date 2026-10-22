import { TriangleAlert } from 'lucide-react';
import FormularioSolicitud from '../../features/expedientes/FormularioSolicitud.jsx';
import useConfiguracionSolicitud from '../../features/expedientes/useConfiguracionSolicitud.js';

// Página "Presentar un documento": carga la configuración del servidor y muestra el formulario.
export default function PresentarPage() {
  const { cargando, error, config, tipos, recargar } = useConfiguracionSolicitud();

  return (
    <section className="section">
      <div className="container container--form">
        <h1 className="page-title">Presentar un documento</h1>
        <p className="page-lead">Completa el formulario. Los campos marcados con * son obligatorios.</p>

        {cargando && (
          <p className="state-msg" role="status">
            Cargando formulario…
          </p>
        )}

        {error && (
          <div className="notice notice--error" role="alert">
            <TriangleAlert size={22} aria-hidden="true" className="notice__icon" />
            <div>
              <h2 className="notice__title">No se pudo cargar el formulario</h2>
              <p>{error}</p>
              {import.meta.env.DEV && (
                <p className="state-msg">
                  (Desarrollo: comprueba que Django esté encendido y que hayas ejecutado{' '}
                  <code>python manage.py cargar_datos_ficticios</code>.)
                </p>
              )}
              <button type="button" className="btn btn--primary" onClick={recargar}>
                Reintentar
              </button>
            </div>
          </div>
        )}

        {config && <FormularioSolicitud config={config} tipos={tipos} />}
      </div>
    </section>
  );
}
