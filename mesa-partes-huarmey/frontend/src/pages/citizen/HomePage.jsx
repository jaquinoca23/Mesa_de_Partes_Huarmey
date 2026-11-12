import { Link } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, FilePlus2, Search, FileText, Paperclip, Receipt, Info, Landmark, MonitorSmartphone, ChevronRight } from 'lucide-react';
import '../../styles/home.css';

const PASOS = [
  { icono: FileText, titulo: 'Completa el formulario', texto: 'Ingresa tus datos de contacto, el asunto y una descripción clara de tu solicitud.' },
  { icono: Paperclip, titulo: 'Adjunta tus documentos', texto: 'Agrega tu documento principal y los archivos de respaldo de tu solicitud.' },
  { icono: Receipt, titulo: 'Conserva tu cargo', texto: 'Al completar el registro, guarda el cargo de recepción y tu número de expediente.' },
];

export default function HomePage() {
  return (
    <div className="citizen-home">
      <section className="portal-hero" aria-labelledby="portal-title">
        <div className="container portal-hero__inner">
          <div className="portal-hero__copy">
            <span className="portal-eyebrow"><span /> PORTAL DE ATENCIÓN CIUDADANA</span>
            <h1 id="portal-title">Tus trámites,<br /><span>más cerca de ti.</span></h1>
            <p>Presenta documentos y consulta tus expedientes en la Municipalidad Provincial de Huarmey desde un solo lugar.</p>
            <a className="portal-guide-link" href="#como-funciona">Conoce cómo realizar tu trámite <ArrowRight size={17} aria-hidden="true" /></a>
            <div className="portal-hero__signature"><Landmark size={19} aria-hidden="true" /><span>Municipalidad Provincial de Huarmey<br /><strong>Al servicio de nuestra ciudadanía</strong></span></div>
          </div>
          <div className="portal-services" aria-label="Servicios digitales">
            <div className="portal-services__heading"><span>¿Qué necesitas hacer hoy?</span><MonitorSmartphone size={20} aria-hidden="true" /></div>
            <Link className="service-card service-card--primary" to="/presentar">
              <div className="service-card__top"><span className="service-card__icon"><FilePlus2 size={25} aria-hidden="true" /></span><ArrowUpRight size={23} aria-hidden="true" /></div>
              <h2>Presentar un documento</h2>
              <p>Registra una nueva solicitud y adjunta tus documentos.</p>
              <span className="service-card__action">Iniciar trámite <ArrowRight size={17} aria-hidden="true" /></span>
            </Link>
            <Link className="service-card service-card--secondary" to="/consultar">
              <span className="service-card__icon"><Search size={24} aria-hidden="true" /></span>
              <div><h2>Consultar un expediente</h2><p>Revisa el estado de tu trámite.</p></div>
              <ChevronRight size={22} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>
      <section className="portal-steps" id="como-funciona" aria-labelledby="titulo-pasos">
        <div className="container">
          <div className="portal-section-heading"><div><span className="portal-label">GUÍA DEL CIUDADANO</span><h2 id="titulo-pasos">Tu solicitud, en tres pasos</h2></div><p>Prepara tus documentos y sigue estas indicaciones.</p></div>
          <ol className="portal-step-grid">
            {PASOS.map(({ icono: Icono, titulo, texto }, index) => (
              <li key={titulo} className="portal-step"><div className="portal-step__top"><span className="portal-step__icon"><Icono size={23} aria-hidden="true" /></span><span className="portal-step__number" aria-hidden="true">0{index + 1}</span></div><h3>{titulo}</h3><p>{texto}</p></li>
            ))}
          </ol>
          <aside className="portal-notice" aria-labelledby="titulo-info"><span className="portal-notice__icon"><Info size={21} aria-hidden="true" /></span><div><h2 id="titulo-info">Información sobre horarios y plazos</h2><p>Los horarios de atención y el cómputo de plazos se publicarán cuando cuenten con la validación oficial de la municipalidad.</p></div><span className="portal-notice__tag">Pendiente de validación</span></aside>
        </div>
      </section>
    </div>
  );
}
