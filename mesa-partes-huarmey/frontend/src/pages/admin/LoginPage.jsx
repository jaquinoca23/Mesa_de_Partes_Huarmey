import { useState } from 'react';
import { Navigate, useLocation, useNavigate, Link } from 'react-router-dom';
import { Loader2, LogIn, ArrowLeft, ShieldCheck, Eye, EyeOff } from 'lucide-react';
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
  const [mostrarPassword, setMostrarPassword] = useState(false);

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
      <div className="login__panel">
        <aside className="login__institucion" aria-label="Municipalidad Provincial de Huarmey">
          <div className="login__marca">
            <img src="/images/logo-huarmey.png" alt="Escudo de Huarmey" />
            <span>Municipalidad Provincial<br /><strong>de Huarmey</strong></span>
          </div>
          <div className="login__presentacion">
            <span className="login__etiqueta">PORTAL DEL PERSONAL</span>
            <h2>Una gestión más ágil.<br />Un mejor servicio.</h2>
            <p>Accede al espacio de trabajo de la Mesa de Partes Digital para gestionar la atención de documentos.</p>
          </div>
          <span className="login__demo">Entorno de demostración</span>
        </aside>
      <form className="login__caja" onSubmit={enviar} noValidate aria-labelledby="login-title" aria-busy={enviando}>
        <div className="login__encabezado">
          <span className="login__icono"><ShieldCheck size={25} aria-hidden="true" /></span>
          <h1 id="login-title">Acceso del personal</h1>
          <p>Ingresa con tu cuenta para continuar al panel de gestión.</p>
        </div>
        <FormField id="username" label="Usuario" placeholder="Ingresa tu usuario" required value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" maxLength={150} />
        <div className="login__password">
          <FormField id="password" type={mostrarPassword ? 'text' : 'password'} label="Contraseña" placeholder="Ingresa tu contraseña" required value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" maxLength={128} />
          <button type="button" className="login__mostrar" onClick={() => setMostrarPassword(!mostrarPassword)} aria-label={mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'} aria-pressed={mostrarPassword} aria-controls="password">
            {mostrarPassword ? <EyeOff size={19} aria-hidden="true" /> : <Eye size={19} aria-hidden="true" />}
          </button>
        </div>
        {error && (
          <p className="field__error login__error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" className="btn btn--primary btn--lg" disabled={enviando}>
          {enviando ? <Loader2 size={18} aria-hidden="true" className="spin" /> : <LogIn size={18} aria-hidden="true" />}
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
        <p className="login__volver">
          <Link to="/"><ArrowLeft size={16} aria-hidden="true" /> Volver al portal ciudadano</Link>
        </p>
      </form>
      </div>
      <p className="login__pie">Mesa de Partes Digital · Municipalidad Provincial de Huarmey</p>
    </main>
  );
}
