# Mesa de Partes Digital — Municipalidad Provincial de Huarmey

Propuesta tecnológica (versión de demostración, **datos ficticios**). Presentación de documentos en línea, cargo de recepción, consulta ciudadana y panel del personal con bandejas por área, derivaciones, reportes y auditoría.

> **Guía completa de instalación y uso: [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md)**

## Estado

Las 9 etapas están construidas. Importante: el código de las etapas 2 a 9 se escribió en un entorno sin acceso a internet, por lo que **no se pudo ejecutar allí**; solo se hicieron comprobaciones estáticas. La primera ejecución de `python manage.py test` y `npm run dev` en tu equipo es la verificación definitiva (ver [docs/pruebas/plan-pruebas.md](docs/pruebas/plan-pruebas.md)).

| Etapa | Contenido |
|---|---|
| 1 | Portal ciudadano (React) |
| 2 | Backend Django + DRF, `GET /api/health/` |
| 3 | PostgreSQL y modelos |
| 4 | Formulario con validación y revisión segura de archivos |
| 5 | Registro real, cargo de recepción, consulta pública |
| 6 | Inicio de sesión, roles, permisos, gestión de usuarios/áreas/catálogos |
| 7 | Bandejas por área, derivación, recepción, actuaciones, descarga privada de adjuntos |
| 8 | Resumen, reportes, CSV, auditoría |
| 9 | Documentación, seguridad, respaldos, guía de demostración |

## Requisitos
Node.js 20+ y npm · Python 3.10+ (probado 3.12) · PostgreSQL con pgAdmin 4 (o Docker, opcional) · Visual Studio Code.

## Arranque rápido (resumen; detalle en la guía)
```
# Terminal 1 — backend
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py cargar_datos_ficticios
python manage.py crear_roles_demo
python manage.py test
python manage.py runserver

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```
Portal: http://localhost:5173 · Panel del personal: http://localhost:5173/panel/login · Administración de Django: http://127.0.0.1:8000/admin

## Documentación
- [Arquitectura y mapa de la API](docs/arquitectura/arquitectura.md) · [Seguridad y pendientes antes de publicar](docs/arquitectura/seguridad.md) · [Modelo de datos](docs/arquitectura/modelo-datos.md)
- [Flujo de un expediente](docs/procesos/flujo-expediente.md) · [Plan de pruebas](docs/pruebas/plan-pruebas.md)
- [Resumen funcional](docs/propuesta/resumen-funcional.md) · [Guía de demostración](docs/propuesta/guia-demostracion.md)
- [Pendientes institucionales](docs/institucional/pendientes.md)
- Guías por etapa: `docs/ETAPA5_PASO_A_PASO.md` a `docs/ETAPA8_PASO_A_PASO.md`
- Respaldos: `scripts/respaldo.ps1` / `scripts/respaldo.sh` · Docker opcional: [infra/README.md](infra/README.md)

## Variables de entorno (backend/.env)
Ver `backend/.env.example`: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DB_*`, `UPLOAD_*`, `PRIVATE_MEDIA_ROOT`, `EMAIL_*`, `SESSION_HORAS`, `DJANGO_HTTPS`.

## Logo oficial
Guarda el archivo como `frontend/public/images/logo-huarmey.png`; se mostrará automáticamente. No se inventó ningún logo.

## Límites conocidos
- Datos, estados, áreas, roles, numeración, plazos y textos legales son **provisionales** (29 pendientes en `docs/institucional/pendientes.md`).
- El cargo **no es firma digital ni constancia legal**.
- No está listo para publicarse en internet: faltan HTTPS, antivirus, CAPTCHA, correo institucional y más (ver `docs/arquitectura/seguridad.md`).
