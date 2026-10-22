import { useCallback, useEffect, useRef, useState } from 'react';
import { Loader2, Pencil, Plus, Save, X } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { ApiError, api } from '../../services/api.js';
import { useAuth } from '../../context/AuthContext.jsx';
import useCarga from '../../hooks/useCarga.js';

/*
 * Pantalla genérica "lista + formulario" para administrar un catálogo (usuarios, áreas, etc.).
 * El servidor valida y decide los permisos: aquí solo se ocultan botones por comodidad.
 *
 * Campos: { nombre, etiqueta, tipo: text|email|password|number|textarea|checkbox|select|multi,
 *           requerido, ayuda, opciones: [{valor, etiqueta}], cargarOpciones: () => Promise<[...]>,
 *           nulo: true (select vacío = sin valor), inicial }
 */
function valoresIniciales(campos) {
  const v = {};
  campos.forEach((c) => {
    if (c.tipo === 'checkbox') v[c.nombre] = c.inicial ?? false;
    else if (c.tipo === 'multi') v[c.nombre] = c.inicial ?? [];
    else v[c.nombre] = c.inicial ?? '';
  });
  return v;
}

function desdeRegistro(campos, registro) {
  const v = valoresIniciales(campos);
  campos.forEach((c) => {
    if (c.tipo === 'password') return;
    const dato = registro[c.nombre];
    if (dato !== null && dato !== undefined) v[c.nombre] = dato;
  });
  return v;
}

