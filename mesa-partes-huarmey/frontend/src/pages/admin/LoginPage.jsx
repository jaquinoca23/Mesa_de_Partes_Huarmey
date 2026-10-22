import { useState } from 'react';
import { Navigate, useLocation, useNavigate, Link } from 'react-router-dom';
import { Loader2, LogIn } from 'lucide-react';
import FormField from '../../components/FormField.jsx';
import { useAuth } from '../../context/AuthContext.jsx';

export default function LoginPage() {
  const { usuario, cargando, entrar } = useAuth();
  const navegar = useNavigate();
  const ubicacion = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  if (!cargando && usuario) return <Navigate to="/panel" replace />;

  async function enviar(evento) {
    evento.preventDefault();
    if (enviando) return;
    setError('');
    if (!username.trim() || !password) {
      setError('Ingresa tu usuario y tu contraseña.');
      return;
    }
    setEnviando(true);
    try {
      await entrar(username.trim(), password);
      navegar(ubicacion.state?.desde || '/panel', { replace: true });
    } catch (e) {
      setError(e.message || 'No se pudo iniciar sesión.');
      setPassword('');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login">
      <form className="card login__caja" onSubmit={enviar} noValidate>
        <h1 className="card__title">Acceso del personal</h1>
        <p>Mesa de Partes Digital — Municipalidad Provincial de Huarmey (demostración)</p>
        <FormField id="username" label="Usuario" required value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" maxLength={150} />
        <FormField id="password" type="password" label="Contraseña" required value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" maxLength={128} />
        {error && (
          <p className="field__error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" className="btn btn--primary btn--lg" disabled={enviando}>
          {enviando ? <Loader2 size={18} aria-hidden="true" className="spin" /> : <LogIn size={18} aria-hidden="true" />}
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
        <p className="login__volver">
          <Link to="/">Volver al portal ciudadano</Link>
        </p>
      </form>
    </main>
  );
}
