import { Link } from 'react-router-dom';
import {
  FilePlus2,
  Search,
  FileText,
  Paperclip,
  Receipt,
  Info,
} from 'lucide-react';

// Pasos orientativos para el ciudadano (texto provisional, sin plazos oficiales).
const PASOS = [
  {
    icono: FileText,
    titulo: '1. Completa el formulario',
    texto: 'Indica tus datos de contacto, el asunto y una descripción de tu solicitud.',
  },
  {
    icono: Paperclip,
    titulo: '2. Adjunta tus documentos',
    texto: 'Puedes agregar archivos de respaldo. Los tipos y tamaños permitidos se definirán más adelante.',
  },
  {
    icono: Receipt,
    titulo: '3. Guarda tu cargo',
    texto: 'Al registrarse correctamente recibirás un cargo de recepción con tu número de expediente.',
  },
];

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="container hero__inner">
          <p className="hero__eyebrow">Portal ciudadano</p>
          <h1 className="hero__title">Mesa de Partes Digital</h1>
          <p className="hero__subtitle">
            Presenta tus documentos a la Municipalidad Provincial de Huarmey y
            consulta el estado de tus trámites desde cualquier dispositivo.
          </p>

          <div className="hero__actions">
            <Link to="/presentar" className="btn btn--light btn--lg">
              <FilePlus2 size={20} aria-hidden="true" />
              Presentar un documento
            </Link>
            <Link to="/consultar" className="btn btn--outline-light btn--lg">
              <Search size={20} aria-hidden="true" />
              Consultar un expediente
            </Link>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="titulo-pasos">
        <div className="container">
          <h2 id="titulo-pasos" className="section__title">
            ¿Cómo funciona?
          </h2>
          <div className="grid grid--3">
            {PASOS.map(({ icono: Icono, titulo, texto }) => (
              <article key={titulo} className="card">
                <div className="card__icon">
                  <Icono size={24} aria-hidden="true" />
                </div>
                <h3 className="card__title">{titulo}</h3>
                <p className="card__text">{texto}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section section--tight" aria-labelledby="titulo-info">
        <div className="container">
          <div className="notice" role="note">
            <Info size={22} aria-hidden="true" className="notice__icon" />
            <div>
              <h2 id="titulo-info" className="notice__title">
                Horarios y plazos
              </h2>
              <p>
                La información sobre horarios de atención y cómputo de plazos se
                publicará aquí únicamente cuando haya sido validada oficialmente
                por la Municipalidad Provincial de Huarmey.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