export default function CrudSimple({ titulo, endpoint, campos, columnas, permisoAgregar, permisoCambiar, nota }) {
  const { tiene } = useAuth();
  const puedeAgregar = tiene(permisoAgregar);
  const puedeCambiar = tiene(permisoCambiar);

  const lista = useCarga(useCallback(() => api.get(endpoint), [endpoint]));
  const [opcionesExtra, setOpcionesExtra] = useState({});
  const [editando, setEditando] = useState(null); // null = cerrado | 'nuevo' | id
  const [valores, setValores] = useState(() => valoresIniciales(campos));
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState('');
  const [aviso, setAviso] = useState('');
  const [guardando, setGuardando] = useState(false);
  const formRef = useRef(null);

  // Carga las opciones dinámicas (por ejemplo, la lista de áreas o de roles).
  useEffect(() => {
    campos
      .filter((c) => c.cargarOpciones)
      .forEach((c) => {
        c.cargarOpciones()
          .then((opciones) => setOpcionesExtra((previas) => ({ ...previas, [c.nombre]: opciones })))
          .catch(() => setOpcionesExtra((previas) => ({ ...previas, [c.nombre]: [] })));
      });
  }, [campos]);

  function abrirNuevo() {
    setValores(valoresIniciales(campos));
    setEditando('nuevo');
    setErrores({});
    setErrorGeneral('');
    setAviso('');
  }

  function abrirEdicion(registro) {
    setValores(desdeRegistro(campos, registro));
    setEditando(registro.id);
    setErrores({});
    setErrorGeneral('');
    setAviso('');
  }

  useEffect(() => {
    if (editando !== null && formRef.current) formRef.current.focus();
  }, [editando]);

  function cambiar(campo, valor) {
    setValores((previos) => ({ ...previos, [campo.nombre]: valor }));
    setErrores((previos) => {
      if (!(campo.nombre in previos)) return previos;
      const copia = { ...previos };
      delete copia[campo.nombre];
      return copia;
    });
  }

  function armarCuerpo() {
    const cuerpo = {};
    campos.forEach((c) => {
      const v = valores[c.nombre];
      if (c.tipo === 'password') {
        if (v) cuerpo[c.nombre] = v; // vacío al editar = no cambiar la contraseña
      } else if (c.tipo === 'number') {
        cuerpo[c.nombre] = v === '' ? null : Number(v);
      } else if (c.tipo === 'select' && c.nulo) {
        cuerpo[c.nombre] = v === '' ? null : v;
      } else {
        cuerpo[c.nombre] = v;
      }
    });
    return cuerpo;
  }

  async function guardar(evento) {
    evento.preventDefault();
    if (guardando) return;
    setGuardando(true);
    setErrores({});
    setErrorGeneral('');
    try {
      const cuerpo = armarCuerpo();
      if (editando === 'nuevo') await api.post(`${endpoint}`, cuerpo);
      else await api.patch(`${endpoint}${editando}/`, cuerpo);
      setAviso(editando === 'nuevo' ? 'Registro creado.' : 'Cambios guardados.');
      setEditando(null);
      lista.recargar();
    } catch (e) {
      if (e instanceof ApiError && e.errores) {
        const normal = {};
        Object.entries(e.errores).forEach(([campo, valor]) => {
          normal[campo] = Array.isArray(valor) ? valor.join(' ') : String(valor);
        });
        setErrores(normal);
        if (normal.non_field_errors || normal.detail) setErrorGeneral(normal.non_field_errors || normal.detail);
        else setErrorGeneral('Revisa los campos marcados.');
      } else {
        setErrorGeneral(e.message || 'No se pudo guardar.');
      }
    } finally {
      setGuardando(false);
    }
  }

  function opcionesDe(campo) {
    return campo.opciones || opcionesExtra[campo.nombre] || [];
  }

  function celda(columna, fila) {
    const valor = fila[columna.clave];
    if (columna.render) return columna.render(fila);
    if (typeof valor === 'boolean') return valor ? 'Sí' : 'No';
    if (Array.isArray(valor)) return valor.join(', ');
    return valor ?? '—';
  }

  return (
    <section>
      <div className="admin__encabezado">
        <h1 className="page-title">{titulo}</h1>
        {puedeAgregar && editando === null && (
          <button type="button" className="btn btn--primary" onClick={abrirNuevo}>
            <Plus size={18} aria-hidden="true" /> Nuevo
          </button>
        )}
      </div>
      {nota && <p className="state-msg">{nota}</p>}
      {aviso && (
        <p className="admin__aviso" role="status">
          {aviso}
        </p>
      )}

      {editando !== null && (
        <form onSubmit={guardar} noValidate className="card form-section" aria-label="Formulario">
          <h2 ref={formRef} tabIndex={-1} className="form-section__title">
            {editando === 'nuevo' ? 'Nuevo registro' : 'Editar registro'}
          </h2>
          {errorGeneral && (
            <p className="field__error" role="alert">
              {errorGeneral}
            </p>
          )}
          <div className="form-grid">
            {campos.map((c) => {
              const id = `campo-${c.nombre}`;
              if (c.tipo === 'checkbox') {
                return (
                  <div key={c.nombre} className="check">
                    <div className="check__fila">
                      <input id={id} type="checkbox" checked={valores[c.nombre]} onChange={(e) => cambiar(c, e.target.checked)} />
                      <label htmlFor={id}>{c.etiqueta}</label>
                    </div>
                    {errores[c.nombre] && <p className="field__error">{errores[c.nombre]}</p>}
                  </div>
                );
              }
              if (c.tipo === 'multi') {
                return (
                  <fieldset key={c.nombre} className="radio-group">
                    <legend className="field__label">{c.etiqueta}</legend>
                    {opcionesDe(c).map((o) => (
                      <label key={o.valor} className="radio">
                        <input
                          type="checkbox"
                          checked={valores[c.nombre].includes(o.valor)}
                          onChange={(e) =>
                            cambiar(c, e.target.checked ? [...valores[c.nombre], o.valor] : valores[c.nombre].filter((x) => x !== o.valor))
                          }
                        />
                        <span>{o.etiqueta}</span>
                      </label>
                    ))}
                    {errores[c.nombre] && <p className="field__error">{errores[c.nombre]}</p>}
                  </fieldset>
                );
              }
              if (c.tipo === 'select') {
                return (
                  <FormField key={c.nombre} id={id} as="select" label={c.etiqueta} required={c.requerido} hint={c.ayuda} value={valores[c.nombre] ?? ''} onChange={(e) => cambiar(c, e.target.value)} error={errores[c.nombre]}>
                    <option value="">{c.nulo ? '— Ninguna —' : 'Selecciona…'}</option>
                    {opcionesDe(c).map((o) => (
                      <option key={o.valor} value={o.valor}>
                        {o.etiqueta}
                      </option>
                    ))}
                  </FormField>
                );
              }
              return (
                <FormField
                  key={c.nombre}
                  id={id}
                  as={c.tipo === 'textarea' ? 'textarea' : 'input'}
                  type={c.tipo === 'textarea' ? undefined : c.tipo || 'text'}
                  label={c.etiqueta}
                  required={c.requerido && !(c.tipo === 'password' && editando !== 'nuevo')}
                  hint={c.tipo === 'password' && editando !== 'nuevo' ? 'Déjala vacía para no cambiarla.' : c.ayuda}
                  value={valores[c.nombre] ?? ''}
                  onChange={(e) => cambiar(c, e.target.value)}
                  error={errores[c.nombre]}
                  autoComplete={c.tipo === 'password' ? 'new-password' : 'off'}
                />
              );
            })}
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={guardando}>
              {guardando ? <Loader2 size={18} aria-hidden="true" className="spin" /> : <Save size={18} aria-hidden="true" />}
              Guardar
            </button>
            <button type="button" className="btn btn--secondary" onClick={() => setEditando(null)}>
              <X size={18} aria-hidden="true" /> Cancelar
            </button>
          </div>
        </form>
      )}

      {lista.cargando && <p className="state-msg" role="status">Cargando…</p>}
      {lista.error && (
        <div className="notice notice--error" role="alert">
          <div>
            <p>{lista.error}</p>
            <button type="button" className="btn btn--primary" onClick={lista.recargar}>
              Reintentar
            </button>
          </div>
        </div>
      )}
      {lista.datos && (
        <div className="tabla-envoltura">
          <table className="tabla">
            <thead>
              <tr>
                {columnas.map((c) => (
                  <th key={c.clave} scope="col">
                    {c.titulo}
                  </th>
                ))}
                {puedeCambiar && <th scope="col">Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {lista.datos.length === 0 && (
                <tr>
                  <td colSpan={columnas.length + 1}>No hay registros.</td>
                </tr>
              )}
              {lista.datos.map((fila) => (
                <tr key={fila.id}>
                  {columnas.map((c) => (
                    <td key={c.clave}>{celda(c, fila)}</td>
                  ))}
                  {puedeCambiar && (
                    <td>
                      <button type="button" className="btn btn--secondary" onClick={() => abrirEdicion(fila)}>
                        <Pencil size={16} aria-hidden="true" /> Editar
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
