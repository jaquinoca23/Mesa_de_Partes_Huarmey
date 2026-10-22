import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2, Send, ShieldCheck } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import FileUploader from '../../components/FileUploader.jsx';
import { ApiError, consultarDni, registrarSolicitud } from '../../services/api.js';
import { guardarCargo } from '../../utils/cargoStorage.js';
import { validarSolicitud } from '../../utils/validaciones.js';
import { generarUuid } from '../../utils/uuid.js';

const VALORES_INICIALES = {
  tipo_persona: 'NATURAL',
  tipo_documento_identidad: 'DNI',
  numero_documento: '',
  nombres: '',
  apellidos: '',
  razon_social: '',
  email: '',
  telefono: '',
  tipo_documental: '',
  asunto: '',
  descripcion: '',
  acepta_politica_privacidad: false,
  declara_veracidad: false,
};

// Nombres legibles de cada campo, para el resumen de errores.
const ETIQUETAS = {
  tipo_persona: 'Tipo de solicitante',
  tipo_documento_identidad: 'Tipo de documento de identidad',
  numero_documento: 'Número de documento',
  nombres: 'Nombres',
  apellidos: 'Apellidos',
  razon_social: 'Razón social',
  email: 'Correo electrónico',
  telefono: 'Teléfono o celular',
  tipo_documental: 'Tipo de documento',
  asunto: 'Asunto',
  descripcion: 'Descripción',
  archivos: 'Documentos adjuntos',
  acepta_politica_privacidad: 'Política de privacidad',
  declara_veracidad: 'Declaración de veracidad',
};

// El servidor puede devolver varios mensajes por campo; aquí se unifican.
// "archivos" se conserva como lista porque cada mensaje nombra un archivo distinto.
function normalizarErrores(errores) {
  const resultado = {};
  Object.entries(errores).forEach(([campo, valor]) => {
    const lista = Array.isArray(valor) ? valor.map(String) : [String(valor)];
    resultado[campo] = campo === 'archivos' ? lista : lista.join(' ');
  });
  return resultado;
}

// Casilla de verificación con mensaje de error accesible.
function Casilla({ id, checked, onChange, error, children }) {
  const idError = error ? `${id}-error` : undefined;
  return (
    <div className={`check${error ? ' check--error' : ''}`}>
      <div className="check__fila">
        <input
          type="checkbox"
          id={id}
          name={id}
          checked={checked}
          onChange={onChange}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={idError}
        />
        <label htmlFor={id}>{children}</label>
      </div>
      {error && (
        <p id={idError} className="field__error">
          {error}
        </p>
      )}
    </div>
  );
}

