# Guía paso a paso (Windows + PowerShell + VS Code)

Sigue los pasos en orden. Necesitas **dos terminales** abiertas a la vez (backend y frontend). En VS Code: menú Terminal → Nuevo terminal.

## 0. Antes de empezar (una sola vez)
Instala: Python 3.12, Node.js 20 o superior, PostgreSQL (con pgAdmin 4) y VS Code. Comprueba en PowerShell:
```
python --version
node --version
npm --version
```
Para PostgreSQL sigue `database/README.md` (crear la base `mesa_partes_huarmey` y el usuario `mesa_partes_user`). *Alternativa con Docker:* `infra/README.md`.

## 1. Copiar los archivos
Descomprime el zip **sobre** tu carpeta del proyecto (acepta reemplazar). No borres tu carpeta `backend\.venv`, tu `backend\.env` ni tus archivos `migrations` ya generados.

## 2. Configurar el backend (una sola vez)
```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Abre `backend\.env` y completa: `DB_PASSWORD` (la contraseña de PostgreSQL) y, si quieres, una `DJANGO_SECRET_KEY` propia. Si PowerShell no deja activar el entorno: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

> Si ya tenías el backend funcionando, salta los pasos `python -m venv` y `Copy-Item`; solo agrega las variables nuevas de `.env.example` si quieres cambiarlas (todas son opcionales).

## 3. Crear las tablas y los datos de prueba
Con el entorno activado (se ve `(.venv)` al inicio de la línea), dentro de `backend`:
```
python manage.py makemigrations
python manage.py migrate
python manage.py cargar_datos_ficticios
python manage.py crear_roles_demo
```
`crear_roles_demo` imprime **una sola vez** la contraseña de cada usuario de prueba. **Anótalas.** (Si prefieres una: `python manage.py crear_roles_demo --password "TuClaveLarga-2026!"`.)

## 4. Ejecutar las pruebas automáticas
```
python manage.py test
```
Debe terminar con `OK`. Si aparece un error, copia el mensaje completo y envíalo para corregirlo.

## 5. Encender el backend (Terminal 1)
```
python manage.py runserver
```
Déjalo abierto. Prueba: http://127.0.0.1:8000/api/health/ debe mostrar `"status": "ok"`.

## 6. Encender el frontend (Terminal 2)
```
cd frontend
npm install
npm run dev
```
Abre http://localhost:5173. El indicador del pie de página debe decir "Backend conectado" (solo en desarrollo).

## 7. Recorrido de prueba
1. **Ciudadano:** http://localhost:5173/presentar → llena el formulario con datos ficticios → adjunta un PDF pequeño → Enviar. Verás el cargo con **número** y **código**. El correo aparece en la Terminal 1.
2. **Consultar:** http://localhost:5173/consultar con el número y el código.
3. **Mesa de partes:** http://localhost:5173/panel/login → `mesa.demo` → Expedientes → abre el expediente → **Derivar** a "Gerencia de Ejemplo 1".
4. **Área:** cierra sesión → `area1.demo` → verás "Por recibir" → **Recibir** → agrega una observación → cambia el estado.
5. **Separación:** entra como `area2.demo`: no debe ver nada.
6. **Administración:** `admin.demo` → Usuarios, Áreas, Tipos de documento, Estados.
7. **Control:** `auditor.demo` → Reportes (filtros y **Exportar CSV**) y Auditoría.

| Usuario | Rol | Qué puede hacer |
|---|---|---|
| admin.demo | Administrador | Usuarios, áreas, catálogos, auditoría |
| mesa.demo | Mesa de partes | Ver todos los expedientes, derivar, cambiar estado |
| area1.demo / area2.demo | Funcionario de área | Solo lo de su área |
| auditor.demo | Consulta y reportes | Ver todo, reportes, CSV, auditoría |

## 8. Respaldo
```
powershell -ExecutionPolicy Bypass -File scripts\respaldo.ps1
```
Crea `backups\FECHA\` con la base de datos y los adjuntos. Contiene datos personales: guárdalo cifrado y fuera del repositorio. Para restaurar la base: `pg_restore -U mesa_partes_user -d mesa_partes_huarmey --clean base_datos.dump` (con PostgreSQL detenido para otras conexiones).

## 9. Subir a GitHub (opcional)
```
git init
git add .
git status
```
Revisa que **no aparezcan** `.env`, `node_modules`, `.venv`, `storage_privado` ni `backups`. Luego `git commit -m "Mesa de partes digital"` y sigue las instrucciones de GitHub para conectar el repositorio.

## Errores comunes
| Mensaje o síntoma | Causa y solución |
|---|---|
| "Backend no disponible" (rojo) | Django no está encendido: ejecuta `python manage.py runserver` en la Terminal 1 |
| `No module named ...` | Falta activar el entorno (`.venv\Scripts\Activate.ps1`) o `pip install -r requirements.txt` |
| `Falta DJANGO_SECRET_KEY` / `Falta DB_PASSWORD` | Falta crear o completar `backend\.env` |
| `password authentication failed` | La contraseña de `DB_PASSWORD` no coincide con la de PostgreSQL |
| `relation ... does not exist` / `No such table` | Falta `python manage.py makemigrations` y `migrate` |
| Error 503 al enviar el formulario | Falta `python manage.py cargar_datos_ficticios` |
| Menú del panel vacío | Falta `python manage.py crear_roles_demo` |
| "Usuario o contraseña incorrectos" | Usa las contraseñas que mostró `crear_roles_demo` |
| 403 al guardar en el panel | Recarga la página (renueva el token CSRF) |
| Puerto 8000 o 5173 ocupado | Cierra la otra terminal que lo usa o reinicia VS Code |
| La consulta dice "No encontramos un expediente" | Número o código mal escrito (el código distingue las letras sin importar mayúsculas) |
| Muchos intentos seguidos → 429 | Es el límite de seguridad; espera unos minutos |
