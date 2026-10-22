import { Link } from 'react-router-dom';

// Se muestra cuando la dirección escrita no existe.
export default function NotFoundPage() {
  return (
    <section className="section">
      <div className="container container--narrow">
        <div className="card card--center">
          <h1 className="card__title card__title--lg">Página no encontrada</h1>
          <p className="card__text">
            La dirección que buscas no existe o fue movida.
          </p>
          <Link to="/" className="btn btn--primary">
            Volver al inicio
          </Link>
        </div>
      </div>
    </section>
  );
}
