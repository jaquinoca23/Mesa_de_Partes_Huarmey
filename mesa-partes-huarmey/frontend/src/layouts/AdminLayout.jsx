import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { ClipboardList, Building2, FileText, FilePlus2, ScrollText, Home, Inbox, ListChecks, LogOut, Users, ChevronRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

// Cada opción del menú aparece solo si el usuario tiene el permiso de "ver" esa sección.
const MENU = [
  { a: '/panel', texto: 'Inicio', icono: Home, fin: true },
  { a: '/panel/registrar-documento', texto: 'Registrar documento', icono: FilePlus2, permiso: 'expedientes.add_expediente' },
  { a: '/panel/expedientes', texto: 'Expedientes', icono: Inbox, permiso: 'expedientes.view_expediente' },
  { a: '/panel/reportes', texto: 'Reportes', icono: ClipboardList, permiso: 'expedientes.ver_reportes' },
  { a: '/panel/auditoria', texto: 'Auditoría', icono: ScrollText, permiso: 'auditoria.view_registroauditoria' },
  { a: '/panel/usuarios', texto: 'Usuarios del personal', icono: Users, permiso: 'usuarios.view_usuario' },
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
        <div className="admin__marca"><span className="admin__escudo"><img src="/images/logo-huarmey.png" alt="" /></span><span>Municipalidad de Huarmey<strong>Mesa de Partes</strong><small>GESTIÓN DOCUMENTAL</small></span></div>
        <div className="admin__portal"><ShieldCheck size={14} aria-hidden="true" /> Portal del personal</div>
        <p className="admin__menu-label">PRINCIPAL</p>
        <nav aria-label="Menú del panel">
          {MENU.filter((m) => !m.permiso || tiene(m.permiso)).map(({ a, texto, icono: Icono, fin }) => (
            <NavLink key={a} to={a} end={fin} className="admin__enlace">
              <span className="admin__nav-icono"><Icono size={18} aria-hidden="true" /></span>
              <span className="admin__nav-texto">{texto}</span>
              <ChevronRight className="admin__nav-flecha" size={15} aria-hidden="true" />
            </NavLink>
          ))}
        </nav>
        <div className="admin__usuario-pie"><div className="admin__usuario-tarjeta"><span className="admin__usuario-avatar" aria-hidden="true">{usuario.nombre.trim().split(/\s+/).slice(0, 2).map((n) => n[0]).join('')}</span><span className="admin__usuario-datos"><strong>{usuario.nombre}</strong><small>{usuario.roles.join(', ') || 'Personal municipal'}</small></span></div><div className="admin__institucion-pie"><Building2 size={13} aria-hidden="true" /> Municipalidad de Huarmey</div></div>
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
