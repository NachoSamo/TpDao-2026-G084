# User stories

Reglas de negocio (RN-xx) y glosario: [conocimiento/negocio.md](../conocimiento/negocio.md).

## Cómo trabajamos

- Una US = una rama `us-XX-descripcion-corta` = un PR. Otro integrante revisa antes de mergear.
- Una US está **terminada** cuando cumple todos sus criterios de aceptación y tiene al menos un test de la regla principal.
- Si una US crece mucho, se parte en dos (`US-07a`, `US-07b`).

### Plantilla

```markdown
### US-XX — Título
**Como** <rol> **quiero** <acción> **para** <beneficio>.
Criterios de aceptación:
- [ ] Dado ... cuando ... entonces ...
Reglas: RN-xx · Clases: ...
```

## Reparto propuesto (por épica, para no pisarnos)

| Épica | Responsable | US | Patrón |
|---|---|---|---|
| E1 Catálogo e inventario | Juan | US-01 a US-04 | Observer |
| E2 Logística CD → local | Oli | US-05 a US-09 | State |
| E3 Ventas y devoluciones | Nacho | US-10 a US-12 | — |
| E4 Reportes | uno cada uno + el 4.º a quien termine primero | US-13 a US-16 | — |

Orden sugerido: US-01 → US-02 → US-03 son la base de todo; arrancar por ahí.

---

## E1 — Catálogo e inventario

### US-01 — ABM de sucursales
**Como** administrador **quiero** dar de alta, modificar y dar de baja sucursales **para** representar los locales y el CD.
- [ ] Una sucursal tiene nombre, dirección y tipo (LOCAL o CENTRO_DISTRIBUCION).
- [ ] `esCentroDistribucion()` devuelve true solo para el tipo CD.

### US-02 — ABM de productos, categorías y proveedores
**Como** administrador **quiero** gestionar productos, categorías y proveedores **para** tener el catálogo actualizado.
- [ ] Dado un producto con `codigo` existente, al crear otro igual entonces se rechaza (RN-05).
- [ ] Dado un proveedor con `cuit` existente, al crear otro igual entonces se rechaza (RN-05).
- [ ] Un producto puede tener varios proveedores con su costo y uno marcado como principal.

### US-03 — Stock por sucursal y mínimos
**Como** encargado de local **quiero** ver el stock de cada producto en mi sucursal y definir su mínimo **para** saber cuándo reponer.
- [ ] Cada entrada/salida genera un `MovimientoStock` (no se edita el stock "a mano").
- [ ] `disponibleParaVenta()` = disponible − reservada.

### US-04 — Aviso de stock bajo (Observer)
**Como** encargado de local **quiero** ser notificado cuando un producto queda bajo su mínimo **para** pedir reposición a tiempo.
- [ ] Dado un stock con mínimo 10 y disponible 11, cuando se venden 2 entonces se notifica a todos los observadores (RN-09).
- [ ] `GeneradorReposicionAutomatica` agrega el faltante a una orden de reposición pendiente.

## E2 — Logística CD → local

### US-05 — Orden de reposición
**Como** encargado de local **quiero** consolidar mis necesidades en una orden hacia el CD **para** recibir mercadería.
- [ ] Origen debe ser el CD y destino un local (RN-07); si no, se rechaza.
- [ ] Una orden tiene al menos un detalle (producto + cantidad solicitada).

### US-06 — Armar y precintar bultos
**Como** operario del CD **quiero** armar bultos con productos de una orden y precintarlos **para** prepararlos para el despacho.
- [ ] Un bulto nace en estado **Preparado**.
- [ ] No se puede poner en bultos más de lo pendiente de la orden (RN-08).
- [ ] `precintar()` asigna el código de precinto y pasa a **Precintado**.

### US-07 — Despachar remito
**Como** operario del CD **quiero** registrar el despacho del remito **para** que los bultos queden en tránsito.
- [ ] Todos los bultos del remito pasan a **En tránsito**.
- [ ] Despachar un bulto que no está Precintado lanza error (State).

### US-08 — Recepción y verificación de precinto
**Como** encargado de local **quiero** registrar la llegada de cada bulto indicando si el precinto está íntegro **para** que solo ingrese mercadería segura.
- [ ] Precinto íntegro → **Recibido** → **Verificado** → el stock del local aumenta (RN-01).
- [ ] Precinto roto → **Rechazado** con motivo, el stock **no** aumenta (RN-02).
- [ ] Un bulto Verificado o Rechazado no acepta más transiciones.

### US-09 — Historial inmutable del bulto
**Como** auditor **quiero** ver todos los cambios de estado de un bulto **para** tener trazabilidad.
- [ ] Cada transición crea un `CambioEstadoBulto` con fecha, estado anterior/nuevo y responsable (RN-03).
- [ ] No existe operación para modificar ni borrar el historial.

## E3 — Ventas y devoluciones

### US-10 — Registrar venta
**Como** vendedor **quiero** registrar una venta con uno o más productos **para** atender al cliente.
- [ ] Dado un stock disponible de 3, cuando intento vender 4 entonces se rechaza (RN-04).
- [ ] La venta descuenta stock y guarda precio y costo unitario del momento.

### US-11 — Cobro y comprobante
**Como** vendedor **quiero** cobrar con uno o más medios de pago y emitir el comprobante **para** cerrar la venta.
- [ ] La suma de los cobros debe ser igual al total (RN-10).
- [ ] Se emite un comprobante con número único.

### US-12 — Devolución
**Como** vendedor **quiero** registrar devoluciones de una venta **para** reintegrar dinero y stock.
- [ ] Sin venta registrada, se rechaza (RN-06).
- [ ] No se puede devolver más que `cantidadDevolvible()` (RN-06).
- [ ] Reingresa stock y registra el monto reintegrado (RN-11).

## E4 — Reportes

| US | Reporte | Filtros |
|---|---|---|
| US-13 | Ventas e ingresos por período, local y medio de pago | fecha desde/hasta, sucursal |
| US-14 | Productos más vendidos y margen estimado | fecha desde/hasta, top N |
| US-15 | Bultos rechazados / mermas por precinto | fecha, sucursal destino |
| US-16 | Tiempo promedio de tránsito CD → local | fecha, sucursal destino |
