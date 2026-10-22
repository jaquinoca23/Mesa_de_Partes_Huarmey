import { useCallback, useState } from 'react';
import FormField from '../../components/FormField.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';
import { formatearFecha } from '../../utils/formato.js';

const VACIO = { accion: '', desde: '', hasta: '' };

// Bitácora de acciones importantes. Es de solo lectura: nadie puede modificarla ni borrarla.
export default function AuditoriaPage() {
  const acciones = useCarga(useCallback(() => api.get('/panel/auditoria/acciones/'), []));
  const [formulario, setFormulario] = useState(VACIO);
  const [filtros, setFiltros] = useState(VACIO);
  const [pagina, setPagina] = useState(1);
  const lista = useCarga(
    useCallback(() => {
      const p = new URLSearchParams();
      Object.entries(filtros).forEach(([k, v]) => v && p.set(k, v));
      p.set('page', String(pagina));
      return api.get(`/panel/auditoria/?${p.toString()}`);
    }, [filtros, pagina]),
  );

  function cambiar(e) {
    setFormulario((previo) => ({ ...previo, [e.target.name]: e.target.value }));
  }

  return (
    <section>
      <h1 className="page-title">Auditoría</h1>
      <p className="state-msg">Registro de accesos y acciones importantes. Solo lectura.</p>
      <form
        className="card form-section"
        onSubmit={(e) => {
          e.preventDefault();
          setPagina(1);
          setFiltros(formulario);
        }}
      >
        <div className="form-grid">
          <FormField id="accion" as="select" label="Acción" value={formulario.accion} onChange={cambiar}>
            <option value="">Todas</option>
            {acciones.datos && acciones.datos.map((a) => <option key={a.valor} value={a.valor}>{a.etiqueta}</option>)}
          </FormField>
          <FormField id="desde" type="date" label="Desde" value={formulario.desde} onChange={cambiar} />
          <FormField id="hasta" type="date" label="Hasta" value={formulario.hasta} onChange={cambiar} />
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn--primary">Filtrar</button>
          <button type="button" className="btn btn--secondary" onClick={() => { setFormulario(VACIO); setFiltros(VACIO); setPagina(1); }}>Limpiar</button>
        </div>
      </form>

      {lista.cargando && <p className="state-msg" role="status">Cargando…</p>}
      {lista.error && <p className="field__error" role="alert">{lista.error}</p>}
      {lista.datos && (
        <>
          <div className="tabla-envoltura">
            <table className="tabla">
              <thead>
                <tr><th scope="col">Fecha</th><th scope="col">Usuario</th><th scope="col">Acción</th><th scope="col">Objeto</th><th scope="col">Detalle</th><th scope="col">IP</th></tr>
              </thead>
              <tbody>
                {lista.datos.results.length === 0 && <tr><td colSpan={6}>Sin registros.</td></tr>}
                {lista.datos.results.map((r) => (
                  <tr key={r.fecha + r.accion + r.objeto + r.detalle}>
                    <td>{formatearFecha(r.fecha)}</td>
                    <td>{r.usuario}</td>
                    <td>{r.accion}</td>
                    <td>{r.objeto || '—'}</td>
                    <td>{r.detalle || '—'}</td>
                    <td>{r.ip || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn--secondary" disabled={!lista.datos.previous} onClick={() => setPagina((n) => n - 1)}>Anterior</button>
            <span>Página {pagina} · {lista.datos.count} registro(s)</span>
            <button type="button" className="btn btn--secondary" disabled={!lista.datos.next} onClick={() => setPagina((n) => n + 1)}>Siguiente</button>
          </div>
        </>
      )}
    </section>
  );
}
