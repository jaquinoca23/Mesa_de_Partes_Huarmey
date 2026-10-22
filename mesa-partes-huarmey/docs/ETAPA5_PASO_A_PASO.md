# Etapa 5 — Registro de expedientes y cargo de recepción

## Qué hace
- `POST /api/solicitudes/` registra la solicitud (expediente + historial inicial + adjuntos privados) y devuelve el **cargo**.
- Envíos repetidos (doble clic) no duplican: se devuelve el mismo expediente.
- `POST /api/seguimiento/consultar/` consulta pública con **número + código de verificación** (respuesta genérica si no coincide, límite de 30 intentos/hora).
- Se envía un correo (en desarrollo se imprime en la terminal de Django).
- React: tras enviar, muestra `/cargo` (imprimible); `/consultar` muestra estado e historial.

## Pasos (PowerShell, en la carpeta del proyecto)
1. Copia el contenido del zip sobre tu proyecto (reemplaza archivos).
2. Backend (terminal 1):
   ```
   cd backend
   .venv\Scripts\Activate.ps1
   python manage.py makemigrations
   python manage.py migrate
   python manage.py cargar_datos_ficticios
   python manage.py test
   python manage.py runserver
   ```
3. Frontend (terminal 2): `cd frontend` → `npm run dev`
4. Abre http://localhost:5173/presentar, llena el formulario y envía. Verás el cargo.
5. Copia número y código, ve a `/consultar` y verifica.

## Errores comunes
- *503 "sistema no disponible"*: falta `cargar_datos_ficticios` (no hay estado inicial).
- *"No such table"*: falta `makemigrations` + `migrate`.
- *Correo*: aparece en la terminal de Django, no en tu bandeja (es lo esperado en desarrollo).
