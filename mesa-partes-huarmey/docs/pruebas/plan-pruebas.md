# Plan de pruebas

## Automáticas (`cd backend` → `python manage.py test`)
Unas 140 pruebas:
| Archivo | Cubre |
|---|---|
| `documentos/tests.py` | Validación de archivos (también: `python -m unittest apps.documentos.tests`, sin base de datos) |
| `expedientes/test_solicitudes_api.py`, `tests.py` | Formulario, validaciones, modelos, historial, numeración |
| `expedientes/test_registro.py` | Registro, cargo, idempotencia, adjuntos privados, correo, consulta pública y su límite |
| `usuarios/tests.py` | Login, CSRF, límite de intentos, roles, permisos, gestión de usuarios, escalada de privilegios, áreas y catálogos |
| `expedientes/test_panel.py` | Bandejas por área, IDOR, derivar/recibir, estados finales, actuaciones, descarga de adjuntos |
| `expedientes/test_reportes.py` | Resumen, reportes, CSV (sin datos personales, fórmulas neutralizadas), auditoría |

**Resultado esperado:** `OK` al final. Si algo falla, copia el mensaje completo para corregirlo.

## Manuales (lista de comprobación)
- [ ] Enviar el formulario con datos válidos → ver cargo y recibir el correo en la terminal de Django.
- [ ] Hacer doble clic en "Enviar": se crea un solo expediente.
- [ ] Adjuntar un `.exe` renombrado a `.pdf` → se rechaza.
- [ ] Consultar con código equivocado → mensaje genérico.
- [ ] Iniciar sesión con contraseña incorrecta 11 veces seguidas → bloqueo temporal.
- [ ] `area2.demo` no ve expedientes de `area1.demo`.
- [ ] Derivar → el destino ve "Por recibir" → recibir → el expediente cambia de área.
- [ ] Descargar un adjunto como `mesa.demo` (funciona) y sin sesión (se rechaza).
- [ ] Exportar CSV y abrirlo en Excel; verificar que no hay documentos ni correos.
- [ ] Revisar la auditoría tras las acciones anteriores.
- [ ] Probar en el celular (la pantalla del portal se adapta).

## Revisión técnica pendiente
Mientras se redactaba este código no fue posible instalar paquetes ni ejecutarlo (sin acceso a internet en el entorno del asistente). Las comprobaciones hechas fueron estáticas (compilación, nombres sin definir, importaciones internas, rutas de React). **La primera ejecución real de `python manage.py test` y `npm run dev` es la prueba definitiva**; los errores que aparezcan se corrigen enviando el mensaje.
