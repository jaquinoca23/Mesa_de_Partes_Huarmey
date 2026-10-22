# Etapa 8 — Resumen, reportes, exportación y auditoría

## Qué incluye
- **Inicio del panel:** tarjetas con el total de expedientes visibles, cuántos están "por recibir" en tu área y el conteo por estado, más los últimos 5.
- **Reportes** (`/panel/reportes`, permiso `ver_reportes`): conteos por estado, tipo, área y mes, con filtros de fechas, estado, tipo y área. Solo cuentan los expedientes que tu rol puede ver. No se calculan plazos (pendiente de validar).
- **Exportar CSV:** mismos filtros, hasta 10 000 filas. **No incluye datos personales** del solicitante (ni documento ni correo). Neutraliza fórmulas (`=`, `+`, `-`, `@`) para que Excel no las ejecute. Cada exportación queda en la auditoría.
- **Auditoría** (`/panel/auditoria`, permiso `view_registroauditoria`): lista paginada y filtrable de accesos, cambios de estado, derivaciones, descargas, exportaciones, etc. Solo lectura; no se modifica ni se borra.
- **Seguimiento al ciudadano:** ya incluido desde la Etapa 5 (`/consultar`) y se actualiza con cada cambio de estado, derivación y recepción; el correo de aviso se registra (solo asunto y resultado) en el detalle del expediente.

## Quién ve qué
| Rol | Resumen | Reportes / CSV | Auditoría |
|---|---|---|---|
| Administrador | sí | no* | sí |
| Mesa de partes | sí | no | no |
| Funcionario de área | sí (su área) | no | no |
| Consulta y reportes | sí | sí | sí |

\* El rol Administrador no trae `ver_reportes`; se lo puedes asignar editando permisos en el Admin de Django (http://127.0.0.1:8000/admin) o creando el usuario con el rol "Consulta y reportes". La decisión de roles definitivos es institucional.

## Pasos (PowerShell)
1. Copia el zip sobre tu proyecto (no hay migraciones nuevas en esta etapa).
2. Backend: `cd backend` → `.venv\Scripts\Activate.ps1` → `python manage.py test` → `python manage.py runserver`
3. Frontend: `cd frontend` → `npm run dev`
4. Entra como `auditor.demo` → Reportes → aplica filtros → **Exportar CSV** → ábrelo en Excel.
5. Entra a Auditoría y busca la acción "Reporte exportado".
6. Entra como `area1.demo`: el menú no muestra Reportes ni Auditoría; si abres `/panel/reportes` escribiendo la dirección, ves "Sin permiso".

## Errores comunes
- *Reportes vacíos*: no hay expedientes o los filtros son muy estrictos; pulsa "Limpiar".
- *Tildes raras en Excel*: el CSV ya trae BOM; usa Datos → "Desde texto/CSV" si tu Excel igual no las reconoce.
- *Menú sin Reportes*: tu usuario no tiene el permiso `ver_reportes`.
