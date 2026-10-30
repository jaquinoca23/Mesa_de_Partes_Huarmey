import { Routes, Route } from 'react-router-dom';
import CitizenLayout from '../layouts/CitizenLayout.jsx';
import AdminLayout from '../layouts/AdminLayout.jsx';
import RutaProtegida from './RutaProtegida.jsx';
import HomePage from '../pages/citizen/HomePage.jsx';
import PresentarPage from '../pages/citizen/PresentarPage.jsx';
import ConsultarPage from '../pages/citizen/ConsultarPage.jsx';
import CargoPage from '../pages/citizen/CargoPage.jsx';
import NotFoundPage from '../pages/citizen/NotFoundPage.jsx';
import LoginPage from '../pages/admin/LoginPage.jsx';
import InicioPanelPage from '../pages/admin/InicioPanelPage.jsx';
import RegistrarDocumentoPage from '../pages/admin/RegistrarDocumentoPage.jsx';
import BandejaPage from '../pages/admin/BandejaPage.jsx';
import ExpedienteDetallePage from '../pages/admin/ExpedienteDetallePage.jsx';
import ReportesPage from '../pages/admin/ReportesPage.jsx';
import AuditoriaPage from '../pages/admin/AuditoriaPage.jsx';
import UsuariosPage from '../pages/admin/UsuariosPage.jsx';
import AreasPage from '../pages/admin/AreasPage.jsx';
import TiposDocumentalesPage from '../pages/admin/TiposDocumentalesPage.jsx';
import EstadosPage from '../pages/admin/EstadosPage.jsx';

// Portal ciudadano (público) y panel del personal (/panel, con sesión).
// Ocultar una opción del menú NO es seguridad: el servidor exige los permisos en cada petición.
export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<CitizenLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/presentar" element={<PresentarPage />} />
        <Route path="/consultar" element={<ConsultarPage />} />
        <Route path="/cargo" element={<CargoPage />} />
      </Route>

      <Route path="/panel/login" element={<LoginPage />} />
      <Route path="/panel" element={<RutaProtegida />}>
        <Route element={<AdminLayout />}>
          <Route index element={<InicioPanelPage />} />
          <Route element={<RutaProtegida permiso="expedientes.add_expediente" />}>
            <Route path="registrar-documento" element={<RegistrarDocumentoPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="expedientes.view_expediente" />}>
            <Route path="expedientes" element={<BandejaPage />} />
            <Route path="expedientes/:uuid" element={<ExpedienteDetallePage />} />
          </Route>
          <Route element={<RutaProtegida permiso="expedientes.ver_reportes" />}>
            <Route path="reportes" element={<ReportesPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="auditoria.view_registroauditoria" />}>
            <Route path="auditoria" element={<AuditoriaPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="usuarios.view_usuario" />}>
            <Route path="usuarios" element={<UsuariosPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="organizacion.view_area" />}>
            <Route path="areas" element={<AreasPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="catalogos.view_tipodocumental" />}>
            <Route path="tipos-documentales" element={<TiposDocumentalesPage />} />
          </Route>
          <Route element={<RutaProtegida permiso="catalogos.view_estadoexpediente" />}>
            <Route path="estados" element={<EstadosPage />} />
          </Route>
        </Route>
      </Route>

      <Route element={<CitizenLayout />}>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
