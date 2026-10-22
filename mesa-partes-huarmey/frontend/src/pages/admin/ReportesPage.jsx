import { useCallback, useState } from 'react';
import { Download } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';

const VACIO = { desde: '', hasta: '', estado: '', tipo: '', area: '' };

function aConsulta(filtros) {
  const p = new URLSearchParams();
  Object.entries(filtros).forEach(([k, v]) => v && p.set(k, v));
  return p.toString();
}

// Tabla de conteos con barras proporcionales (sin librerías de gráficos).
function Conteo({ titulo, filas }) {
  const maximo = Math.max(1, ...filas.map((f) => f.total));
  return (
    <div className="card form-section">
      <h2 className="form-section__title">{titulo}</h2>
      {filas.length === 0 ? (
        <p>Sin datos.</p>
      ) : (
        <table className="tabla">
          <tbody>
            {filas.map((f) => (
              <tr key={f.nombre}>
                <th scope="row">{f.nombre}</th>
                <td className="barra-celda">
                  <span className="barra" style={{ width: `${(f.total / maximo) * 100}%` }} aria-hidden="true" />
                </td>
                <td>{f.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function ReportesPage() {
  const opciones = useCarga(useCallback(() => api.get('/panel/expedientes/opciones/'), []));
  const [formulario, setFormulario] = useState(VACIO);
  const [filtros, setFiltros] = useState(VACIO);
  const resumen = useCarga(useCallback(() => api.get(`/panel/reportes/resumen/?${aConsulta(filtros)}`), [filtros]));
  const op = opciones.datos;
  const d = resumen.datos;

  function cambiar(e) {
    setFormulario((previo) => ({ ...previo, [e.target.name]: e.target.value }));
  }

  return (
    <section>
      <h1 className="page-title">Reportes</h1>
      <p className="state-msg">Conteos de los expedientes que tu rol puede ver. No incluyen cálculo de plazos (pendiente de validar).</p>

      <form
        className="card form-section"
        onSubmit={(e) => {
          e.preventDefault();
          setFiltros(formulario);
        }}
      >
        <div className="form-grid">
          <FormField id="desde" type="date" label="Desde" value={formulario.desde} onChange={cambiar} />
          <FormField id="hasta" type="date" label="Hasta" value={formulario.hasta} onChange={cambiar} />
          <FormField id="estado" as="select" label="Estado" value={formulario.estado} onChange={cambiar}>
            <option value="">Todos</option>
            {op && op.estados.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}
          </FormField>
          <FormField id="tipo" as="select" label="Tipo de documento" value={formulario.tipo} onChange={cambiar}>
            <option value="">Todos</option>
            {op && op.tipos.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}
          </FormField>
          {op && op.ve_todos && (
            <FormField id="area" as="select" label="Área que lo tiene" value={formulario.area} onChange={cambiar}>
              <option value="">Todas</option>
              {op.areas.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}
            </FormField>
          )}
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn--primary">Aplicar filtros</button>
          <button type="button" className="btn btn--secondary" onClick={() => { setFormulario(VACIO); setFiltros(VACIO); }}>Limpiar</button>
          <a className="btn btn--secondary" href={`/api/panel/reportes/exportar.csv?${aConsulta(filtros)}`} download>
            <Download size={16} aria-hidden="true" /> Exportar CSV
          </a>
        </div>
      </form>

      {resumen.cargando && <p className="state-msg" role="status">Calculando…</p>}
      {resumen.error && <p className="field__error" role="alert">{resumen.error}</p>}
      {d && (
        <>
          <p className="state-msg" role="status"><strong>{d.total}</strong> expediente(s) en el reporte.</p>
          <Conteo titulo="Por estado" filas={d.por_estado} />
          <Conteo titulo="Por tipo de documento" filas={d.por_tipo} />
          <Conteo titulo="Por área que lo tiene" filas={d.por_area} />
          <Conteo titulo="Por mes de recepción" filas={d.por_mes} />
        </>
      )}
    </section>
  );
}
