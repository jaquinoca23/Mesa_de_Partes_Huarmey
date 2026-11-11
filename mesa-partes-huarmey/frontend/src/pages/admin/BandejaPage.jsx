import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, SlidersHorizontal, Inbox, ArrowUpRight, ChevronLeft, ChevronRight, RotateCcw, FilePlus2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
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
  const { tiene } = useAuth();
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
  const filtrosActivos = Object.values(filtros).filter(Boolean).length;

  return (
    <section className="bandeja">
      <header className="bandeja__encabezado">
        <div><span className="panel-eyebrow">GESTIÓN DOCUMENTAL</span><h1>Bandeja de expedientes</h1><p>Consulta, encuentra y da seguimiento a tus documentos.</p></div>
        {tiene('expedientes.add_expediente') && <Link className="btn btn--primary" to="/panel/registrar-documento"><FilePlus2 size={18} aria-hidden="true" /> Registrar documento</Link>}
      </header>

      <form onSubmit={buscar} className="card form-section bandeja__filtros" aria-label="Filtros">
        <div className="bandeja__filtros-titulo"><h2><SlidersHorizontal size={17} aria-hidden="true" /> Buscar y filtrar</h2><span>Combina los filtros para encontrar un expediente</span></div>
        <div className="form-grid">
          <FormField id="q" label="Buscar expediente" placeholder="Número, asunto o solicitante…" value={formulario.q} onChange={cambiar} maxLength={100} />
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
        <div className="bandeja__filtros-pie"><div className="check">
          <div className="check__fila">
            <input id="pendientes" name="pendientes" type="checkbox" checked={formulario.pendientes} onChange={cambiar} />
            <label htmlFor="pendientes">Solo derivaciones pendientes de recibir por mi área</label>
          </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn--primary"><Search size={18} aria-hidden="true" /> Buscar</button>
          <button type="button" className="btn btn--secondary" onClick={limpiar}><RotateCcw size={15} aria-hidden="true" /> Limpiar</button>
        </div></div>
      </form>
      {opciones.error && <p className="field__error" role="alert">No se pudieron cargar las opciones de los filtros. {opciones.error}</p>}

      {lista.cargando && <p className="state-msg" role="status">Cargando…</p>}
      {lista.error && <p className="field__error" role="alert">{lista.error}</p>}
      {lista.datos && (
        <>
          <div className="bandeja__resultados">
          <div className="bandeja__resultados-cabecera"><div><h2><Inbox size={19} aria-hidden="true" /> Expedientes <span className="bandeja__contador">{total}</span></h2><p role="status">{lista.cargando ? 'Actualizando resultados…' : `${total} ${total === 1 ? 'expediente encontrado' : 'expedientes encontrados'}`}{filtrosActivos > 0 && ` · ${filtrosActivos} ${filtrosActivos === 1 ? 'filtro aplicado' : 'filtros aplicados'}`}</p></div><span className="bandeja__alcance"><ShieldCheck size={14} aria-hidden="true" /> Según tus permisos de acceso</span></div>
          <div className="tabla-envoltura" tabIndex={0} role="region" aria-label="Resultados de expedientes" aria-busy={lista.cargando}>
            <table className="tabla">
              <thead>
                <tr>
                  <th scope="col">Número</th>
                  <th scope="col">Asunto</th>
                  <th scope="col">Tipo</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Área actual</th>
                  <th scope="col">Fecha de recepción</th>
                  <th scope="col"><span className="bandeja__sr">Abrir expediente</span></th>
                </tr>
              </thead>
              <tbody>
                {lista.datos.results.length === 0 && (
                  <tr><td colSpan={7}><div className="bandeja__vacia"><Search size={30} aria-hidden="true" /><strong>No encontramos expedientes</strong><p>Prueba con otro término o limpia los filtros para ampliar la búsqueda.</p><button type="button" className="btn btn--secondary" onClick={limpiar}>Limpiar filtros</button></div></td></tr>
                )}
                {lista.datos.results.map((e) => (
                  <tr key={e.uuid}>
                    <td><Link className="bandeja__numero" to={`/panel/expedientes/${e.uuid}`}>{e.numero}</Link></td>
                    <td className="bandeja__asunto">
                      <Link to={`/panel/expedientes/${e.uuid}`}>{e.asunto}</Link>
                      <small>{e.solicitante}</small>
                    </td>
                    <td>{e.tipo_documental}</td>
                    <td>
                      <span className="bandeja__estado"><span aria-hidden="true" />{e.estado}</span>
                      {e.por_recibir && <span className="etiqueta etiqueta--alerta">Por recibir</span>}
                      {e.derivacion_pendiente && !e.por_recibir && <span className="etiqueta">Derivación pendiente</span>}
                    </td>
                    <td>{e.area_actual || 'Mesa de partes'}</td>
                    <td className="bandeja__fecha">{formatearFecha(e.fecha_recepcion)}</td>
                    <td><Link className="bandeja__abrir" to={`/panel/expedientes/${e.uuid}`} aria-label={`Abrir expediente ${e.numero}`}><ArrowUpRight size={18} aria-hidden="true" /></Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <nav className="bandeja__paginacion" aria-label="Paginación de expedientes"><span>Página <strong>{pagina}</strong></span><div>
            <button type="button" className="btn btn--secondary" disabled={!hayAnterior || lista.cargando} onClick={() => setPagina((n) => n - 1)}><ChevronLeft size={16} aria-hidden="true" /> Anterior</button>
            <button type="button" className="btn btn--secondary" disabled={!haySiguiente || lista.cargando} onClick={() => setPagina((n) => n + 1)}>Siguiente <ChevronRight size={16} aria-hidden="true" /></button>
          </div></nav></div>
        </>
      )}
    </section>
  );
}
