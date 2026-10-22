# Base de datos (PostgreSQL)

La base de datos objetivo del proyecto es **PostgreSQL**. Esta carpeta contiene lo necesario para crearla.

## 1. Crear el usuario y la base de datos (una sola vez)

1. Abre `database/crear_base_datos.sql` y cambia `CAMBIAR_ESTA_CLAVE` por una contraseña propia.
   **No subas ese archivo a GitHub con tu contraseña real.**
2. Ejecuta el archivo con el administrador `postgres` (te pedirá la contraseña que elegiste al instalar PostgreSQL).

   En PowerShell, desde la carpeta raíz del proyecto (ajusta `17` a tu versión de PostgreSQL):

   ```
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -f database\crear_base_datos.sql
   ```

   Alternativa visual: abre **pgAdmin 4**, clic derecho en *Databases* → *Query Tool*,
   pega el contenido del archivo y pulsa el botón de ejecutar (▶). Ejecuta primero el `CREATE USER`
   y luego el `CREATE DATABASE` (selecciona cada instrucción y ejecútala por separado).

## 2. Conectar Django

En `backend/.env` deben estar las variables `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST` y `DB_PORT` (ver `backend/.env.example`). `DB_PASSWORD` es la contraseña del paso 1.

## 3. Crear las tablas (migraciones)

Desde la carpeta `backend`, con `(.venv)` activo:

```
python manage.py makemigrations
python manage.py migrate
```

- `makemigrations` genera los archivos que describen las tablas a partir de los modelos
  (quedan en `apps/*/migrations/`; se suben a Git).
- `migrate` crea las tablas en PostgreSQL.

## 4. Cargar datos ficticios

```
python manage.py cargar_datos_ficticios
```

Se puede repetir sin duplicar datos. Todo lo que carga es de prueba y está marcado como ficticio o provisional.

## 5. Ver los datos

Crea un usuario administrador y abre http://127.0.0.1:8000/admin/ :

```
python manage.py createsuperuser
```

## Política de conservación y eliminación (provisional)

- Los expedientes, solicitantes y el historial **no se eliminan** desde el sistema (relaciones protegidas).
- El historial de estados solo se agrega; no se modifica ni se borra.
- Las reglas oficiales de archivo y conservación documental están pendientes de validar con la municipalidad.

## Copias de seguridad (ejemplo para desarrollo)

```
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -U mesa_partes_user -d mesa_partes_huarmey -F c -f copia_respaldo.dump
```

Guarda los respaldos fuera del repositorio. Para un respaldo completo (base de datos + adjuntos) usa `scripts/respaldo.ps1` (ver GUIA_PASO_A_PASO.md). La estrategia de respaldo para producción es un pendiente institucional (ver docs/institucional/pendientes.md).
