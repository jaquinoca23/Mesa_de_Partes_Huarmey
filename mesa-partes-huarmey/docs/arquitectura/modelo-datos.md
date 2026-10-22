# Modelo de datos (actualizado en la ETAPA 9)

Todo lo marcado como **provisional** debe validarse con la Municipalidad Provincial de Huarmey antes de considerarse oficial.

## Entidades implementadas

| Entidad | App | Para qué sirve | Notas |
|---------|-----|----------------|-------|
| `Area` | organizacion | Dependencias en jerarquía (padre → hijas) | Tipos configurables; `es_ficticia` marca datos de prueba |
| `Usuario` | usuarios | Personal municipal (extiende `AbstractUser`) | Contraseña con hash; roles y permisos en ETAPA 6 |
| `TipoDocumental` | catalogos | Categorías de documento | `es_procedimiento_tupa` distingue los del TUPA; `es_provisional` |
| `EstadoExpediente` | catalogos | Estados del trámite | Un solo estado inicial (restricción en BD); `es_provisional` |
| `Solicitante` | expedientes | Persona natural o jurídica | Documento de identidad único; nombre o razón social según tipo |
| `Expediente` | expedientes | Documento presentado y su seguimiento | Número asignado por el servidor; `uuid` y código de verificación para consulta |
| `HistorialEstado` | expedientes | Cambios de estado | Solo se agrega; no se modifica ni elimina |
| `SecuenciaExpediente` | expedientes | Contador de números por año | Bloqueo de fila para evitar duplicados |

## Relaciones principales

```
Area ──(padre)──▶ Area
Usuario ──▶ Area
Expediente ──▶ Solicitante, TipoDocumental, EstadoExpediente (actual)
HistorialEstado ──▶ Expediente, EstadoExpediente (anterior y nuevo), Usuario (opcional)
```

## Decisiones de diseño

- **Numeración (provisional):** formato `AAAA-NNNNNN` (ej. `2026-000001`), correlativo por año de recepción, asignado en el servidor con una transacción y bloqueo de fila. Puede haber saltos si una transacción mayor se revierte; la regla oficial está pendiente.
- **Consulta segura:** el ciudadano no usará el id interno. Cada expediente tiene un `uuid` (no adivinable) y un `codigo_verificacion` aleatorio de 8 caracteres. En la ETAPA 8 se decidirá si el código se almacena con hash.
- **Fechas:** todas con zona horaria; se guardan en UTC y se muestran en hora de Lima. La hora de recepción es la del servidor (provisional).
- **Eliminación:** relaciones con `PROTECT`; el administrador de Django muestra expedientes y solicitantes en solo lectura.
- **Duplicados de solicitante:** restricción única por tipo y número de documento de identidad (provisional).
- **Archivos:** se guardarán fuera de la base de datos; en esta etapa solo se prepara el modelo del expediente.

## Entidades agregadas en las etapas 4 a 8

| Entidad | App | Para qué sirve | Notas |
|---------|-----|----------------|-------|
| `Adjunto` | documentos | Archivo de un expediente | Contenido en carpeta privada con nombre aleatorio; guarda nombre original, tamaño y SHA-256; no se elimina |
| `Derivacion` | derivaciones | Envío de un expediente a otra área | Pendiente/Recibida; una sola pendiente por expediente (restricción en BD) |
| `Actuacion` | derivaciones | Observación o actuación del personal | Solo se agrega |
| `Notificacion` | notificaciones | Resultado de cada correo | Guarda asunto y resultado, no el cuerpo |
| `RegistroAuditoria` | auditoria | Bitácora de acciones | Solo se agrega; sin datos personales |

Campos agregados a `Expediente`: `clave_envio` (único; evita duplicados), `email_contacto`, `telefono_contacto`, `area_actual` (área que lo tiene hoy) y permisos propios (`ver_todos_expedientes`, `cambiar_estado_expediente`, `derivar_expediente`, `registrar_actuacion`, `ver_reportes`).

## Relaciones nuevas

```
Adjunto ──▶ Expediente
Derivacion ──▶ Expediente, Area (origen y destino), Usuario (remitente, receptor, quien recibió)
Actuacion ──▶ Expediente, Usuario
Notificacion ──▶ Expediente
RegistroAuditoria ──▶ Usuario (opcional)
Expediente ──▶ Area (area_actual)
```

## Decisiones de diseño vigentes

- **Idempotencia:** el formulario envía una `clave_envio`; si llega repetida se devuelve el mismo expediente.
- **Visibilidad:** quien tiene `ver_todos_expedientes` ve todo; los demás ven lo de su área y lo derivado a su área pendiente de recepción.
- **Código de verificación:** se guarda en texto (se reenvía por correo y se compara en tiempo constante). Decidir si se guarda con hash es un pendiente de seguridad.
- **Trazabilidad:** `HistorialEstado`, `Actuacion` y `RegistroAuditoria` no se modifican ni se eliminan; adjuntos y usuarios tampoco se eliminan (los usuarios se desactivan).
