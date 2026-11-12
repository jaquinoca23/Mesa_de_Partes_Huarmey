import CrudSimple from '../../features/panel/CrudSimple.jsx';
import { api } from '../../services/api.js';

// Se definen FUERA del componente para que no cambien en cada pintado.
const CAMPOS = [
  { nombre: 'dni', etiqueta: 'DNI', requerido: true, ayuda: '8 dígitos. No se permite repetir el DNI de otro usuario.' },
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
    cargarOpciones: async () => (await api.get('/panel/areas/')).filter((a) => a.activo).map((a) => ({ valor: a.id, etiqueta: a.nombre })),
  },
  { nombre: 'roles', etiqueta: 'Roles', tipo: 'multi', inicial: ['Mesa de partes'], cargarOpciones: () => api.get('/panel/roles/') },
  { nombre: 'password', etiqueta: 'Contraseña', tipo: 'password', requerido: true, ayuda: 'Mínimo 8 caracteres; no puede ser común ni solo números.' },
  { nombre: 'is_active', etiqueta: 'Usuario activo', tipo: 'checkbox', inicial: true },
];
const COLUMNAS = [
  { clave: 'dni', titulo: 'DNI' },
  { clave: 'username', titulo: 'Usuario' },
  { clave: 'nombre', titulo: 'Nombre', render: (f) => `${f.first_name} ${f.last_name}`.trim() || '—' },
  { clave: 'area_nombre', titulo: 'Área', render: (f) => f.area_nombre || '—' },
  { clave: 'roles', titulo: 'Roles' },
  { clave: 'is_active', titulo: 'Activo' },
];

export default function UsuariosPage() {
  return (
    <CrudSimple
      titulo="Usuarios del personal"
      endpoint="/panel/usuarios/"
      campos={CAMPOS}
      columnas={COLUMNAS}
      permisoAgregar="usuarios.add_usuario"
      permisoCambiar="usuarios.change_usuario"
      nota="Crea una cuenta con DNI, usuario y contraseña. El rol Mesa de partes permite registrar documentos. Las cuentas se guardan en la base de datos y pueden desactivarse sin perder su historial."
    />
  );
}
