import { useCallback, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { FilePlus2, ScanLine, Paperclip, Send, CheckCircle2, ArrowRight, X } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import useCarga from '../../hooks/useCarga.js';
import { api, getConfiguracionSolicitud } from '../../services/api.js';
import { formatearTamano } from '../../utils/formato.js';

const VACIO = { tipo_persona: 'NATURAL', tipo_documento_identidad: 'DNI', numero_documento: '', nombres: '', apellidos: '', razon_social: '', email: '', telefono: '', tipo_documental: '', asunto: '', descripcion: '', area: '', mensaje: '' };

export default function RegistrarDocumentoPage() {
  const opciones = useCarga(useCallback(() => Promise.all([api.get('/panel/expedientes/opciones/'), getConfiguracionSolicitud()]), []));
  const [datos, setDatos] = useState(VACIO);
  const [principal, setPrincipal] = useState(null);
  const [anexos, setAnexos] = useState([]);
  const [errores, setErrores] = useState({});
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const clave = useRef(null);
  const bloqueo = useRef(false);
  const [version, setVersion] = useState(0);
  const [op, config] = opciones.datos || [];
  const limites = config?.archivos;

  function cambiar(e) {
    const { name, value } = e.target;
    setDatos((d) => ({ ...d, [name]: value, ...(name === 'tipo_persona' ? { tipo_documento_identidad: value === 'JURIDICA' ? 'RUC' : 'DNI' } : {}) }));
  }
  function campo(id, label, extra = {}) {
    return <FormField id={id} label={label} value={datos[id]} onChange={cambiar} error={errores[id]?.join(' ')} {...extra} />;
  }
  async function enviar(e) {
    e.preventDefault();
    if (bloqueo.current) return;
    setError(''); setErrores({});
    if (!principal) { setErrores({ documento: ['Selecciona el documento principal escaneado.'] }); return; }
    if (limites && anexos.length + 1 > limites.max_archivos) { setErrores({ anexos: [`Puedes subir hasta ${limites.max_archivos} archivos en total, incluido el documento principal.`] }); return; }
    const grandes = [principal, ...anexos].filter((a) => limites && a.size > limites.max_tamano_mb * 1024 * 1024);
    if (grandes.length) { setError(`Estos archivos superan el máximo de ${limites.max_tamano_mb} MB: ${grandes.map((a) => a.name).join(', ')}`); return; }
    bloqueo.current = true; setEnviando(true);
    try {
      clave.current ||= crypto.randomUUID();
      const cuerpo = new FormData();
      Object.entries(datos).forEach(([k, v]) => cuerpo.append(k, v));
      cuerpo.append('clave_envio', clave.current);
      cuerpo.append('documento', principal);
      anexos.forEach((a) => cuerpo.append('anexos', a));
      setResultado(await api.postForm('/panel/expedientes/registrar/', cuerpo));
    } catch (err) {
      setError(err.message || 'No se pudo registrar el documento.');
      setErrores(Object.fromEntries(Object.entries(err.errores || {}).map(([k, v]) => [k, Array.isArray(v) ? v : [String(v)]])));
    } finally { bloqueo.current = false; setEnviando(false); }
  }
  function nuevo() { setResultado(null); setDatos(VACIO); setPrincipal(null); setAnexos([]); setErrores({}); setError(''); clave.current = null; setVersion((v) => v + 1); }

  if (resultado) return <section className="registro registro-exito"><CheckCircle2 size={44} aria-hidden="true" /><h1>Documento registrado</h1><p>Expediente <strong>{resultado.numero}</strong></p><p>El documento y sus anexos se guardaron. La derivación queda pendiente de recepción por el área de destino.</p><div className="form-actions"><Link className="btn btn--primary" to={`/panel/expedientes/${resultado.uuid}`}>Ver expediente <ArrowRight size={17} aria-hidden="true" /></Link><button className="btn btn--secondary" onClick={nuevo}>Registrar otro documento</button></div></section>;
  return <section className="registro">
    <div className="panel-bienvenida"><div><span className="panel-eyebrow">RECEPCIÓN PRESENCIAL</span><h1>Registrar documento</h1><p>Digitaliza el documento recibido en físico y envíalo al área que lo atenderá.</p></div><FilePlus2 size={32} aria-hidden="true" /></div>
    {opciones.cargando && <p role="status">Cargando opciones del registro…</p>}
    {opciones.error && <div role="alert"><p className="field__error">{opciones.error}</p><button className="btn btn--secondary" onClick={opciones.recargar}>Volver a intentar</button></div>}
    {op && config && <form onSubmit={enviar} aria-busy={enviando}>
      <fieldset disabled={enviando} className="registro__campos">
        <div className="card form-section"><h2 className="form-section__title"><span className="registro__paso">1</span> Datos del solicitante</h2><div className="form-grid">
          {campo('tipo_persona', 'Tipo de persona', { as: 'select', required: true, children: config.tipos_persona.map((p) => <option key={p.valor} value={p.valor}>{p.etiqueta}</option>) })}
          {campo('tipo_documento_identidad', 'Documento de identidad', { as: 'select', required: true, children: config.tipos_documento_identidad.filter((p) => datos.tipo_persona !== 'JURIDICA' || p.valor === 'RUC').map((p) => <option key={p.valor} value={p.valor}>{p.etiqueta}</option>) })}
          {campo('numero_documento', 'Número de documento', { required: true, maxLength: 20 })}
          {datos.tipo_persona === 'NATURAL' ? <>{campo('nombres', 'Nombres', { required: true, maxLength: 150 })}{campo('apellidos', 'Apellidos', { required: true, maxLength: 150 })}</> : campo('razon_social', 'Razón social', { required: true, maxLength: 200 })}
          {campo('email', 'Correo electrónico', { type: 'email', maxLength: 254 })}{campo('telefono', 'Teléfono', { type: 'tel', maxLength: 20 })}
        </div></div>
        <div className="card form-section"><h2 className="form-section__title"><span className="registro__paso">2</span> Documento y anexos</h2>
          {campo('tipo_documental', 'Tipo de documento', { as: 'select', required: true, children: <><option value="">Selecciona un tipo</option>{op.tipos.map((t) => <option key={t.valor} value={t.valor}>{t.etiqueta}</option>)}</> })}
          {campo('asunto', 'Asunto', { required: true, minLength: 5, maxLength: 300, placeholder: 'Describe brevemente el motivo del documento' })}
          {campo('descripcion', 'Descripción del documento', { as: 'textarea', rows: 3, maxLength: 5000 })}
          <div className="registro__archivos"><ScanLine size={25} aria-hidden="true" /><FormField key={`documento-${version}`} id="documento" type="file" label="Documento principal escaneado" required accept=".pdf,.jpg,.jpeg,.png" hint="Carga el escaneo en PDF, JPG o PNG." onChange={(e) => setPrincipal(e.target.files[0] || null)} error={errores.documento?.join(' ')} />{principal && <p className="registro__archivo">{principal.name} · {formatearTamano(principal.size)}</p>}</div>
          <div className="registro__archivos"><Paperclip size={23} aria-hidden="true" /><FormField key={`anexos-${version}`} id="anexos" type="file" label="Anexos" multiple accept={limites.extensiones_permitidas.map((e) => `.${e}`).join(',')} hint="Puedes añadir varios archivos y retirar los que no correspondan." onChange={(e) => { setAnexos((a) => [...a, ...Array.from(e.target.files)]); e.target.value = ''; }} error={errores.anexos?.join(' ')} />
            {anexos.length > 0 && <ul className="registro__lista">{anexos.map((a, i) => <li key={`${a.name}-${i}`}><span>{a.name} · {formatearTamano(a.size)}</span><button type="button" onClick={() => setAnexos((lista) => lista.filter((_, n) => n !== i))} aria-label={`Quitar anexo ${a.name}`}><X size={16} aria-hidden="true" /></button></li>)}</ul>}
          </div><p className="field__hint">Máximo {limites.max_archivos} archivos en total y {limites.max_tamano_mb} MB por archivo. Anexos: {limites.extensiones_permitidas.join(', ').toUpperCase()}.</p>
        </div>
        <div className="card form-section"><h2 className="form-section__title"><span className="registro__paso">3</span> Derivación al área</h2>
          {campo('area', 'Área de destino', { as: 'select', required: true, children: <><option value="">Selecciona el área que atenderá el documento</option>{op.areas.map((a) => <option key={a.valor} value={a.valor}>{a.etiqueta}</option>)}</> })}
          {campo('mensaje', 'Mensaje para el área', { as: 'textarea', rows: 3, maxLength: 2000, placeholder: 'Añade indicaciones u observaciones para el área de destino' })}
          <p className="field__hint">Al registrar, se asignará un número de expediente y se enviará al área seleccionada para su recepción.</p>
        </div>
        {error && <div className="notice notice--error" role="alert"><div><p>{error}</p>{Object.keys(errores).length > 0 && <p>Revisa los campos señalados antes de volver a enviar.</p>}</div></div>}
        <div className="form-actions"><button type="submit" className="btn btn--primary"><Send size={18} aria-hidden="true" />{enviando ? 'Registrando documento…' : 'Registrar y derivar documento'}</button><Link to="/panel" className="panel-link">Volver al inicio</Link></div>
      </fieldset>
    </form>}
  </section>;
}
