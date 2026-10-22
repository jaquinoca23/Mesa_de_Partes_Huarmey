# Etapa 6 — Inicio de sesión, roles y panel de administración

## Qué incluye
- Inicio y cierre de sesión por cookie de sesión + protección CSRF (`/api/auth/csrf|login|logout|me/`), límite de 10 intentos/minuto, mensaje genérico si falla, auditoría de accesos.
- Roles de ejemplo (provisionales): Administrador, Mesa de partes, Funcionario de área, Consulta y reportes.
- Permisos exigidos **en el servidor** (Django): ocultar un botón en React no da seguridad.
- Panel React en `/panel`: usuarios (crear/editar/desactivar, roles, área, contraseña con validación), áreas (con control de ciclos), tipos de documento y estados (un solo estado inicial).
- Nada se elimina (solo se desactiva). Cada cambio queda en la auditoría.
- Un no-administrador no puede crear administradores ni modificar cuentas de administradores.

## Pasos (PowerShell)
1. Copia el contenido del zip sobre tu proyecto.
2. Backend (terminal 1):
   ```
   cd backend
   .venv\Scripts\Activate.ps1
   python manage.py makemigrations
   python manage.py migrate
   python manage.py cargar_datos_ficticios
   python manage.py crear_roles_demo
   python manage.py test
   python manage.py runserver
   ```
   `crear_roles_demo` muestra UNA sola vez la contraseña aleatoria de cada usuario demo: anótalas.
   (Para elegir una: `python manage.py crear_roles_demo --password "TuClaveLarga-2026!"`.)
3. Frontend (terminal 2): `cd frontend` → `npm run dev`
4. Abre http://localhost:5173/panel/login e ingresa con `admin.demo`.
5. Prueba: crear un usuario, cambiar su rol, entrar con `area1.demo` y ver que NO aparecen Usuarios/Áreas.

## Usuarios demo
| Usuario | Rol |
|---|---|
| admin.demo | Administrador |
| mesa.demo | Mesa de partes |
| area1.demo / area2.demo | Funcionario de área |
| auditor.demo | Consulta y reportes |

## Errores comunes
- *"Usuario o contraseña incorrectos"*: revisa la clave que mostró `crear_roles_demo`; si la perdiste, borra el usuario en http://127.0.0.1:8000/admin (con `createsuperuser`) o ejecútalo con `--password` tras eliminarlo.
- *403 al guardar*: recarga la página (se renueva el token CSRF) y confirma que Django está encendido.
- *Menú vacío tras entrar*: falta ejecutar `crear_roles_demo` (los roles no tienen permisos).
