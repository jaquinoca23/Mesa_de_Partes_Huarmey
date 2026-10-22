import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, Printer, Search } from 'lucide-react';
import CargoRecepcion from '../../components/CargoRecepcion.jsx';
import { leerCargo } from '../../utils/cargoStorage.js';

// Pantalla que se muestra DESPUÉS de que el servidor confirmó el registro.
export default function CargoPage() {
  const cargo = leerCargo();

  useEffect(() => {
    document.title = 'Cargo de recepción';
  }, []);

  if (!cargo) {
    return (
      <section className="section">
        <div className="container container--narrow">
          <div className="card card--center">
            <h1 className="card__title card__title--lg">No hay un cargo para mostrar</h1>
            <p className="card__text">
              El cargo solo se muestra justo después de registrar una solicitud. Si ya la registraste, usa tu número
              de expediente y tu código de verificación para consultarla.
            </p>
            <Link to="/consultar" className="btn btn--primary">
              Consultar un expediente
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="container container--form">
        <div className="result result--ok no-imprimir" role="status">
          <CheckCircle2 size={36} aria-hidden="true" className="result__icon" />
          <h1 className="result__title">Tu solicitud fue registrada</h1>
          <p>
            <strong>Guarda tu número de expediente y tu código de verificación.</strong> Los necesitarás para consultar
            tu trámite. También te enviamos un correo (en la versión de demostración se imprime en la terminal).
          </p>
        </div>

        <CargoRecepcion cargo={cargo} />

        <div className="result__acciones no-imprimir">
          <button type="button" className="btn btn--primary" onClick={() => window.print()}>
            <Printer size={18} aria-hidden="true" />
            Imprimir o guardar como PDF
          </button>
          <Link to="/consultar" className="btn btn--secondary">
            <Search size={18} aria-hidden="true" />
            Consultar mi expediente
          </Link>
          <Link to="/" className="btn btn--secondary">
            Ir al inicio
          </Link>
        </div>
      </div>
    </section>
  );
}
