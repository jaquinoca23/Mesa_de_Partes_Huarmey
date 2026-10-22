# Etapa 7 — Bandejas por área, derivaciones y recepción

## Qué incluye
- **Bandeja** (`/panel/expedientes`): lista con filtros (texto, estado, tipo, área, fechas, "pendientes de recibir") y paginación de 20.
- **Regla de visibilidad (en el servidor):** Mesa de partes y Consulta ven todos; un funcionario ve los expedientes que tiene su área y los que le derivaron y aún no recibió. Un expediente ajeno responde 404 (no se revela que existe).
- **Derivar:** crea una derivación PENDIENTE. El expediente sigue en el área de origen hasta que el destino lo **recibe**. Solo puede haber una pendiente por expediente (también lo garantiza la base de datos).
- **Recibir:** lo hace una persona del área destino (o la persona designada). Entonces el expediente pasa a esa área.
- **Cambiar estado:** bloqueado si hay derivación pendiente o si el estado es final. Cada cambio queda en el historial y avisa al solicitante por correo.
- **Observaciones y actuaciones:** se agregan; no se editan ni se borran.
- **Adjuntos:** descarga solo con sesión, permiso y área correcta; queda en la auditoría.
- Estados `en-derivacion` y `en-atencion` se aplican solos si existen en el catálogo (son provisionales).

## Pasos (PowerShell)
1. Copia el zip sobre tu proyecto.
2. Backend:
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
   (`makemigrations` ahora también crea las tablas de derivaciones.)
3. Frontend: `cd frontend` → `npm run dev`
4. Prueba completa:
   1. Registra una solicitud en http://localhost:5173/presentar (anota número y código).
   2. Entra como `mesa.demo` → Expedientes → abre el expediente → **Derivar** a "Gerencia de Ejemplo 1".
   3. Cierra sesión, entra como `area1.demo` → verás el expediente con la etiqueta "Por recibir" → **Recibir**.
   4. Como `area1.demo` agrega una observación y cambia el estado.
   5. Entra como `area2.demo`: no debe ver nada. Prueba la dirección del expediente: debe dar "No se encontró…".
   6. En `/consultar` el ciudadano ve el historial actualizado.

## Errores comunes
- *Bandeja vacía para area1.demo*: es lo correcto hasta que alguien le derive un expediente.
- *"No tienes permiso"*: `crear_roles_demo` no se ejecutó o el usuario no tiene el rol.
- *"El expediente tiene una derivación pendiente"*: el área destino debe recibirlo antes de cambiar su estado.
- *Usuario sin área*: no ve expedientes; asígnale un área en Usuarios.
