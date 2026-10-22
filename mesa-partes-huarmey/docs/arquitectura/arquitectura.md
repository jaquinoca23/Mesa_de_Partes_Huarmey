# Arquitectura

```
 Ciudadano ──▶ React (portal público)  ─┐
                                        ├─▶ /api  ──▶ Django + DRF ──▶ PostgreSQL
 Personal  ──▶ React (/panel, sesión)  ─┘                 │
                                                          └─▶ carpeta privada de adjuntos (storage_privado)
```

- **Frontend** (`frontend/`): React + Vite + React Router + Lucide. Portal ciudadano (`/`, `/presentar`, `/cargo`, `/consultar`) y panel del personal (`/panel/...`). En desarrollo Vite reenvía `/api` a Django.
- **Backend** (`backend/`): Django 5.2 + DRF. Una app por responsabilidad:

| App | Responsabilidad |
|---|---|
| `core` | Salud (`/api/health/`), permisos reutilizables, paginación, roles de ejemplo, comandos de datos demo |
| `organizacion` | Áreas en jerarquía |
| `usuarios` | Personal municipal, inicio/cierre de sesión, gestión de usuarios |
| `catalogos` | Tipos documentales y estados |
| `expedientes` | Solicitante, Expediente, historial, registro y cargo, consulta pública, bandeja, reportes |
| `derivaciones` | Derivaciones entre áreas y actuaciones |
| `documentos` | Adjuntos privados y validación segura de archivos |
| `notificaciones` | Correos al solicitante (solo se registra asunto y resultado) |
| `auditoria` | Bitácora de solo lectura |
| `identidad` | Consulta de nombres por DNI en un servicio externo (opcional, ver `docs/VERIFICACION_DNI.md`) |

## Mapa de la API

**Pública (sin sesión):** `GET /api/health/`, `GET /api/catalogos/tipos-documentales/`, `GET /api/solicitudes/configuracion/`, `POST /api/solicitudes/` (registra), `POST /api/solicitudes/validar/`, `POST /api/seguimiento/consultar/`, `GET /api/identidad/dni/<dni>/` (solo si hay token configurado).

**Sesión:** `GET /api/auth/csrf/`, `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/`.

**Panel (sesión + permisos):** `/api/panel/` → `usuarios/`, `roles/`, `areas/`, `tipos-documentales/`, `estados/`, `expedientes/` (+ `opciones/`, `<uuid>/`, `cambiar-estado/`, `derivar/`, `actuaciones/`), `derivaciones/<id>/recibir/`, `adjuntos/<id>/descargar/`, `dashboard/`, `reportes/resumen/`, `reportes/exportar.csv`, `auditoria/`.

## Decisiones clave
- Los permisos se aplican **en el servidor**; React solo oculta opciones.
- Sesión por cookie HttpOnly + CSRF (no se guardan tokens en el navegador).
- Los endpoints públicos no usan sesión (no dependen de cookies) y tienen límite de intentos.
- Historial, actuaciones y auditoría son de solo agregar; las relaciones usan `PROTECT`.
- Los archivos nunca van a la base de datos ni a una carpeta pública.
