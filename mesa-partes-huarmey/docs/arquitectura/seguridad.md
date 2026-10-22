# Seguridad

## Medidas implementadas
| Tema | Medida |
|---|---|
| Secretos | `.env` fuera de Git; Django no arranca sin `DJANGO_SECRET_KEY` ni con clave de ejemplo y `DEBUG=False` |
| Contraseñas | Hash de Django + validadores (longitud, comunes, solo números, similitud). Los usuarios demo reciben claves aleatorias |
| Sesión | Cookie HttpOnly, SameSite Lax, expira al cerrar el navegador y a las 8 h (configurable), sesión nueva al iniciar |
| CSRF | Token obligatorio en todo lo que modifica datos con sesión (incluido el login) |
| Fuerza bruta | Login 10/min; consulta pública 30/h; envío de solicitudes 30/h (por IP) |
| Autorización | Permisos de Django exigidos en el servidor; visibilidad por área; IDOR → 404; nadie puede ascender privilegios (no-admin no asigna ni toca administradores) |
| Consulta ciudadana | Número + código aleatorio de 8 caracteres; comparación de tiempo constante; respuesta genérica; sin datos personales |
| Archivos | Lista blanca de extensiones, tamaño, firma real del contenido, PDF con JavaScript y Office con macros rechazados, nombres saneados, guardado con nombre aleatorio en carpeta privada, SHA-256, descarga solo autenticada como adjunto con `nosniff` |
| Trazabilidad | Historial, actuaciones y auditoría de solo agregar; adjuntos y usuarios no se eliminan |
| Datos personales | Cargo con documento enmascarado; CSV sin datos personales; correos no se guardan (solo asunto y resultado); auditoría sin contraseñas ni datos personales |
| CSV | Neutralización de fórmulas (`=`, `+`, `-`, `@`) |
| Cabeceras | `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`; con `DJANGO_HTTPS=True` también cookies seguras, redirección HTTPS y HSTS |

## Antes de publicar en internet (NO está hecho)
1. Servidor con **HTTPS** real (certificado) y `DJANGO_HTTPS=True`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` con el dominio real.
2. Servidor de aplicación (por ejemplo Gunicorn/Waitress) detrás de un servidor web (Nginx/IIS) que limite el tamaño de peticiones, y archivos estáticos del panel de administración de Django. Construir el frontend (`npm run build`) y servirlo.
3. **Antivirus** (por ejemplo ClamAV) sobre los adjuntos: la validación actual reduce el riesgo pero no lo elimina.
4. **CAPTCHA** o equivalente en el formulario público contra envíos automáticos masivos; el límite por IP se debe revisar si hay un proxy delante (la IP real llega en cabeceras que hoy no se confían).
5. Caché compartida (Redis) para los límites de intentos si hay más de un proceso (hoy usan memoria local).
6. Autenticación reforzada del personal (segundo factor) y política de contraseñas institucional.
7. Respaldos automáticos probados (ver `scripts/respaldo.*`) con cifrado y restauración ensayada.
8. Registro (logs) centralizado y monitoreo; revisión periódica de la auditoría.
9. Revisión legal de la política de privacidad, retención y acceso a datos personales (Ley de Protección de Datos Personales del Perú; ver pendientes institucionales).
10. Pruebas de seguridad independientes (revisión de código y pruebas de intrusión) y actualización de dependencias.
11. Servicio de correo institucional real (hoy los correos se imprimen en la terminal).
12. Decidir si el código de verificación se almacena con hash (hoy se guarda en texto para poder reenviarlo).
