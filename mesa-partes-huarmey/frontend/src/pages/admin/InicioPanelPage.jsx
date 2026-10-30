import { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, ArrowRight, Files, Inbox, CheckCircle2, Building2, BriefcaseBusiness, ShieldCheck, FileText } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
import { api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';

function Indicador({ numero, titulo, detalle, icono: Icono, pendiente }) {
  return <article className={`panel-stat${pendiente ? ' panel-stat--pendiente' : ''}`}>
    <div className="panel-stat__top"><span>{titulo}</span><span className="panel-stat__icono"><Icono size={21} aria-hidden="true" /></span></div>
    <strong className="panel-stat__numero">{numero}</strong><span className="panel-stat__detalle">{detalle}</span>
  </article>;
}

function Resumen() {
  const { datos, cargando, error } = useCarga(useCallback(() => api.get('/panel/dashboard/'), []));
  if (cargando) return <p className="panel-empty" role="status">Cargando resumen de expedientes…</p>;
  if (error) return <p className="field__error panel-empty" role="alert">{error}</p>;
  return <>
    <div className="panel-stats">
      <Indicador numero={datos.total} titulo="Expedientes visibles" detalle="Documentos a tu alcance" icono={Files} />
      <Indicador numero={datos.por_recibir} titulo="Por recibir en mi área" detalle={datos.por_recibir > 0 ? 'Pendientes de recepción' : 'Sin recepciones pendientes'} icono={Inbox} pendiente={datos.por_recibir > 0} />
      {datos.por_estado.map((e) => <Indicador key={e.nombre} numero={e.total} titulo={e.nombre} detalle="Según el estado del expediente" icono={CheckCircle2} />)}
    </div>
    <section className="panel-recientes" aria-labelledby="recientes-title">
      <div className="panel-recientes__cabecera"><div><h2 id="recientes-title">Últimos expedientes</h2><p>Consulta los documentos más recientes de tu bandeja.</p></div><Link className="panel-link" to="/panel/expedientes">Ver todos <ArrowRight size={16} aria-hidden="true" /></Link></div>
      {datos.recientes.length === 0 ? <div className="panel-empty"><Inbox size={30} aria-hidden="true" /><p>Aún no hay expedientes para mostrar.</p></div> :
        <div className="panel-documentos">{datos.recientes.map((e) => <Link className="panel-documento" key={e.uuid} to={`/panel/expedientes/${e.uuid}`}>
          <span className="panel-documento__icono"><FileText size={21} aria-hidden="true" /></span><span className="panel-documento__texto"><strong>{e.numero}</strong><span>{e.asunto}</span></span><span className="panel-estado"><span />{e.estado}</span><ArrowUpRight className="panel-documento__flecha" size={19} aria-hidden="true" />
        </Link>)}</div>}
      <div className="panel-recientes__pie">Los expedientes se muestran según tus permisos de acceso.</div>
    </section>
  </>;
}

export default function InicioPanelPage() {
  const { usuario, tiene } = useAuth();
  return <section className="panel-inicio">
    <div className="panel-bienvenida"><div><span className="panel-eyebrow">TU PANEL DE GESTIÓN</span><h1>Bienvenido, {usuario.nombre}</h1><p>Todo listo para continuar con la atención de tus documentos.</p></div>{tiene('expedientes.view_expediente') && <Link className="btn btn--primary" to="/panel/expedientes"><Inbox size={18} aria-hidden="true" /> Ir a expedientes <ArrowRight size={17} aria-hidden="true" /></Link>}</div>
    <dl className="panel-perfil">
      <div><ShieldCheck size={19} aria-hidden="true" /><span><dt>Rol asignado</dt><dd>{usuario.roles.length ? usuario.roles.join(', ') : 'Sin rol asignado'}</dd></span></div>
      <div><Building2 size={19} aria-hidden="true" /><span><dt>Área de trabajo</dt><dd>{usuario.area ? usuario.area.nombre : 'Sin área asignada'}</dd></span></div>
      <div><BriefcaseBusiness size={19} aria-hidden="true" /><span><dt>Cargo</dt><dd>{usuario.cargo || 'Sin cargo asignado'}</dd></span></div>
    </dl>
    {tiene('expedientes.view_expediente') && <Resumen />}
  </section>;
}
