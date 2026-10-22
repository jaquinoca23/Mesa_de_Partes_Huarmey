import { Outlet } from 'react-router-dom';
import BrandHeader from '../components/BrandHeader.jsx';
import Footer from '../components/Footer.jsx';

// Estructura común de todas las páginas del portal ciudadano:
// cabecera arriba, contenido en el medio (Outlet) y pie abajo.
export default function CitizenLayout() {
  return (
    <div className="page-shell">
      <a href="#contenido" className="skip-link">
        Saltar al contenido
      </a>
      <BrandHeader />
      <main id="contenido" className="page-shell__main">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
