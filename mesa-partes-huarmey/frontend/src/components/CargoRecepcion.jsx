import { formatearFecha, formatearTamano } from '../utils/formato.js';

// Muestra el cargo de recepción. Se usa tras registrar y en la consulta pública.
export default function CargoRecepcion({ cargo }) {
  return (
    <article className="cargo" aria-label="Cargo de recepción">
      <header className="cargo__cabecera">
        <p className="cargo__institucion">Municipalidad Provincial de Huarmey</p>
        <h2 className="cargo__titulo">Cargo de recepción — Mesa de Partes Digital</h2>
        <p className="cargo__demo">VERSIÓN DE DEMOSTRACIÓN</p>
      </header>

      <div className="cargo__claves">
        <div>
          <span className="cargo__etiqueta">Número de expediente</span>
          <strong className="cargo__valor">{cargo.numero}</strong>
        </div>
        <div>
          <span className="cargo__etiqueta">Código de verificación</span>
          <strong className="cargo__valor">{cargo.codigo_verificacion}</strong>
        </div>
      </div>

      <dl className="result__datos">
        <dt>Fecha y hora de recepción (hora de Lima)</dt>
        <dd>{formatearFecha(cargo.fecha_recepcion)}</dd>
        <dt>Estado</dt>
        <dd>{cargo.estado}</dd>
        <dt>Tipo de documento</dt>
        <dd>{cargo.tipo_documental}</dd>
        <dt>Asunto</dt>
        <dd>{cargo.asunto}</dd>
        <dt>Solicitante</dt>
        <dd>
          {cargo.solicitante} ({cargo.documento_identidad})
        </dd>
        <dt>Documentos adjuntos</dt>
        <dd>
          {cargo.adjuntos.length === 0 ? (
            'Sin adjuntos'
          ) : (
            <ul className="cargo__adjuntos">
              {cargo.adjuntos.map((a) => (
                <li key={a.sha256 + a.nombre}>
                  {a.nombre} ({formatearTamano(a.tamano)})
                  <br />
                  <small>Huella SHA-256: {a.sha256.slice(0, 16)}…</small>
                </li>
              ))}
            </ul>
          )}
        </dd>
      </dl>

      <ul className="cargo__advertencias">
        {cargo.advertencias.map((texto) => (
          <li key={texto}>{texto}</li>
        ))}
      </ul>
    </article>
  );
}
