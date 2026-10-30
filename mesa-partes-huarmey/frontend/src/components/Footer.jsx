import BackendStatus from './BackendStatus.jsx';

// Pie de página del portal ciudadano.
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer__inner">
        <p>
          <strong>Mesa de Partes Digital</strong> · Propuesta tecnológica para la
          Municipalidad Provincial de Huarmey
        </p>
        <p className="site-footer__note">
          Versión de demostración en desarrollo. Todos los datos mostrados son
          ficticios. La información institucional (horarios, plazos, áreas y
          procedimientos) está pendiente de validación oficial.
        </p>
        <BackendStatus />
      </div>
    </footer>
  );
}
