# Infraestructura (opcional)

Docker es **opcional**: el proyecto funciona igual con PostgreSQL instalado en Windows (ver `database/README.md`).
Este archivo solo levanta la base de datos para quien prefiera no instalar PostgreSQL.

Pasos en PowerShell, desde la raíz del proyecto:

```
Copy-Item infra\.env.example infra\.env      # luego edita infra\.env y escribe tu contraseña
docker compose --env-file infra\.env -f infra\docker-compose.yml up -d
```

En `backend/.env` usa: `DB_HOST=localhost`, `DB_PORT=5433`, `DB_USER=mesa_partes_user`, `DB_NAME=mesa_partes_huarmey` y la misma contraseña.
Después: `python manage.py migrate`.

Esto NO es una configuración de producción (no incluye HTTPS, servidor web ni respaldos automáticos).
Ver `docs/arquitectura/seguridad.md`, sección "Antes de publicar".
