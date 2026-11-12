import { useCallback, useState } from 'react';
import { Download, SlidersHorizontal, RotateCcw, Search, FileText, Layers, Building2, CalendarDays, BarChart3, Info } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';
import '../../styles/reports.css';

const VACIO = { desde: '', hasta: '', estado: '', tipo: '', area: '' };
function aConsulta(filtros) {
  const p = new URLSearchParams();
  Object.entries(filtros).forEach(([k, v]) => v && p.set(k, v));
  return p.toString();
}
function Conteo({ titulo, descripcion, filas, icono: Icono }) {
  const maximo = Math.max(1, ...filas.map((f) => f.total));
  return (
    <article className="report-chart">
      <header><span className="report-icon"><Icono size={19} aria-hidden="true" /></span><div><h2>{titulo}</h2><p>{descripcion}</p></div><span className="report-chart__badge">{filas.length} categorías</span></header>
      {filas.length === 0 ? (
        <div className="report-empty"><BarChart3 size={30} strokeWidth={1.4} aria-hidden="true" /><strong>Sin información para mostrar</strong><p>Los resultados aparecerán al registrar documentos<br />que coincidan con los filtros.</p></div>
      ) : (
        <ul className="report-bars" aria-label={titulo}>
          {filas.map((f) => <li key={f.nombre}><div><span>{f.nombre}</span><strong>{f.total}</strong></div><span className="report-bars__track" aria-hidden="true"><span style={{ width: `${(f.total / maximo) * 100}%` }} /></span></li>)}
        </ul>
      )}
    </article>
  );
}
export default function ReportesPage() {
  const opciones = useCarga(useCallback(() => api.get('/panel/expedientes/opciones/'), []));
  const [formulario, setFormulario] = useState(VACIO);
  const [filtros, setFiltros] = useState(VACIO);
  const resumen = useCarga(useCallback(() => api.get(`/panel/reportes/resumen/?${aConsulta(filtros)}`), [filtros]));
  const op = opciones.datos;
  const d = resumen.datos;
  const listo = d && !resumen.cargando && !resumen.error;
  const activos = Object.values(filtros).filter(Boolean).length;
  function cambiar(e) { setFormulario((previo) => ({ ...previo, [e.target.name]: e.target.value })); }
  return (
    <section className="reports" aria-labelledby="reports-title">
      <header className="reports-heading"><div><span className="reports-eyebrow">GESTIÓN DOCUMENTAL / ANÁLISIS</span><h1 id="reports-title">Reportes de expedientes</h1><p>Consulta la distribución de documentos y exporta la información de tu gestión.</p></div>{listo && <a className="btn btn--secondary reports-export" href={`/api/panel/reportes/exportar.csv?${aConsulta(filtros)}`} download><Download size={17} aria-hidden="true" /> Exportar CSV</a>}</header>
      <form className="reports-filters" onSubmit={(e) => { e.preventDefault(); setFiltros({ ...formulario }); }}>
        <div className="reports-filters__heading"><h2><SlidersHorizontal size={18} aria-hidden="true" /> Filtros de consulta</h2><span>Todos los campos son opcionales</span></div>
        <div className="reports-filters__grid">
          <FormField id="desde" type="date" label="Fecha desde" value={formulario.desde} max={formulario.hasta || undefined} onChange={cambiar} />
          <FormField id="hasta" type="date" label="Fecha hasta" value={formulario.hasta} min={formulario.desde || undefined} onChange={cambiar} />
          <FormField id="estado" as="select" label="Estado del expediente" value={formulario.estado} onChange={cambiar}><option value="">Todos los estados</option>{op?.estados.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}</FormField>
          <FormField id="tipo" as="select" label="Tipo de documento" value={formulario.tipo} onChange={cambiar}><option value="">Todos los tipos</option>{op?.tipos.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}</FormField>
          {op?.ve_todos && <FormField id="area" as="select" label="Área responsable" value={formulario.area} onChange={cambiar}><option value="">Todas las áreas</option>{op.areas.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}</FormField>}
        </div>
        {opciones.error && <p className="field__error" role="alert">{opciones.error} <button type="button" onClick={opciones.recargar}>Reintentar</button></p>}
        <div className="reports-filters__footer"><span>{activos ? `${activos} filtro${activos === 1 ? '' : 's'} aplicado${activos === 1 ? '' : 's'}` : 'Mostrando todos los registros disponibles'}</span><div><button type="button" className="btn btn--secondary" onClick={() => { setFormulario(VACIO); setFiltros(VACIO); }}><RotateCcw size={15} aria-hidden="true" /> Limpiar</button><button type="submit" className="btn btn--primary" disabled={resumen.cargando}><Search size={15} aria-hidden="true" /> Aplicar filtros</button></div></div>
      </form>
      {resumen.cargando && <p className="state-msg" role="status">Actualizando reporte…</p>}
      {resumen.error && <p className="field__error" role="alert">{resumen.error} <button type="button" onClick={resumen.recargar}>Reintentar</button></p>}
      {listo && <>
        <div className="reports-stats" role="status">
          {[{ titulo: 'Total de expedientes', valor: d.total, detalle: 'Documentos en esta consulta', icono: FileText }, { titulo: 'Estados representados', valor: d.por_estado.length, detalle: 'Distribución del seguimiento', icono: Layers }, { titulo: 'Áreas con expedientes', valor: d.por_area.length, detalle: 'Dependencias responsables', icono: Building2 }].map(({ titulo, valor, detalle, icono: Icono }, i) => <div className={`reports-stat${i === 0 ? ' reports-stat--featured' : ''}`} key={titulo}><div><span>{titulo}</span><strong>{valor.toLocaleString('es-PE')}</strong><small>{detalle}</small></div><span className="report-icon"><Icono size={23} aria-hidden="true" /></span></div>)}
        </div>
        <div className="reports-results-heading"><h2>Distribución de expedientes</h2><span>Según los filtros aplicados</span></div>
        <div className="reports-charts"><Conteo titulo="Por estado" descripcion="Situación actual de los expedientes" filas={d.por_estado} icono={Layers} /><Conteo titulo="Por tipo de documento" descripcion="Composición de los documentos registrados" filas={d.por_tipo} icono={FileText} /><Conteo titulo="Por área responsable" descripcion="Distribución entre dependencias" filas={d.por_area} icono={Building2} /><Conteo titulo="Por mes de recepción" descripcion="Volumen de registros por período" filas={d.por_mes} icono={CalendarDays} /></div>
      </>}
      <p className="reports-note"><Info size={16} aria-hidden="true" />Los reportes incluyen los expedientes que tu cuenta puede consultar. El cálculo de plazos está pendiente de validación.</p>
    </section>
  );
}
