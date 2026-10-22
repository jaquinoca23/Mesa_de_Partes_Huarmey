import CrudSimple from '../../features/panel/CrudSimple.jsx';
import { api } from '../../services/api.js';

// Los valores deben coincidir con Area.TipoArea del backend (el servidor vuelve a validarlos).
const TIPOS = [
  ['MUNICIPALIDAD', 'Municipalidad'],
  ['ORGANO', 'Órgano'],
  ['GERENCIA', 'Gerencia'],
  ['SUBGERENCIA', 'Subgerencia'],
  ['OFICINA', 'Oficina'],
  ['UNIDAD', 'Unidad'],
  ['OTRO', 'Otra dependencia'],
].map(([valor, etiqueta]) => ({ valor, etiqueta }));

const CAMPOS = [
  { nombre: 'nombre', etiqueta: 'Nombre', requerido: true },
  { nombre: 'siglas', etiqueta: 'Siglas' },
  { nombre: 'tipo', etiqueta: 'Tipo', tipo: 'select', requerido: true, opciones: TIPOS },
  {
    nombre: 'padre',
    etiqueta: 'Depende de',
    tipo: 'select',
    nulo: true,
    cargarOpciones: async () => (await api.get('/panel/areas/')).map((a) => ({ valor: a.id, etiqueta: a.nombre })),
  },
  { nombre: 'activo', etiqueta: 'Activa', tipo: 'checkbox', inicial: true },
  { nombre: 'es_ficticia', etiqueta: 'Dato ficticio (desmarcar solo si está confirmada por el ROF vigente)', tipo: 'checkbox', inicial: true },
];
const COLUMNAS = [
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'tipo', titulo: 'Tipo' },
  { clave: 'padre_nombre', titulo: 'Depende de', render: (f) => f.padre_nombre || '—' },
  { clave: 'activo', titulo: 'Activa' },
  { clave: 'es_ficticia', titulo: 'Ficticia' },
];

export default function AreasPage() {
  return (
    <CrudSimple
      titulo="Áreas"
      endpoint="/panel/areas/"
      campos={CAMPOS}
      columnas={COLUMNAS}
      permisoAgregar="organizacion.add_area"
      permisoCambiar="organizacion.change_area"
      nota="Estructura provisional: la definitiva depende del ROF vigente de la municipalidad (pendiente de validar)."
    />
  );
}
