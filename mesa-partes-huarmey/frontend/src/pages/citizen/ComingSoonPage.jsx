import { Link } from 'react-router-dom';
import { ArrowLeft, Construction } from 'lucide-react';

// Página provisional para secciones que se construirán en etapas posteriores.
export default function ComingSoonPage({ title, stage, description }) {
  return (
    <section className="section">
      <div className="container container--narrow">
        <div className="card card--center">
          <div className="card__icon">
            <Construction size={28} aria-hidden="true" />
          </div>
          <h1 className="card__title card__title--lg">{title}</h1>
          <p className="badge badge--stage">Disponible en la {stage}</p>
          <p className="card__text">{description}</p>
          <Link to="/" className="btn btn--primary">
            <ArrowLeft size={18} aria-hidden="true" />
            Volver al inicio
          </Link>
        </div>
      </div>
    </section>
  );
}
