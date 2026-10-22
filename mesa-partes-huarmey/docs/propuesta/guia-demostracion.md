# Guía de demostración (≈ 10 minutos)

**Preparación (antes de la reunión):** `cargar_datos_ficticios` y `crear_roles_demo` ejecutados, anota las contraseñas, Django y React encendidos, una ventana normal y otra privada del navegador.

1. **Portal ciudadano** (`/`): explica en una frase qué es y que los datos son ficticios.
2. **Presentar** (`/presentar`): llena el formulario como una persona ficticia, adjunta un PDF pequeño y envía. Muestra el **cargo** (número, código, aviso de que no es firma digital) y "Imprimir".
3. **Correo:** muestra en la terminal de Django el mensaje enviado.
4. **Seguridad del formulario:** intenta adjuntar un archivo falso (`.exe` renombrado a `.pdf`) → rechazo.
5. **Mesa de partes** (ventana privada, `mesa.demo`): abre la bandeja, entra al expediente, revisa el adjunto y **deriva** a "Gerencia de Ejemplo 1".
6. **Área** (`area1.demo`): ve "Por recibir" → **Recibir** → agrega una observación → cambia el estado a *Atendido*.
7. **Separación por área:** entra como `area2.demo`: no ve nada.
8. **Ciudadano:** en `/consultar` con número y código muestra el historial completo.
9. **Gestión** (`admin.demo`): usuarios, áreas, tipos y estados editables; nada se elimina.
10. **Control** (`auditor.demo`): reportes, exportación CSV, auditoría.

**Mensaje final:** funciona de punta a punta con datos ficticios; lo que falta es institucional (ROF, TUPA, directivas, plazos, textos legales) y de despliegue seguro. Muestra `docs/institucional/pendientes.md` y la sección "Antes de publicar" de `docs/arquitectura/seguridad.md`.