export default function FormularioSolicitud({ config, tipos }) {
  const [valores, setValores] = useState(VALORES_INICIALES);
  const [archivos, setArchivos] = useState([]);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState('');
  const [estado, setEstado] = useState('editando'); // editando | enviando
  const navigate = useNavigate();
  // Estado de la búsqueda de DNI: reposo | buscando | ok | error
  const [dni, setDni] = useState({ estado: 'reposo', mensaje: '' });
  const [avisoFoco, setAvisoFoco] = useState(0);

  const claveEnvio = useRef(generarUuid()); // identifica este envío (el servidor evita duplicados con ella)
  const enviandoRef = useRef(false); // bloqueo inmediato contra doble clic
  const resumenRef = useRef(null);

  // Cuando falla un envío, el foco pasa al resumen de errores para que se lea de inmediato.
  useEffect(() => {
    if (avisoFoco > 0 && resumenRef.current) resumenRef.current.focus();
  }, [avisoFoco]);

  function quitarError(campo) {
    setErrores((previos) => {
      if (!(campo in previos)) return previos;
      const copia = { ...previos };
      delete copia[campo];
      return copia;
    });
  }

  function cambiar(evento) {
    const { name, value, type, checked } = evento.target;
    setValores((previos) => ({ ...previos, [name]: type === 'checkbox' ? checked : value }));
    quitarError(name);
    if (name === 'numero_documento' || name === 'tipo_documento_identidad') setDni({ estado: 'reposo', mensaje: '' });
  }

  // Busca nombres y apellidos por DNI. Solo AYUDA a completar: no es una constancia de identidad.
  async function verificarDni() {
    const numero = valores.numero_documento.replace(/\s/g, '');
    if (!/^\d{8}$/.test(numero)) {
      setDni({ estado: 'error', mensaje: 'Escribe un DNI de 8 dígitos para verificarlo.' });
      return;
    }
    setDni({ estado: 'buscando', mensaje: '' });
    try {
      const r = await consultarDni(numero);
      setValores((previos) => ({ ...previos, nombres: r.nombres, apellidos: r.apellidos }));
      quitarError('nombres');
      quitarError('apellidos');
      setDni({ estado: 'ok', mensaje: 'Datos encontrados. Revísalos y corrígelos si hace falta.' });
    } catch (e) {
      setDni({ estado: 'error', mensaje: e.message || 'No se pudo verificar el DNI.' });
    }
  }

  function cambiarTipoPersona(tipo) {
    setValores((previos) => ({
      ...previos,
      tipo_persona: tipo,
      // Una persona jurídica se identifica con RUC; una natural empieza con DNI.
      tipo_documento_identidad: tipo === 'JURIDICA' ? 'RUC' : 'DNI',
    }));
    quitarError('tipo_persona');
    quitarError('tipo_documento_identidad');
    quitarError('numero_documento');
  }

  function cambiarArchivos(nuevos) {
    setArchivos(nuevos);
    quitarError('archivos');
  }

  function armarFormData() {
    const datos = new FormData();
    datos.append('clave_envio', claveEnvio.current);
    datos.append('tipo_persona', valores.tipo_persona);
    datos.append('tipo_documento_identidad', valores.tipo_documento_identidad);
    datos.append('numero_documento', valores.numero_documento);
    if (valores.tipo_persona === 'JURIDICA') {
      datos.append('razon_social', valores.razon_social);
    } else {
      datos.append('nombres', valores.nombres);
      datos.append('apellidos', valores.apellidos);
    }
    datos.append('email', valores.email);
    datos.append('telefono', valores.telefono);
    datos.append('tipo_documental', valores.tipo_documental);
    datos.append('asunto', valores.asunto);
    datos.append('descripcion', valores.descripcion);
    datos.append('acepta_politica_privacidad', String(valores.acepta_politica_privacidad));
    datos.append('declara_veracidad', String(valores.declara_veracidad));
    archivos.forEach((archivo) => datos.append('archivos', archivo, archivo.name));
    return datos;
  }

  async function enviar(evento) {
    evento.preventDefault();
    if (enviandoRef.current) return; // ya hay un envío en curso
    setErrorGeneral('');

    const erroresCliente = validarSolicitud(valores, archivos, config);
    if (Object.keys(erroresCliente).length > 0) {
      setErrores(erroresCliente);
      setAvisoFoco((n) => n + 1);
      return;
    }

    enviandoRef.current = true;
    setErrores({});
    setEstado('enviando');
    try {
      const respuesta = await registrarSolicitud(armarFormData());
      // Solo se muestra el cargo si el servidor confirmó que la solicitud quedó registrada.
      if (!respuesta || respuesta.registrado !== true || !respuesta.cargo) {
        throw new ApiError('No se pudo confirmar el registro de tu solicitud. Inténtalo de nuevo.');
      }
      guardarCargo(respuesta.cargo);
      navigate('/cargo');
    } catch (error) {
      if (error instanceof ApiError && error.errores) {
        setErrores(normalizarErrores(error.errores));
      } else {
        setErrorGeneral(error.message || 'Ocurrió un error inesperado. Inténtalo de nuevo.');
      }
      setEstado('editando');
      setAvisoFoco((n) => n + 1);
    } finally {
      enviandoRef.current = false;
    }
  }

  // ---------- Formulario ----------
  const enviando = estado === 'enviando';
  const esJuridica = valores.tipo_persona === 'JURIDICA';
  const opcionesDocumento = esJuridica
    ? config.tipos_documento_identidad.filter((o) => o.valor === 'RUC')
    : config.tipos_documento_identidad;
  const listaErrores = Object.entries(errores).flatMap(([campo, valor]) =>
    (Array.isArray(valor) ? valor : [valor]).map((mensaje) => ({ campo, mensaje })),
  );
  const hayResumen = listaErrores.length > 0 || errorGeneral;

  return (
    <form onSubmit={enviar} noValidate>
      {hayResumen && (
        <div ref={resumenRef} className="error-summary" role="alert" tabIndex={-1}>
          <h2 className="error-summary__title">
            {errorGeneral ? 'No se pudo enviar el formulario' : 'Revisa los campos marcados'}
          </h2>
          {errorGeneral && <p>{errorGeneral}</p>}
          {listaErrores.length > 0 && (
            <ul>
              {listaErrores.map(({ campo, mensaje }) => (
                <li key={`${campo}-${mensaje}`}>
                  <a href={`#${campo}`}>{ETIQUETAS[campo] || 'Solicitud'}</a>: {mensaje}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <section className="card form-section" aria-labelledby="sec-solicitante">
        <h2 id="sec-solicitante" className="form-section__title">
          1. Datos del solicitante
        </h2>

        <fieldset className="radio-group" id="tipo_persona">
          <legend className="field__label">
            Tipo de solicitante{' '}
            <span className="field__required" aria-hidden="true">
              *
            </span>
          </legend>
          <div className="radio-group__opciones">
            {config.tipos_persona.map((opcion) => (
              <label key={opcion.valor} className="radio">
                <input
                  type="radio"
                  name="tipo_persona"
                  value={opcion.valor}
                  checked={valores.tipo_persona === opcion.valor}
                  onChange={() => cambiarTipoPersona(opcion.valor)}
                />
                <span>{opcion.etiqueta}</span>
              </label>
            ))}
          </div>
          {errores.tipo_persona && <p className="field__error">{errores.tipo_persona}</p>}
        </fieldset>

        <div className="form-grid">
          <FormField
            id="tipo_documento_identidad"
            as="select"
            label="Tipo de documento de identidad"
            required
            value={valores.tipo_documento_identidad}
            onChange={cambiar}
            error={errores.tipo_documento_identidad}
          >
            {opcionesDocumento.map((opcion) => (
              <option key={opcion.valor} value={opcion.valor}>
                {opcion.etiqueta}
              </option>
            ))}
          </FormField>
          <FormField
            id="numero_documento"
            label="Número de documento"
            required
            value={valores.numero_documento}
            onChange={cambiar}
            error={errores.numero_documento}
            maxLength={20}
            inputMode="text"
            autoComplete="off"
          />
        </div>

        {config.verificacion_dni && !esJuridica && valores.tipo_documento_identidad === 'DNI' && (
          <div className="dni-verificar">
            <button type="button" className="btn btn--secondary" onClick={verificarDni} disabled={dni.estado === 'buscando'}>
              {dni.estado === 'buscando' ? (
                <Loader2 size={18} aria-hidden="true" className="spin" />
              ) : (
                <ShieldCheck size={18} aria-hidden="true" />
              )}
              {dni.estado === 'buscando' ? 'Buscando…' : 'Verificar DNI y completar mis datos'}
            </button>
            <p
              className={dni.estado === 'error' ? 'field__error' : 'field__hint'}
              role={dni.estado === 'error' ? 'alert' : 'status'}
              aria-live="polite"
            >
              {dni.mensaje}
            </p>
          </div>
        )}

        {esJuridica ? (
          <FormField
            id="razon_social"
            label="Razón social"
            required
            value={valores.razon_social}
            onChange={cambiar}
            error={errores.razon_social}
            maxLength={200}
            autoComplete="organization"
          />
        ) : (
          <div className="form-grid">
            <FormField
              id="nombres"
              label="Nombres"
              required
              value={valores.nombres}
              onChange={cambiar}
              error={errores.nombres}
              maxLength={150}
              autoComplete="given-name"
            />
            <FormField
              id="apellidos"
              label="Apellidos"
              required
              value={valores.apellidos}
              onChange={cambiar}
              error={errores.apellidos}
              maxLength={150}
              autoComplete="family-name"
            />
          </div>
        )}

        <div className="form-grid">
          <FormField
            id="email"
            type="email"
            label="Correo electrónico"
            required
            value={valores.email}
            onChange={cambiar}
            error={errores.email}
            maxLength={254}
            autoComplete="email"
          />
          <FormField
            id="telefono"
            type="tel"
            label="Teléfono o celular"
            value={valores.telefono}
            onChange={cambiar}
            error={errores.telefono}
            maxLength={20}
            autoComplete="tel"
          />
        </div>
      </section>

      <section className="card form-section" aria-labelledby="sec-documento">
        <h2 id="sec-documento" className="form-section__title">
          2. Documento que presentas
        </h2>
        <FormField
          id="tipo_documental"
          as="select"
          label="Tipo de documento"
          required
          value={valores.tipo_documental}
          onChange={cambiar}
          error={errores.tipo_documental}
        >
          <option value="">Selecciona una opción…</option>
          {tipos.map((tipo) => (
            <option key={tipo.codigo} value={tipo.codigo}>
              {tipo.nombre}
            </option>
          ))}
        </FormField>
        <FormField
          id="asunto"
          label="Asunto"
          required
          hint="Resume en una frase de qué trata tu documento."
          value={valores.asunto}
          onChange={cambiar}
          error={errores.asunto}
          maxLength={300}
        />
        <FormField
          id="descripcion"
          as="textarea"
          label="Descripción"
          hint={`${valores.descripcion.length} / 5000 caracteres`}
          rows={5}
          value={valores.descripcion}
          onChange={cambiar}
          error={errores.descripcion}
          maxLength={5000}
        />
      </section>

      <section className="card form-section" aria-labelledby="sec-adjuntos">
        <h2 id="sec-adjuntos" className="form-section__title">
          3. Adjuntos
        </h2>
        <FileUploader id="archivos" archivos={archivos} onChange={cambiarArchivos} config={config} errores={errores.archivos} />
      </section>

      <section className="card form-section" aria-labelledby="sec-declaraciones">
        <h2 id="sec-declaraciones" className="form-section__title">
          4. Declaraciones
        </h2>
        <Casilla
          id="acepta_politica_privacidad"
          checked={valores.acepta_politica_privacidad}
          onChange={cambiar}
          error={errores.acepta_politica_privacidad}
        >
          He leído y acepto la política de privacidad.{' '}
          <span className="check__nota">(Texto oficial pendiente de validación por la municipalidad.)</span>
        </Casilla>
        <Casilla
          id="declara_veracidad"
          checked={valores.declara_veracidad}
          onChange={cambiar}
          error={errores.declara_veracidad}
        >
          Declaro que la información que presento es veraz.{' '}
          <span className="check__nota">(Redacción provisional, pendiente de validación.)</span>
        </Casilla>
      </section>

      <div className="form-actions">
        <button type="submit" className="btn btn--primary btn--lg" disabled={enviando}>
          {enviando ? (
            <>
              <Loader2 size={20} aria-hidden="true" className="spin" />
              Enviando…
            </>
          ) : (
            <>
              <Send size={20} aria-hidden="true" />
              Enviar solicitud
            </>
          )}
        </button>
        <Link to="/" className="btn btn--secondary btn--lg">
          Cancelar
        </Link>
      </div>
    </form>
  );
}
