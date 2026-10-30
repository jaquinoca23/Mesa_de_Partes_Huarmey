import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Landmark, LogIn } from 'lucide-react';

// Ruta donde se colocará el logo oficial (carpeta frontend/public/images/).
const LOGO_URL = '/images/logo-huarmey.png';

/**
 * Cabecera institucional reutilizable.
 * - Si existe el archivo del logo oficial, lo muestra tal cual.
 * - Si no existe, muestra un espacio reservado claramente temporal.
 *   (No se dibuja ni se inventa ningún logotipo.)
 */
export default function BrandHeader() {
  const [logoDisponible, setLogoDisponible] = useState(true);

  return (
    <header className="brand-header">
      <div className="container brand-header__inner">
        <Link to="/" className="brand-header__brand" aria-label="Ir al inicio">
          {logoDisponible ? (
            <img
              src={LOGO_URL}
              alt="Logo de la Municipalidad Provincial de Huarmey"
              className="brand-header__logo"
              onError={() => setLogoDisponible(false)}
            />
          ) : (
            <div
              className="brand-header__logo-placeholder"
              role="img"
              aria-label="Espacio reservado para el logo oficial (pendiente)"
            >
              <Landmark size={22} aria-hidden="true" />
              <span>LOGO OFICIAL (pendiente)</span>
            </div>
          )}

          <div className="brand-header__text">
            <span className="brand-header__entity">
              Municipalidad Provincial de Huarmey
            </span>
            <span className="brand-header__system">Mesa de Partes Digital</span>
          </div>
        </Link>

        <div className="brand-header__actions">
          <span className="badge badge--demo" title="Versión de demostración con datos ficticios">
            Demostración
          </span>
          <Link to="/panel/login" className="brand-header__staff">
            <LogIn size={18} aria-hidden="true" />
            Acceso al personal
          </Link>
        </div>
      </div>
    </header>
  );
}
