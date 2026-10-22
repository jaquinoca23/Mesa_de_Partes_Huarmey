import { useState } from 'react';
import { Loader2, Search } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import CargoRecepcion from '../../components/CargoRecepcion.jsx';
import { ApiError, consultarExpediente } from '../../services/api.js';
import { formatearFecha } from '../../utils/formato.js';

// Consulta pública: necesita el número Y el código de verificación.
export default function ConsultarPage() {
  const [numero, setNumero] = useState('');
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState(null);

  async function consultar(evento) {
    evento.preventDefault();
    setError('');
    setResultado(null);
    if (!numero.trim() || !codigo.trim()) {
      setError('Ingresa el número de expediente y el código de verificación.');
      return;
    }
    setCargando(true);
    try {
      setResultado(await consultarExpediente(numero.trim(), codigo.trim()));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Ocurrió un error inesperado. Inténtalo de nuevo.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="section">
      <div className="container container--form">
        <h1 className="page-title">Consultar un expediente</h1>
        <p className="page-lead">Ingresa el número de expediente y el código de verificación de tu cargo.</p>

        <form onSubmit={consultar} noValidate className="card form-section">
          <div className="form-grid">
            <FormField
              id="numero"
              label="Número de expediente"
              required
              hint="Ejemplo: 2026-000001"
              value={numero}
              onChange={(e) => setNumero(e.target.value)}
              maxLength={20}
              autoComplete="off"
            />
            <FormField
              id="codigo"
              label="Código de verificación"
              required
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              maxLength={12}
              autoComplete="off"
            />
          </div>
          {error && (
            <p className="field__error" role="alert">
              {error}
            </p>
          )}
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={cargando}>
              {cargando ? <Loader2 size={18} aria-hidden="true" className="spin" /> : <Search size={18} aria-hidden="true" />}
              {cargando ? 'Consultando…' : 'Consultar'}
            </button>
          </div>
        </form>

        {resultado && (
          <div className="card form-section" role="status">
            <h2 className="form-section__title">Estado actual: {resultado.estado}</h2>
            {resultado.estado_descripcion && <p>{resultado.estado_descripcion}</p>}
            <h3 className="form-section__subtitle">Historial</h3>
            <ol className="historial">
              {resultado.historial.map((h) => (
                <li key={h.fecha + h.estado}>
                  <strong>{h.estado}</strong> — {formatearFecha(h.fecha)}
                </li>
              ))}
            </ol>
            <CargoRecepcion cargo={resultado.cargo} />
            <div className="result__acciones no-imprimir">
              <button type="button" className="btn btn--secondary" onClick={() => window.print()}>
                Imprimir
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
