# Flujo de un expediente (provisional)

```
Ciudadano presenta ─▶ Recibido ──▶ [Mesa de partes] ─derivar─▶ En derivación (pendiente)
                                                                   │ el área destino RECIBE
                                                                   ▼
                                   Atendido / Archivado ◀── En atención (área responsable) ─derivar─▶ …
```

1. **Presentación:** el ciudadano llena el formulario. El servidor valida, guarda y entrega el **cargo** con número y código. Estado inicial: *Recibido*, en Mesa de partes (sin área asignada).
2. **Derivación:** Mesa de partes (o el área que lo tiene) elige un área destino y un motivo. La derivación queda *pendiente* y el expediente sigue siendo del área de origen.
3. **Recepción:** una persona del área destino (o la designada) confirma. Recién entonces el expediente es del área destino y pasa a *En atención*.
4. **Trabajo:** el área registra observaciones/actuaciones y cambia el estado.
5. **Cierre:** *Atendido* o *Archivado* (estados finales: ya no se puede derivar ni cambiar).
6. **Seguimiento:** el ciudadano consulta con número + código; recibe correos en cada cambio de estado.

Reglas: una sola derivación pendiente por expediente; no se cambia el estado con una derivación pendiente; nada se borra.
**Provisional:** estados, flujo, numeración y roles deben validarse con el procedimiento documentario vigente de la municipalidad (ver `docs/institucional/pendientes.md`).
