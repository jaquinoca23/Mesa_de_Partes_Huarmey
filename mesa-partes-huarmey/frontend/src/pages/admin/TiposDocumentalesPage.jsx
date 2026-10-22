import CrudSimple from '../../features/panel/CrudSimple.jsx';

const CAMPOS = [
  { nombre: 'codigo', etiqueta: 'Código', requerido: true, ayuda: 'Identificador interno sin espacios (ej. solicitud).' },
  { nombre: 'nombre', etiqueta: 'Nombre', requerido: true },
  { nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'textarea' },
  { nombre: 'orden', etiqueta: 'Orden', tipo: 'number', inicial: 0 },
  { nombre: 'es_procedimiento_tupa', etiqueta: 'Corresponde a un procedimiento del TUPA vigente (por validar)', tipo: 'checkbox' },
  { nombre: 'es_provisional', etiqueta: 'Provisional', tipo: 'checkbox', inicial: true },
  { nombre: 'activo', etiqueta: 'Activo (visible para el ciudadano)', tipo: 'checkbox', inicial: true },
];
const COLUMNAS = [
  { clave: 'orden', titulo: 'Orden' },
  { clave: 'codigo', titulo: 'Código' },
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'es_provisional', titulo: 'Provisional' },
  { clave: 'activo', titulo: 'Activo' },
];

export default function TiposDocumentalesPage() {
  return (
    <CrudSimple
      titulo="Tipos de documento"
      endpoint="/panel/tipos-documentales/"
      campos={CAMPOS}
      columnas={COLUMNAS}
      permisoAgregar="catalogos.add_tipodocumental"
      permisoCambiar="catalogos.change_tipodocumental"
    />
  );
}
