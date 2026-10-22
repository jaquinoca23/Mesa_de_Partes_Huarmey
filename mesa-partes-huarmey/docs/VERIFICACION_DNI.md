# Verificación de DNI (botón "Verificar DNI y completar mis datos")

## Qué hace
En el formulario ciudadano, si la persona es natural y el documento es DNI, aparece un botón. Al pulsarlo, Django consulta un servicio externo (APIsPERU) y React completa **Nombres** y **Apellidos**. La persona puede corregirlos.

**Es una ayuda para completar el formulario, no una constancia legal de identidad.** El expediente guarda lo que la persona envía; no se guarda ninguna marca de "verificado".

## Cómo activarlo (PowerShell + VS Code)
1. Abre `backend\.env` en VS Code y agrega estas líneas al final (con TU token; no lo compartas):
   ```
   IDENTIDAD_API_URL=https://dniruc.apisperu.com/api/v1/dni
   IDENTIDAD_API_TOKEN=pega_aqui_tu_token
   ```
2. Reinicia Django (Ctrl+C y `python manage.py runserver`).
3. Recarga http://localhost:5173/presentar. Escribe un DNI de 8 dígitos y pulsa el botón.
4. Sin token, el botón no aparece y el formulario funciona igual (se escribe a mano).

## Reglas de seguridad aplicadas
- El token solo está en `backend\.env` (que no se sube a GitHub). Nunca llega al navegador ni a los registros.
- Se envía en la cabecera `Authorization`, no en la dirección.
- Solo se aceptan 8 dígitos; se exige HTTPS; no se siguen redirecciones; se limita el tamaño de la respuesta y el tiempo de espera.
- Límite de 20 consultas por hora por dirección IP (consultas públicas podrían usarse para buscar nombres ajenos).
- No se guarda el resultado ni se escribe el DNI en los registros del servidor.
- Si el proveedor falla, el usuario ve un mensaje genérico y escribe sus datos a mano.

## Límites y decisiones pendientes
- APIsPERU es un servicio de **terceros no oficial**; su plan gratuito permite 1000 consultas al mes. Sirve para la demostración.
- Para producción corresponde un **convenio con RENIEC o la plataforma PIDE**, y definir la finalidad y el tratamiento de datos según la Ley 29733 (ver pendientes #30 y #31).
- Si más adelante se necesita una verificación confiable, el servidor debería volver a consultar el DNI al registrar y comparar con lo enviado.

## Pruebas
`python manage.py test apps.identidad` (simulan el proveedor; no gastan consultas reales).
