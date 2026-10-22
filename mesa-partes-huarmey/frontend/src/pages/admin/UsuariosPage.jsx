import CrudSimple from '../../features/panel/CrudSimple.jsx';
import { api } from '../../services/api.js';

// Se definen FUERA del componente para que no cambien en cada pintado.
const CAMPOS = [
  { nombre: 'username', etiqueta: 'Usuario', requerido: true },
  { nombre: 'first_name', etiqueta: 'Nombres', requerido: true },
  { nombre: 'last_name', etiqueta: 'Apellidos', requerido: true },
  { nombre: 'email', etiqueta: 'Correo electrónico', tipo: 'email', requerido: true },
  { nombre: 'cargo', etiqueta: 'Cargo' },
  {
    nombre: 'area',
    etiqueta: 'Área',
    tipo: 'select',
    nulo: true,
    cargarOpciones: async () => (await api.get('/panel/areas/')).map((a) => ({ valor: a.id, etiqueta: a.nombre })),
  },
  { nombre: 'roles', etiqueta: 'Roles', tipo: 'multi', cargarOpciones: () => api.get('/panel/roles/') },
  { nombre: 'password', etiqueta: 'Contraseña', tipo: 'password', requerido: true, ayuda: 'Mínimo 8 caracteres; no puede ser común ni solo números.' },
  { nombre: 'is_active', etiqueta: 'Usuario activo', tipo: 'checkbox', inicial: true },
];
const COLUMNAS = [
  { clave: 'username', titulo: 'Usuario' },
  { clave: 'nombre', titulo: 'Nombre', render: (f) => `${f.first_name} ${f.last_name}`.trim() || '—' },
  { clave: 'area_nombre', titulo: 'Área', render: (f) => f.area_nombre || '—' },
  { clave: 'roles', titulo: 'Roles' },
  { clave: 'is_active', titulo: 'Activo' },
];

export default function UsuariosPage() {
  return (
    <CrudSimple
      titulo="Usuarios"
      endpoint="/panel/usuarios/"
      campos={CAMPOS}
      columnas={COLUMNAS}
      permisoAgregar="usuarios.add_usuario"
      permisoCambiar="usuarios.change_usuario"
      nota="Los usuarios no se eliminan: se desactivan para conservar la trazabilidad."
    />
  );
}
