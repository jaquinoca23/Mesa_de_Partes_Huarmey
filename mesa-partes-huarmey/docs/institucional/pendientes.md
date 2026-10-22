# Pendientes institucionales (por validar con la Municipalidad Provincial de Huarmey)

Esta lista reúne lo que **no se puede asumir** y debe confirmarse con la municipalidad.
Mientras tanto, el sistema usa configuraciones provisionales y datos ficticios.

| # | Tema a validar | Estado | Qué se hace mientras tanto |
|---|----------------|--------|----------------------------|
| 1 | ROF vigente y modificatorias (estructura de áreas) | Pendiente | Áreas de ejemplo marcadas como ficticias |
| 2 | TUPA vigente y modificatorias | Pendiente | No se asume que todo tipo documental sea del TUPA |
| 3 | Directiva de gestión documental | Pendiente | Flujo provisional |
| 4 | Procedimientos de recepción y derivación | Pendiente | Flujo provisional |
| 5 | Reglas de numeración de expedientes y del cargo | Pendiente | Numeración provisional `AAAA-NNNNNN` |
| 6 | Fecha y hora oficial de recepción | Pendiente | Hora del servidor (provisional) |
| 7 | Horarios de atención y cómputo de plazos | Pendiente | No se muestran en el portal |
| 8 | Firma digital (si corresponde) | Pendiente | El cargo no se presenta como firma digital |
| 9 | Archivo y conservación documental | Pendiente | Sin política de eliminación |
| 10 | Privacidad y acceso a la información | Pendiente | Texto de política provisional |
| 11 | Integración con sistemas institucionales existentes | Pendiente | Sistema independiente |
| 12 | Instrumentos de gobierno y transformación digital | Pendiente | — |
| 13 | Logo oficial e identidad visual definitiva | Pendiente | Espacio reservado; paleta provisional |
| 14 | Catálogo oficial de tipos documentales y estados | Pendiente | Catálogos de prueba configurables |
| 15 | Texto oficial de la política de privacidad y tratamiento de datos personales | Pendiente | Casilla con aviso de texto pendiente |
| 16 | Redacción oficial de la declaración de veracidad y cuándo corresponde exigirla | Pendiente | Declaración provisional, obligatoria para todos |
| 17 | Tipos, cantidad y tamaño máximo de archivos adjuntos permitidos | Pendiente | PDF, JPG, PNG, DOCX; 5 archivos de 10 MB (configurable en `.env`) |
| 18 | Documentos de identidad aceptados y sus formatos (DNI, RUC, carné de extranjería, pasaporte) | Pendiente | Formatos provisionales en el formulario |
| 19 | Datos obligatorios y opcionales de la solicitud (por ejemplo teléfono, domicilio) | Pendiente | Teléfono opcional; sin domicilio |
| 20 | Política de identificación del remitente en el cargo de recepción | Pendiente | El cargo muestra nombre y documento enmascarado (solo 2 últimos caracteres); no es constancia legal |
| 21 | Roles, perfiles y permisos definitivos del personal (quién deriva, cambia estados, ve reportes o auditoría) | Pendiente | 4 roles de ejemplo en `apps/core/roles.py` |
| 22 | Procedimiento de derivación y recepción entre áreas (¿se exige recepción?, plazos de recepción, reasignación) | Pendiente | Derivación con recepción obligatoria; sin plazos |
| 23 | Textos oficiales de los correos de notificación y cuáles cambios de estado se notifican | Pendiente | Textos de demostración; se notifica cada cambio de estado |
| 24 | Servicio de correo institucional (remitente, servidor) | Pendiente | En desarrollo los correos se imprimen en la terminal |
| 25 | Política de retención y conservación de adjuntos y datos personales (cuánto tiempo, cómo se eliminan) | Pendiente | Nada se elimina |
| 26 | Política de respaldos y continuidad (frecuencia, responsable, lugar de custodia, cifrado) | Pendiente | Script manual `scripts/respaldo.*` |
| 27 | Política de contraseñas y autenticación reforzada del personal (segundo factor) | Pendiente | Validadores estándar de Django |
| 28 | Qué datos del expediente puede exportar cada rol en reportes | Pendiente | CSV sin datos personales, solo para el rol con `ver_reportes` |
| 29 | Infraestructura de publicación (servidor, dominio, HTTPS, hosting) | Pendiente | Solo ejecución local; ver `docs/arquitectura/seguridad.md` |
| 30 | Proveedor oficial para consultar DNI (convenio con RENIEC o plataforma PIDE) | Pendiente | APIsPERU (terceros) solo para demostración, desactivable quitando el token |
| 31 | Finalidad, base legal y aviso al ciudadano sobre la consulta de su DNI en un servicio externo (Ley 29733) | Pendiente | Resultado no se guarda; sin aviso oficial aún |
