import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { ClipboardList, Building2, FileText, ScrollText, Home, Inbox, ListChecks, LogOut, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

// Cada opción del menú aparece solo si el usuario tiene el permiso de "ver" esa sección.
const MENU = [
  { a: '/panel', texto: 'Inicio', icono: Home, fin: true },
  { a: '/panel/expedientes', texto: 'Expedientes', icono: Inbox, permiso: 'expedientes.view_expediente' },
  { a: '/panel/reportes', texto: 'Reportes', icono: ClipboardList, permiso: 'expedientes.ver_reportes' },
  { a: '/panel/auditoria', texto: 'Auditoría', icono: ScrollText, permiso: 'auditoria.view_registroauditoria' },
  { a: '/panel/usuarios', texto: 'Usuarios', icono: Users, permiso: 'usuarios.view_usuario' },
  { a: '/panel/areas', texto: 'Áreas', icono: Building2, permiso: 'organizacion.view_area' },
  { a: '/panel/tipos-documentales', texto: 'Tipos de documento', icono: FileText, permiso: 'catalogos.view_tipodocumental' },
  { a: '/panel/estados', texto: 'Estados', icono: ListChecks, permiso: 'catalogos.view_estadoexpediente' },
];

export default function AdminLayout() {
  const { usuario, salir, tiene } = useAuth();
  const navegar = useNavigate();

  async function cerrar() {
    await salir();
    navegar('/panel/login', { replace: true });
  }

  return (
    <div className="admin">
      <aside className="admin__menu">
        <p className="admin__marca">Mesa de Partes · Panel</p>
        <nav aria-label="Menú del panel">
          {MENU.filter((m) => !m.permiso || tiene(m.permiso)).map(({ a, texto, icono: Icono, fin }) => (
            <NavLink key={a} to={a} end={fin} className="admin__enlace">
              <Icono size={18} aria-hidden="true" />
              {texto}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="admin__cuerpo">
        <header className="admin__barra">
          <span>
            <strong>{usuario.nombre}</strong>
            {usuario.roles.length > 0 && <small> · {usuario.roles.join(', ')}</small>}
          </span>
          <button type="button" className="btn btn--secondary" onClick={cerrar}>
            <LogOut size={16} aria-hidden="true" /> Cerrar sesión
          </button>
        </header>
        <main className="admin__contenido">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
