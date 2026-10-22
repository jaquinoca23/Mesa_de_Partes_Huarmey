import { useCallback, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Download, Inbox } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { ApiError, api } from '../../services/api.js';
import useCarga from '../../hooks/useCarga.js';
import { formatearFecha, formatearTamano } from '../../utils/formato.js';

// Mensaje de éxito o de error de una acción, con el detalle por campo si el servidor lo envía.
function textoDeError(e) {
  if (e instanceof ApiError && e.errores) {
    return Object.values(e.errores).map((v) => (Array.isArray(v) ? v.join(' ') : String(v))).join(' ');
  }
  return e.message || 'No se pudo completar la acción.';
}

// Formulario pequeño que envía a una acción del servidor y recarga el expediente.
function Accion({ titulo, ruta, vacio, campos, alExito, textoBoton }) {
  const [valores, setValores] = useState(vacio);
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function enviar(e) {
    e.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setError('');
    try {
      const respuesta = await api.post(ruta, valores);
      setValores(vacio);
      alExito(respuesta.mensaje);
    } catch (err) {
      setError(textoDeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="card form-section">
      <h3 className="form-section__title">{titulo}</h3>
      {campos.map((c) => (
        <FormField
          key={c.nombre}
          id={`${ruta}-${c.nombre}`}
          as={c.tipo === 'select' ? 'select' : c.tipo === 'textarea' ? 'textarea' : 'input'}
          label={c.etiqueta}
          required={c.requerido}
          value={valores[c.nombre]}
          onChange={(e) => setValores((v) => ({ ...v, [c.nombre]: e.target.value }))}
          {...(c.tipo === 'textarea' ? { rows: 3 } : {})}
        >
          {c.tipo === 'select' && (
            <>
              <option value="">Selecciona…</option>
              {c.opciones.map((o) => <option key={o.valor} value={o.valor}>{o.etiqueta}</option>)}
            </>
          )}
        </FormField>
      ))}
      {error && <p className="field__error" role="alert">{error}</p>}
      <button type="submit" className="btn btn--primary" disabled={enviando}>{enviando ? 'Guardando…' : textoBoton}</button>
    </form>
  );
}

export default function ExpedienteDetallePage() {
  const { uuid } = useParams();
  const base = `/panel/expedientes/${uuid}`;
  const detalle = useCarga(useCallback(() => api.get(`${base}/`), [base]));
  const opciones = useCarga(useCallback(() => api.get('/panel/expedientes/opciones/'), []));
  const [aviso, setAviso] = useState('');
  const [errorRecibir, setErrorRecibir] = useState('');

  function exito(mensaje) {
    setAviso(mensaje);
    detalle.recargar();
  }

  async function recibir(id) {
    setErrorRecibir('');
    try {
      const r = await api.post(`/panel/derivaciones/${id}/recibir/`, {});
      exito(r.mensaje);
    } catch (e) {
      setErrorRecibir(textoDeError(e));
    }
  }

  if (detalle.cargando && !detalle.datos) return <p className="state-msg" role="status">Cargando…</p>;
  if (detalle.error) {
    return (
      <div className="notice notice--error" role="alert">
        <div>
          <p>{detalle.error}</p>
          <Link to="/panel/expedientes" className="btn btn--primary">Volver a la bandeja</Link>
        </div>
      </div>
    );
  }
  const d = detalle.datos;
  const op = opciones.datos;
  const acc = d.acciones;

  return (
    <section>
      <Link to="/panel/expedientes" className="btn btn--secondary"><ArrowLeft size={16} aria-hidden="true" /> Bandeja</Link>
      <h1 className="page-title">Expediente {d.numero}</h1>
      {aviso && <p className="admin__aviso" role="status">{aviso}</p>}

      <div className="card form-section">
        <dl className="result__datos">
          <dt>Asunto</dt><dd>{d.asunto}</dd>
          <dt>Descripción</dt><dd>{d.descripcion || '—'}</dd>
          <dt>Tipo de documento</dt><dd>{d.tipo_documental}</dd>
          <dt>Estado</dt><dd>{d.estado}</dd>
          <dt>Área actual</dt><dd>{d.area_actual || 'Mesa de partes'}</dd>
          <dt>Recibido</dt><dd>{formatearFecha(d.fecha_recepcion)}</dd>
          <dt>Solicitante</dt><dd>{d.solicitante.nombre} ({d.solicitante.tipo_persona})</dd>
          <dt>Documento</dt><dd>{d.solicitante.documento}</dd>
          <dt>Contacto</dt><dd>{d.solicitante.email} {d.solicitante.telefono && `· ${d.solicitante.telefono}`}</dd>
        </dl>
      </div>

      {d.derivacion_pendiente && (
        <div className="notice" role="status">
          <Inbox size={22} aria-hidden="true" className="notice__icon" />
          <div>
            <h2 className="notice__title">Derivación pendiente de recepción</h2>
            <p>Enviado a <strong>{d.derivacion_pendiente.area_destino}</strong> — {d.derivacion_pendiente.motivo}</p>
            {acc.recibir_derivacion_id && (
              <button type="button" className="btn btn--primary" onClick={() => recibir(acc.recibir_derivacion_id)}>
                Recibir este expediente
              </button>
            )}
            {errorRecibir && <p className="field__error" role="alert">{errorRecibir}</p>}
          </div>
        </div>
      )}

      <h2 className="form-section__subtitle">Documentos adjuntos</h2>
      {d.adjuntos.length === 0 ? <p>Sin adjuntos.</p> : (
        <ul>
          {d.adjuntos.map((a) => (
            <li key={a.id}>
              <a href={`/api/panel/adjuntos/${a.id}/descargar/`} download>
                <Download size={14} aria-hidden="true" /> {a.nombre}
              </a>{' '}
              ({formatearTamano(a.tamano)}) <small>SHA-256: {a.sha256.slice(0, 12)}…</small>
            </li>
          ))}
        </ul>
      )}

      {op && (acc.cambiar_estado || acc.derivar || acc.actuar) && (
        <div className="form-grid">
          {acc.cambiar_estado && (
            <Accion
              titulo="Cambiar estado"
              ruta={`${base}/cambiar-estado/`}
              vacio={{ estado: '', observacion: '' }}
              textoBoton="Cambiar estado"
              alExito={exito}
              campos={[
                { nombre: 'estado', etiqueta: 'Nuevo estado', tipo: 'select', requerido: true, opciones: op.estados.filter((e) => e.etiqueta !== d.estado) },
                { nombre: 'observacion', etiqueta: 'Observación', tipo: 'textarea' },
              ]}
            />
          )}
          {acc.derivar && (
            <Accion
              titulo="Derivar a otra área"
              ruta={`${base}/derivar/`}
              vacio={{ area: '', motivo: '', observaciones: '' }}
              textoBoton="Derivar"
              alExito={exito}
              campos={[
                { nombre: 'area', etiqueta: 'Área de destino', tipo: 'select', requerido: true, opciones: op.areas },
                { nombre: 'motivo', etiqueta: 'Motivo', requerido: true },
                { nombre: 'observaciones', etiqueta: 'Observaciones', tipo: 'textarea' },
              ]}
            />
          )}
          {acc.actuar && (
            <Accion
              titulo="Registrar observación o actuación"
              ruta={`${base}/actuaciones/`}
              vacio={{ tipo: '', texto: '' }}
              textoBoton="Registrar"
              alExito={exito}
              campos={[
                { nombre: 'tipo', etiqueta: 'Tipo', tipo: 'select', requerido: true, opciones: op.tipos_actuacion },
                { nombre: 'texto', etiqueta: 'Detalle', tipo: 'textarea', requerido: true },
              ]}
            />
          )}
        </div>
      )}

      <h2 className="form-section__subtitle">Historial de estados</h2>
      <ol className="historial">
        {d.historial.map((h) => (
          <li key={h.fecha + h.estado}>
            <strong>{h.estado}</strong> — {formatearFecha(h.fecha)} — {h.usuario}
            {h.observacion && <><br /><small>{h.observacion}</small></>}
          </li>
        ))}
      </ol>

      <h2 className="form-section__subtitle">Derivaciones</h2>
      {d.derivaciones.length === 0 ? <p>Sin derivaciones.</p> : (
        <div className="tabla-envoltura">
          <table className="tabla">
            <thead><tr><th scope="col">Origen</th><th scope="col">Destino</th><th scope="col">Motivo</th><th scope="col">Enviado por</th><th scope="col">Estado</th></tr></thead>
            <tbody>
              {d.derivaciones.map((x) => (
                <tr key={x.id}>
                  <td>{x.origen}</td>
                  <td>{x.destino}</td>
                  <td>{x.motivo}</td>
                  <td>{x.remitente}<br /><small>{formatearFecha(x.fecha)}</small></td>
                  <td>{x.estado}{x.recibido_por && <><br /><small>{x.recibido_por} · {formatearFecha(x.fecha_recepcion)}</small></>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 className="form-section__subtitle">Observaciones y actuaciones</h2>
      {d.actuaciones.length === 0 ? <p>Sin registros.</p> : (
        <ul className="historial">
          {d.actuaciones.map((a) => (
            <li key={a.fecha + a.texto}>
              <strong>{a.tipo}</strong> — {a.usuario} — {formatearFecha(a.fecha)}
              <br />{a.texto}
            </li>
          ))}
        </ul>
      )}

      <h2 className="form-section__subtitle">Notificaciones al solicitante</h2>
      {d.notificaciones.length === 0 ? <p>Sin notificaciones.</p> : (
        <ul>
          {d.notificaciones.map((n) => <li key={n.fecha + n.tipo}>{n.tipo}: {n.estado} ({formatearFecha(n.fecha)})</li>)}
        </ul>
      )}
    </section>
  );
}
