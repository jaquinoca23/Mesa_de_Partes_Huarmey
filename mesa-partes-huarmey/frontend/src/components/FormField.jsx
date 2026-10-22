/**
 * Campo de formulario accesible: etiqueta + ayuda + control + mensaje de error.
 *
 * - "as" indica el tipo de control: 'input' (por defecto), 'select' o 'textarea'.
 * - Todo lo demás que se pase (type, value, onChange, maxLength...) va directo al control.
 * - Los lectores de pantalla leen la ayuda y el error gracias a aria-describedby.
 */
export default function FormField({
  id,
  label,
  required = false,
  hint,
  error,
  as: Control = 'input',
  children,
  ...resto
}) {
  const idAyuda = hint ? `${id}-ayuda` : undefined;
  const idError = error ? `${id}-error` : undefined;
  const describedBy = [idAyuda, idError].filter(Boolean).join(' ') || undefined;

  return (
    <div className={`field${error ? ' field--error' : ''}`}>
      <label htmlFor={id} className="field__label">
        {label}
        {required ? (
          <span className="field__required" aria-hidden="true">
            {' '}
            *
          </span>
        ) : (
          <span className="field__optional"> (opcional)</span>
        )}
      </label>
      {hint && (
        <p id={idAyuda} className="field__hint">
          {hint}
        </p>
      )}
      <Control
        id={id}
        name={id}
        className="field__control"
        aria-required={required ? 'true' : undefined}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        {...resto}
      >
        {children}
      </Control>
      {error && (
        <p id={idError} className="field__error">
          {error}
        </p>
      )}
    </div>
  );
}
