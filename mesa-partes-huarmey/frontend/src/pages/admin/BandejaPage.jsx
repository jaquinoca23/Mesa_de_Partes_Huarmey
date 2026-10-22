import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';
import { formatearFecha } from '../../utils/formato.js';

const FILTROS_VACIOS = { q: '', estado: '', tipo: '', area: '', pendientes: false, desde: '', hasta: '' };

function aConsulta(filtros, pagina) {
  const p = new URLSearchParams();
  Object.entries(filtros).forEach(([k, v]) => {
    if (v === false || v === '') return;
    p.set(k, v === true ? '1' : v);
  });
  p.set('page', String(pagina));
  return p.toString();
}

// Bandeja: lista de expedientes que el usuario puede ver (el servidor aplica la regla por área).
export default function BandejaPage() {
  const opciones = useCarga(useCallback(() => api.get('/panel/expedientes/opciones/'), []));
  const [formulario, setFormulario] = useState(FILTROS_VACIOS);
  const [filtros, setFiltros] = useState(FILTROS_VACIOS);
  const [pagina, setPagina] = useState(1);

  const lista = useCarga(useCallback(() => api.get(`/panel/expedientes/?${aConsulta(filtros, pagina)}`), [filtros, pagina]));

  function cambiar(e) {
    const { name, value, type, checked } = e.target;
    setFormulario((previo) => ({ ...previo, [name]: type === 'checkbox' ? checked : value }));
  }

  function buscar(e) {
    e.preventDefault();
    setPagina(1);
    setFiltros(formulario);
  }

  function limpiar() {
    setFormulario(FILTROS_VACIOS);
    setFiltros(FILTROS_VACIOS);
    setPagina(1);
  }

  const op = opciones.datos;
  const total = lista.datos ? lista.datos.count : 0;
  const hayAnterior = lista.datos && lista.datos.previous;
  const haySiguiente = lista.datos && lista.datos.next;

  return (
    <section>
      <h1 className="page-title">Bandeja de expedientes</h1>
      <p className="state-msg">Solo ves los expedientes de tu área, o todos si tu rol lo permite.</p>

      <form onSubmit={buscar} className="card form-section" aria-label="Filtros">
        <div className="form-grid">
          <FormField id="q" label="Buscar" hint="Número, asunto o solicitante" value={formulario.q} onChange={cambiar} maxLength={100} />
          <FormField id="estado" as="select" label="Estado" value={formulario.estado} onChange={cambiar}>
            <option value="">Todos</option>
            {op && op.estados.map((e) => <option key={e.valor} value={e.valor}>{e.etiqueta}</option>)}
          </FormField>
          <FormField id="tipo" as="select" label="Tipo de documento" value={formulario.tipo} onChange={cambiar}>
            <option value="">Todos</option>
            {op && op.tipos.map((t) => <option key={t.valor} value={t.valor}>{t.etiqueta}</option>)}
          </FormField>
          {op && op.ve_todos && (
            <FormField id="area" as="select" label="Área que lo tiene" value={formulario.area} onChange={cambiar}>
              <option value="">Todas</option>
              {op.areas.map((a) => <option key={a.valor} value={a.valor}>{a.etiqueta}</option>)}
            </FormField>
          )}
          <FormField id="desde" type="date" label="Recibido desde" value={formulario.desde} onChange={cambiar} />
          <FormField id="hasta" type="date" label="Recibido hasta" value={formulario.hasta} onChange={cambiar} />
        </div>
        <div className="check">
          <div className="check__fila">
            <input id="pendientes" name="pendientes" type="checkbox" checked={formulario.pendientes} onChange={cambiar} />
            <label htmlFor="pendientes">Solo derivaciones pendientes de recibir por mi área</label>
          </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn--primary"><Search size={18} aria-hidden="true" /> Buscar</button>
          <button type="button" className="btn btn--secondary" onClick={limpiar}>Limpiar</button>
        </div>
      </form>

      {lista.cargando && <p className="state-msg" role="status">Cargando…</p>}
      {lista.error && <p className="field__error" role="alert">{lista.error}</p>}
      {lista.datos && (
        <>
          <p className="state-msg" role="status">{total} expediente(s) encontrado(s).</p>
          <div className="tabla-envoltura">
            <table className="tabla">
              <thead>
                <tr>
                  <th scope="col">Número</th>
                  <th scope="col">Asunto</th>
                  <th scope="col">Tipo</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Área actual</th>
                  <th scope="col">Recibido</th>
                </tr>
              </thead>
              <tbody>
                {lista.datos.results.length === 0 && (
                  <tr><td colSpan={6}>No hay expedientes con esos filtros.</td></tr>
                )}
                {lista.datos.results.map((e) => (
                  <tr key={e.uuid}>
                    <td><Link to={`/panel/expedientes/${e.uuid}`}>{e.numero}</Link></td>
                    <td>
                      {e.asunto}
                      <br /><small>{e.solicitante}</small>
                    </td>
                    <td>{e.tipo_documental}</td>
                    <td>
                      {e.estado}
                      {e.por_recibir && <span className="etiqueta etiqueta--alerta">Por recibir</span>}
                      {e.derivacion_pendiente && !e.por_recibir && <span className="etiqueta">Derivación pendiente</span>}
                    </td>
                    <td>{e.area_actual || 'Mesa de partes'}</td>
                    <td>{formatearFecha(e.fecha_recepcion)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn--secondary" disabled={!hayAnterior} onClick={() => setPagina((n) => n - 1)}>Anterior</button>
            <span>Página {pagina}</span>
            <button type="button" className="btn btn--secondary" disabled={!haySiguiente} onClick={() => setPagina((n) => n + 1)}>Siguiente</button>
          </div>
        </>
      )}
    </section>
  );
}
