import CrudSimple from '../../features/panel/CrudSimple.jsx';

const CAMPOS = [
  { nombre: 'codigo', etiqueta: 'Código', requerido: true },
  { nombre: 'nombre', etiqueta: 'Nombre', requerido: true },
  { nombre: 'descripcion', etiqueta: 'Qué significa para el ciudadano', tipo: 'textarea' },
  { nombre: 'orden', etiqueta: 'Orden', tipo: 'number', inicial: 0 },
  { nombre: 'es_inicial', etiqueta: 'Estado inicial (solo puede haber uno)', tipo: 'checkbox' },
  { nombre: 'es_final', etiqueta: 'Estado final (cierra el trámite)', tipo: 'checkbox' },
  { nombre: 'es_provisional', etiqueta: 'Provisional', tipo: 'checkbox', inicial: true },
  { nombre: 'activo', etiqueta: 'Activo', tipo: 'checkbox', inicial: true },
];
const COLUMNAS = [
  { clave: 'orden', titulo: 'Orden' },
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'es_inicial', titulo: 'Inicial' },
  { clave: 'es_final', titulo: 'Final' },
  { clave: 'activo', titulo: 'Activo' },
];

export default function EstadosPage() {
  return (
    <CrudSimple
      titulo="Estados de expediente"
      endpoint="/panel/estados/"
      campos={CAMPOS}
      columnas={COLUMNAS}
      permisoAgregar="catalogos.add_estadoexpediente"
      permisoCambiar="catalogos.change_estadoexpediente"
      nota="Estados provisionales, por validar con el procedimiento documentario vigente."
    />
  );
}
