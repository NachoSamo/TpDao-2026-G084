# Revisión del documento de entrega contra enunciado y código (01/11/2026)

Fuentes: enunciado `tema3.pdf`, documento `entrega/Presentacion-grupo-G084.docx` (respaldo: `entrega/Presentacion-grupo-G084.respaldo-2026-11-01.docx`), código en `distribucion/`, esquema en `distribucion/db.py:5-30`, diagramas en `docs/diagramas/`.

Decisión del grupo: los diagramas mantienen el **modelo de diseño**; solo se corrigió lo de C1–C7. La nota de la sección 2.3 se quitó del documento (es la entrega formal); su contenido quedó como nota interna en la sección 5 de este informe.

Ejecución: 25 tests existentes en verde (`python3 -m unittest discover -s tests`) y 14 escenarios (+1 extra) con un script propio sobre base `:memory:`, sin tocar la base de la demo.

**Actualización (C5, opción B aprobada):** se implementó el registro de **merma** al rechazar un bulto (tabla `merma` inmutable, `servicios.py` en `verificar`, reporte de rechazos valorizado, formato en `app.js`, test nuevo). Suite: 26 tests en verde. Se descartaron la regla de plazo de devolución (el enunciado no la pide) y la validación del medio de reintegro (opcional).

---

## 1. Figuras a exportar y reemplazar en el documento

| Figura | Archivo | Qué cambió |
|---|---|---|
| **Figura 1 (DER)** | `docs/diagramas/der.html` | + tabla `merma` (bulto, sucursal, producto, cantidad, costo, motivo; inmutable), abajo a la derecha; + tabla `ingreso` (proveedor, sucursal CD, producto, cantidad, costo) con sus 3 FK; `devolucion.medio_pago_id` + relación a `medio_pago`; `recepcion.observaciones` → `motivo_rechazo` y nota "se registra al recibir"; `producto_proveedor` + `UNIQUE(producto_id) WHERE principal = 1`; `movimiento_stock` lista los tipos reales; RN-07 ahora dice "se valida en Python, sin CHECK". Se intercambiaron de fila `medio_pago` y `comprobante` (misma columna) para que la línea nueva no pase por detrás de otra tabla. |
| **Figura 2 (UML)** | `docs/diagramas/diagrama-clases.html` | `BultoContenedor` → `Bulto` (atributo `estado`; métodos `precintar(codigo)`, `despachar()`, `recibir(integro)`, `verificar(motivo)`; sin `rechazar`). `EstadoPreparado…EstadoRechazado` → `Preparado…Rechazado`; `EstadoBulto.verificar(b, integro)`, sin `rechazar`. Observer: `stockBajoMinimo` → `actualizar(stock)` y `Stock.notificar()`. `Recepcion.observaciones` → `motivoRechazo`. + clase `Ingreso` (a la derecha de `Proveedor`, se agregó una 8.ª columna) asociada a `Proveedor` y `Producto`. + asociación `Devolucion → MedioPago` ("reintegra por"). |
| **Figura 3 (estados)** | `docs/diagramas/maquina-estados-bulto.html` | Título y texto: `Bulto` / `estado`. Subtítulos de estado con los nombres de clase del código. `recibir()` → `recibir(integro)`; `rechazar(motivo) [precinto roto]` → `verificar(motivo) [!precintoIntegro]`; Rechazado: `entry / registra merma` (ahora es cierto: se implementó). (Las tablas de abajo de la página también se actualizaron, pero no se exportan.) |

Para exportar: abrir cada `.html` en Chrome y usar el botón **Exportar JPG**. Un detalle en la Figura 1: la línea `ingreso → sucursal` (rotulada `sucursal_id (CD)`) roza la esquina superior de `movimiento_stock`; no había una celda libre sin ningún cruce.

---

## 2. Contradicciones que necesitan una decisión

1. **Enunciado vs. código y documento: ¿cuándo se habilita el stock?** El enunciado dice que el stock no es Disponible "hasta que el **remito y el contenedor** pasen a estado Verificado". El código suma el stock **por bulto**, al verificar cada uno, aunque el remito quede `EN_REVISION` o `PARCIALMENTE_ACEPTADO` (`servicios.py:236-242`). El documento lo justifica como decisión ("Recepción por bulto"), y el README ya lo marca como algo a confirmar con la cátedra. **Recomendación:** mantener el comportamiento por bulto, defenderlo como decisión explícita y confirmarlo con la cátedra antes de la presentación. Cambiarlo en el código es riesgoso (fase 3, punto 9).
2. **Versión propuesta para C1 vs. código.** La propuesta era `verificar(precinto_integro, motivo?)`. El código recibe la condición del precinto en `recibir(id, integro, responsable)` (`servicios.py:223-227`) y `verificar(id, responsable, motivo)` decide con ese dato (`:230-235`); la interfaz web hace lo mismo. Se documentó la versión real. Cambiarla es la fase 3, punto 6 (no recomendado ahora).
3. **Reporte sugerido "movimientos/valorización del inventario".** No se implementó: el reporte de tránsito cubre la primera mitad de esa línea. No incumple, porque se exigen 4 reportes y hay 4, pero no conviene decir que se cubrieron los 5 sugeridos.

---

## 3. Cumplimiento del enunciado

| Exigencia del enunciado | Estado | Evidencia en código | Evidencia en documento |
|---|---|---|---|
| P1. Sucursales/locales y CD | ✔ Cumple | `servicios.py:42-69` (guardar, baja lógica; el tipo no se modifica) | Tabla 1, fila 1 |
| P2. Productos, categorías, precios, mínimos, proveedores | ✔ Cumple | `servicios.py:42-64, 72-77, 95-101`; `db.py:7-12` | Tabla 1, fila 2 |
| P3. Orden de reposición con origen y destino (consolidar) | ✔ Cumple | `servicios.py:123-156` | Tabla 1, fila 3 |
| P4. Bultos, remito y precinto | ✔ Cumple | `servicios.py:159-204`; `db.py:17-19` (precinto UNIQUE) | Tabla 1, fila 4 |
| P5. Despacho desde el CD | ✔ Cumple | `servicios.py:207-220` (escenarios 3 y 12) | Tabla 1, fila 5 |
| P6. Recepción verificando el precinto | ✔ Cumple | `servicios.py:223-244` (escenarios 4 y 5) | Tabla 1, fila 6; Tabla 4 |
| P7. Ventas, cobros, comprobante, devoluciones (stock y caja) | ✔ Cumple | `servicios.py:247-286`; reporte de ventas `reportes.py:16-24` | Tabla 1, fila 7 |
| Compras (entidades para compras, logística y ventas) | ⚠ Parcial | tabla `ingreso` + movimiento COMPRA (`servicios.py:104-114`); no hay orden de compra con detalle | Tabla 1 (fila nueva), 2.2, sección 4 |
| V1. Stock Disponible solo con Verificado; precinto roto → Rechazado | ⚠ Cumple por bulto (ver contradicción 1) | `servicios.py:236-238`; `modelos.py:56-59` | Tabla 2, fila 1; sección 4 |
| V2. Trazabilidad inmutable de estados | ✔ Cumple | `db.py:20, 26-29`; `servicios.py:186-197` (escenario 6) | Tabla 2, fila 2 |
| V3. No vender más que lo disponible y verificado | ✔ Cumple | `servicios.py:83-88` + `db.py:12` CHECK (escenario 1) | Tabla 2, fila 3 |
| V4. Sin productos ni proveedores duplicados | ✔ Cumple | `db.py:7-9` UNIQUE (escenario 8) | Tabla 2, fila 4 |
| V5. Devoluciones: venta registrada y "reglas establecidas" | ✔ Cumple | reglas definidas por el grupo: venta registrada, producto de la venta, cantidad ≤ vendido − devuelto, mercadería apta (buen estado), medio de reintegro válido; reintegro a precio histórico (`servicios.py:272-286`) | Tabla 2, fila 5 |
| Mínimo 2 patrones | ✔ Cumple (State, Observer) | `modelos.py:25-77, 79-102` | Tabla 5, sección 3 |
| Mínimo 4 reportes no triviales | ✔ Cumple | `reportes.py:16-45` (escenario 14) | Tabla 3 |
| Ciclo de vida del bulto | ✔ Cumple | `modelos.py:25-67`; `servicios.py:191-197` (escenarios 4, 5, 7) | 2.4, Figura 3, Tabla 4 |

---

## 4. Fase 2: afirmaciones del documento contra el código

| # | Afirmación del documento | Ubicación | Evidencia en código | Estado | Acción |
|---|---|---|---|---|---|
| 1 | Alta, modificación y baja lógica de sucursales LOCAL/CD | Tabla 1 f1 | `servicios.py:42-69`; `db.py:6` | ✔ | — |
| 2 | ABM de catálogo, producto–proveedor con costo, un único principal | Tabla 1 f2 | `servicios.py:72-77`; índice parcial `db.py:11` (escenario 8) | ✔ | — |
| 3 | Stock mínimo por sucursal y producto | Tabla 1 f2 | `servicios.py:95-101`; `db.py:12` | ✔ | — |
| 4 | Órdenes CD → local; validación de tipos | Tabla 1 f3 | `servicios.py:124-125` (solo Python, sin CHECK) | ✔ | — |
| 5 | Generación/consolidación automática sin duplicar | Tabla 1 f3, 3 Observer | `servicios.py:136-156` (escenario 11) | ✔ (ver nota 11b) | — |
| 6 | Remito agrupa bultos; precinto único | Tabla 1 f4 | `db.py:17-18` (escenario 8) | ✔ | — |
| 7 | Bulto ≤ lo pedido y ≤ lo libre del CD; reserva | Tabla 1 f4, sección 4 | `servicios.py:171-179` (escenario 2) | ✔ | — |
| 8 | Despacho del remito completo; descuenta CD y libera reserva en la misma transacción | Tabla 1 f5 | `servicios.py:207-220` (escenarios 3 y 12) | ✔ | — |
| 9 | Recepción en dos pasos; precinto registrado al recibir | Tabla 1 f6, Tabla 4 | `servicios.py:223-235` | ✔ (corregido en el doc) | — |
| 10 | Venta multiproducto; cobros = total; comprobante único | Tabla 1 f7 | `servicios.py:247-269`; `db.py:21` (escenario 9) | ✔ | — |
| 11 | Devolución referida a una venta; reingreso; reintegro con medio | Tabla 1 f7, Tabla 2 f5 | `servicios.py:272-286`; `db.py:24` (escenario 10) | ✔ | — |
| 12 | El stock del local solo sube en Recibido → Verificado | Tabla 2 f1 | `servicios.py:236-238` (escenario 4) | ✔ | — |
| 13 | Triggers bloquean UPDATE/DELETE en historial y movimientos | Tabla 2 f2 | `db.py:26-29` (escenario 6) | ✔ | — |
| 14 | No vender más que lo disponible | Tabla 2 f3 | `servicios.py:85-86` (escenario 1) | ✔ | — |
| 15 | CHECK cantidades ≥ 0 y reservada ≤ cantidad | Tabla 2 f3 | `db.py:12` | ✔ | — |
| 16 | UNIQUE en código, CUIT, categoría, precinto | Tabla 2 f4 | `db.py:7-9, 18` (escenario 8) | ✔ | — |
| 17 | No devolver más que lo vendido menos lo devuelto | Tabla 2 f5 | `servicios.py:280-282` (escenario 10) | ✔ | — |
| 18 | Reintegro a precio histórico | Tabla 2 f5 | `servicios.py:283` (escenario 10: precio cambiado a 99, reintegro 20,00) | ✔ | — |
| 19 | Transacción `BEGIN IMMEDIATE` con rollback completo | Tabla 2 f6, sección 4 | `db.py:39-47`; `servicios.py:13-18` (escenario 12) | ✔ | — |
| 20 | 4 reportes, filtros por período y local, CSV | Tabla 3 | `reportes.py:10-46`; `web.py:183-225` (escenario 14) | ✔ | — |
| 21 | Ventas: neto = cobrado − reintegrado, por local y medio | Tabla 3 f1 | `reportes.py:16-24` (EFECTIVO 30 − 20 = 10 ✔) | ✔ | Cosmético: muestra "0" en vez de "0.00" |
| 22 | Margen con precio y costo históricos, descuenta devoluciones | Tabla 3 f2 | `reportes.py:25-33` (6 u, 60,00, margen 24,00 ✔) | ✔ | — |
| 23 | Rechazados: unidades, motivo, destino, fecha y merma valorizada | Tabla 3 f3 | `reportes.py:34-40` | ✔ | Implementado (escenario 13: 10 u × 6,00 = 60,00) |
| 24 | Tránsito: horas promedio y máximo por destino | Tabla 3 f4 | `reportes.py:37-45` | ✔ | — |
| 25 | `EstadoBulto` lanza error por defecto; cada estado sobrescribe | 3 State | `modelos.py:25-65` (escenario 7) | ✔ | — |
| 26 | Estado como texto, reconstruido como objeto | 3 State | `servicios.py:192-195`; `modelos.py:67` | ✔ | — |
| 27 | Reintento sobre Verificado no reingresa stock | 3 State | escenario 4 | ✔ | — |
| 28 | `Stock.notificar()` → `actualizar(stock)`; el generador consolida | 3 Observer | `modelos.py:92-102`; `servicios.py:90-92, 136-156` | ✔ | — |
| 29 | Remito parcialmente aceptado | sección 4 | `servicios.py:239-242` (escenario 14: `PARCIALMENTE_ACEPTADO`) | ✔ | — |
| 30 | `Decimal`, nunca float | sección 4 | `modelos.py:7-16` (rechaza float); `reportes.py` | ✔ | — |
| 31 | Operaciones atómicas aun si falla un paso posterior | sección 4 | escenario 12 (despacho y venta revierten todo) | ✔ | — |
| 32 | Python 3.12, SQLite, sin dependencias externas | 2.2 | solo biblioteca estándar; corrido en 3.14.7 | ✔ | — |
| 33 | Navegador → API → `Sistema` → modelos y DAO → SQLite | 2.2 | `web.py:247-277` → `servicios.py` → `db.py:52-72` | ✔ | — |
| 34 | La interfaz solo valida tipos | 2.2 | `web.py:69-123` (tipos y forma del JSON) | ✔ | — |
| 35 | Bulto rechazado: no vuelve al CD, registra merma, el Observer lo vuelve a pedir | 2.4, sección 4 | `servicios.py` `verificar` (rama no íntegro); escenario 13; `test_rechazo_registra_merma_valorizada_e_inmutable` | ✔ | — |
| 36 | DER y UML | 2.3 | ver sección 5 | ⚠ modelo de diseño | Diferencias en la nota interna (sección 5); no se mencionan en la entrega |

### Escenarios ejecutados (esperado vs. obtenido)

| # | Escenario | Esperado | Obtenido |
|---|---|---|---|
| 1 | Vender 6 con stock 5 | falla, sin cambios | `Stock disponible insuficiente`; sin venta, cobro ni movimiento ✔ |
| 2 | Bulto con 11 de 10 pedidos / con 101 de 100 libres | falla | `Cantidad superior al pendiente…` / `Stock CD insuficiente para reservar` ✔ |
| 3 | Despachar remito con un bulto sin precintar | falla | `El bulto no permite despachar`; el primer bulto vuelve a PRECINTADO, la reserva queda intacta y el remito sigue PREPARADO ✔ |
| 4 | Recibir / verificar / volver a verificar | local 0 → 10 → 10 | recibir: local sin stock; verificar: 10; reintento: `El bulto no permite verificar`, sigue en 10 ✔ |
| 5 | Precinto roto | Rechazado con motivo, sin stock | sin motivo: `Rechazo requiere motivo`; con motivo: RECHAZADO, `integro=0`, local en 0 ✔ |
| 6 | UPDATE/DELETE en `historial` y `movimiento` | bloqueado | `IntegrityError: Historial inmutable` / `Movimiento inmutable` (×4) ✔ |
| 7 | Despachar un remito con bulto Recibido; precintar Recibido; recibir Preparado | error, sin cambio | `Remito ya despachado`, `no permite precintar`, `no permite recibir`; estados intactos ✔ |
| 8 | Código, CUIT, categoría y precinto duplicados | rechazo | `UNIQUE constraint failed` en los 4 ✔; dos principales por SQL directo también fallan ✔ |
| 9 | Cobros que no suman el total | falla | `Los cobros deben sumar el total exacto` (menor y mayor) ✔; además falla con medio inválido y si vende un CD ✔ |
| 10 | Devolver 4 de 3; venta 999; 2 + 2 de 3; no apta | fallan | `supera lo vendido pendiente`, `Registro inexistente`, `supera…`, `Solo se acepta mercadería apta` ✔ |
| 11 | Mínimo 30 con stock 20; repetir; vender 1; vender 1 | orden de 10, sin duplicar, luego 11 y 12 | 10 → 10 (repetir no duplica) → 11 → 12 ✔ |
| 11b | Orden de 20 con remito de 15 ya despachado; mínimo 25 | — | Los 5 no enviados siguen contando como "pendientes", así que el Observer pide 5 y no 10. Se pueden enviar con otro remito de la misma orden, pero nadie avisa (menor) |
| 12 | Error forzado en el 2.º bulto del despacho y al grabar el cobro | rollback total | estado, reserva, historial y movimientos idénticos; venta sin rastros ✔ |
| 13 | Rechazar el bulto de una orden automática | — | CD queda en 90 (descontado), local 0; movimientos solo COMPRA y DESPACHO; el Observer crea una **nueva orden de 10**. Tras el cambio: se registra la merma y el reporte muestra `merma: 60.00` |
| 14 | 4 reportes con datos conocidos | coincidencia | ventas EFECTIVO 30/20/10, DEBITO 20/0/20, CREDITO 30/0/30 ✔; margen P1: 6 u, 60,00, 24,00 ✔; rechazos: 1 bulto, 10 u ✔; tránsito: 2 bultos ✔; filtros por local y período ✔ |

---

## 5. Diferencias estructurales (nota interna del equipo, no va en la entrega)

> Los diagramas representan el modelo de diseño. El código implementa el mismo comportamiento con un esquema más compacto; estas diferencias quedan pendientes de alinear en el código. Esta nota estaba en la sección 2.3 del documento y se quitó porque el documento es la entrega formal.
>
> - **Inventario.** `stock` usa la clave (sucursal, producto) con `cantidad`, `reservada` y `minimo`; `movimiento_stock` se llama `movimiento` y se asocia a sucursal y producto, sin costo. La tabla `aviso` registra cada notificación del Observer.
> - **Logística.** `orden_reposicion`, `detalle_orden_reposicion` y `cambio_estado_bulto` se llaman `orden`, `detalle_orden` e `historial`; la orden no tiene estado ni `cantidad_enviada` (lo enviado se calcula sumando los bultos) y el remito no tiene número ni fecha. No hay `Recepcion`: la condición del precinto y el motivo de rechazo se guardan en `bulto` (`integro`, `motivo`).
> - **Ventas.** El comprobante es una columna de `venta`; el medio de pago es un texto de valores fijos en `cobro` y `devolucion`, sin tabla `medio_pago`. Cada devolución es de un producto (sin `detalle_devolucion`) y no guarda motivo.
> - **Clases.** Solo `Bulto` y sus estados, `Stock`, `ObservadorStock` y `GeneradorReposicionAutomatica` son clases; las demás entidades son tablas que opera `Sistema` mediante el DAO. Los cuatro reportes están en una sola clase `Reportes` (no hay interfaz `Reporte`) y el estado del remito se recalcula dentro de `Sistema.verificar()`.

Detalle completo:

**DER vs. esquema real (`db.py:5-30`):**
- No existen: `recepcion`, `medio_pago`, `comprobante`, `detalle_devolucion`.
- Con otro nombre: `cambio_estado_bulto` → `historial`, `movimiento_stock` → `movimiento`, `orden_reposicion` / `detalle_orden_reposicion` → `orden` / `detalle_orden`.
- Existen en el código y no en el DER: `aviso`. `ingreso` ya se agregó al DER.
- `stock`: el código usa PK (sucursal, producto) y `cantidad`/`reservada`/`minimo`; el DER usa `id` y `cantidad_disponible`/…
- `movimiento`: el código usa sucursal + producto, sin `costo_unitario`; el DER usa `stock_id`.
- `orden`: no tiene `estado`; `detalle_orden` no tiene `id` ni `cantidad_enviada`.
- `remito`: no tiene `numero` ni `fecha_emision`.
- `bulto`: tiene `precinto`, `integro` y `motivo`; no tiene `fecha_creacion`, y su estado no tiene CHECK de valores.
- `detalle_bulto`: apunta a `producto`, no a `detalle_orden`.
- `venta`: tiene `comprobante`; `cobro` usa `medio` TEXT con CHECK.
- `devolucion`: tiene `producto_id`, `cantidad`, `monto` y `medio`; no tiene `motivo`.
- `proveedor`: tiene `nombre`, no `razon_social` ni `telefono`.
- `producto`: tiene `precio`/`costo` y `activo`.
- Todas las entidades de catálogo y sucursal tienen `activo` (baja lógica) y no figura en el DER.

**UML vs. clases reales:** el código tiene `Bulto`, `EstadoBulto` + 6 estados, `Stock`, `ObservadorStock`, `GeneradorReposicionAutomatica`, `Sistema`, `BaseDatos`, `DAO` y `Reportes`. Del resto (`Venta`, `Remito`, `OrdenReposicion`, `Recepcion`, `Comprobante`, `MedioPago`, `Reporte` + 4 implementaciones, `Ingreso`, etc.) no hay clases: son filas que manipula `Sistema`. Los reportes **no** son Strategy (`if/elif` en `Reportes.generar`), por eso no se agregó como tercer patrón. Métodos del UML como `Stock.ingresarVerificado()`, `Venta.calcularTotal()` o `Remito.actualizarEstadoSegunBultos()` viven como lógica dentro de `Sistema`.

**Estados (Figura 3 / Tabla 4 vs. código):** después de la corrección coinciden. Estados: `PREPARADO, PRECINTADO, EN_TRANSITO, RECIBIDO, VERIFICADO, RECHAZADO` (`modelos.py:41-67`). Transiciones: `precintar`, `despachar`, `recibir`, `verificar(integro)`; cualquier otra lanza `ValueError` (`modelos.py:28-38`).

---

## 6. Fase 3: cambios de código propuestos (esperan tu OK)

| Prioridad | Cambio | Afecta a | Esfuerzo / riesgo | Recomendación |
|---|---|---|---|---|
| 1 | **Registrar la merma al rechazar** | 2.4, sección 4, Tabla 3 | Chico / bajo | ✅ **Implementado**: costo = costo vigente del producto al rechazar. Los rechazos anteriores al cambio siguen mostrando "NO DETERMINADA" (por eso regenerar la base de la demo). |
| 2 | Reglas de devolución: plazo y medio de reintegro igual al de la venta | Tabla 2 f5 | Chico / bajo | ❌ **Descartado** por el grupo: el enunciado no pide plazo; las reglas son las ya implementadas (apta, venta registrada, cantidad). |
| 3 | Pendiente de órdenes ya remitidas (escenario 11b): que `consolidar_faltante` no cuente como pendiente lo que no entró en ningún remito despachado, o cerrar la orden al despachar. | Tabla 1 f3 ("sin duplicar unidades ya pedidas") | Mediano / medio | Posponer; no aparece en una demo normal. |
| 4 | Compra con encabezado y detalle (`compra` / `detalle_compra`) en lugar de `ingreso` por producto. | Tabla 1 (Compras), 2.2 | Mediano / medio (servicio, web, demo, tests) | **No ahora**: el documento ya describe `ingreso` como lo que es. |
| 5 | `medio_pago_id` en devolución | — | — | **No hace falta**: `devolucion.medio` ya existe (`db.py:24`). |
| 6 | Pasar la condición del precinto de `recibir` a `verificar` (versión propuesta de C1). | Tabla 4, Figura 3 | Mediano / medio (servicio, `app.js`, demo, tests) | **No recomendado**: el documento ya es coherente con el código. |
| 7 | Índice único parcial del proveedor principal | — | — | **Ya existe** (`db.py:11`). |
| 8 | Alinear esquema y clases con el modelo de diseño (lo que lista la nota interna, sección 5). | Figuras 1-2 | Grande / alto | Después de la presentación, o redibujar los diagramas según el código. |
| 9 | Habilitar stock solo con el remito completo Verificado (lectura literal del enunciado). | V1 | Mediano / alto | Solo si la cátedra lo exige (contradicción 1). |
| 10 | Cosmético: reporte de ventas con "0.00" en vez de "0". | Tabla 3 | Trivial / nulo | Opcional. |

---

## 7. Checklist de demo para la presentación

Preparación: una base nueva, para no arrastrar pruebas.
```bash
python3 -m distribucion.demo_web --db presentacion.db
python3 main.py --web --db presentacion.db --port 8080
```
Datos: CD Córdoba; locales Centro, Nueva Córdoba y General Paz; productos Yerba, Arroz, Aceite y Fideos; 10 bultos repartidos en todas las etapas, incluido un rechazado (DEMO-002).

1. **Tablero (State, ciclo de vida).** Mostrar las columnas por estado. Abrir un bulto Verificado: historial con responsable y fecha. Señalar que cada tarjeta ofrece **solo** la acción siguiente válida → Tabla 4.
2. **Preparar → Precintar → Despachar** un bulto Preparado. Antes y después, en Inventario: el CD tiene reserva al preparar y la cantidad baja al despachar → Tabla 1 f4-f5, "Stock reservado".
3. **Despacho incompleto:** intentar despachar un remito con un bulto sin precintar → error, nada cambia → Tabla 1 f5.
4. **Recibido ≠ Disponible:** registrar la llegada de un bulto En tránsito con precinto **íntegro**; en Inventario el stock del local **no** cambia. Verificar → ahora sí sube → Tabla 2 f1.
5. **Rechazo y merma:** llegada con precinto **roto**, verificar sin motivo (error) y con motivo → Rechazado; el stock no sube. Abrir Reportes → Bultos rechazados: aparece la merma en pesos (la demo trae DEMO-002: 5 u = $8.001,25) → Tabla 3 f3, 2.4.
6. **Observer:** en Inventario, definir un mínimo mayor que el stock de un local → aparece el aviso y la orden automática; repetir y mostrar que **no duplica** → 3 Observer.
7. **Venta:** carrito con 2 productos y 2 medios de pago; probar primero cobros que no suman (error) y una cantidad mayor al stock (error); después la venta OK → comprobante `V-xxxxxxxx`.
8. **Devolución:** devolver parte de la venta → el stock sube y el reintegro va a precio histórico; intentar devolver de más (error) → Tabla 2 f5.
9. **Reportes:** ventas por local y medio (cobrado / reintegrado / neto), margen, rechazos y tránsito; filtrar por período y local; **exportar CSV** → Tabla 3.
10. **Inmutabilidad y atomicidad** (opcional, en terminal): `python3 -m unittest discover -s tests -v` y mostrar `test_integridad_historial_movimientos_fk` y `test_venta_fallida_revierte_todo` → Tabla 2 f2 y f6.
11. **Compras:** en Inventario, registrar un ingreso de proveedor al CD con costo → movimiento COMPRA → Tabla 1, fila "Compras / ingreso al CD".

Preguntas probables y respuesta corta:
- *¿Por qué el stock se habilita por bulto y no por remito?* → "Recepción por bulto" (sección 4), confirmado con la cátedra.
- *¿Qué pasa con lo rechazado?* → se registra como merma (inmutable) y se valoriza; no vuelve al CD porque físicamente está en el local; el Observer repone.
- *¿Dónde está el DAO?* → `db.py`, clases `BaseDatos` y `DAO` (2.2).

---

## 8. Cambios en el documento (antes / después)

### Tabla 1, fila 2 (C7)
- **Antes:** ABM del catálogo; relación producto–proveedor con costo y proveedor principal; stock mínimo por sucursal y producto; código de producto y CUIT únicos.
- **Después:** ABM del catálogo; relación producto–proveedor con costo y un único proveedor principal por producto (lo garantiza un índice único parcial); stock mínimo por sucursal y producto; código de producto, CUIT y nombre de categoría únicos.

### Tabla 1, fila 3 (C7, RN-07)
- **Antes:** Órdenes con origen (CD) y destino (local) y sus detalles. También se generan o consolidan automáticamente cuando un stock queda bajo el mínimo (Observer), sin duplicar unidades ya pedidas.
- **Después:** Órdenes con origen (CD) y destino (local) y sus detalles; el servicio valida que el origen sea un CD y el destino un local. También se generan o consolidan automáticamente cuando un stock queda bajo el mínimo (Observer), sin duplicar unidades ya pedidas.

### Tabla 1, fila 6 (C1)
- **Antes:** El local registra la llegada (Recibido) y luego verifica: con precinto íntegro el bulto pasa a Verificado y su contenido ingresa al stock; con precinto roto pasa a Rechazado con motivo y no habilita venta.
- **Después:** El local registra la llegada (Recibido) indicando la condición del precinto, y luego verifica: si el precinto estaba íntegro el bulto pasa a Verificado y su contenido ingresa al stock; si estaba roto pasa a Rechazado con motivo obligatorio y no habilita venta.

### Tabla 1, fila 7 (C3)
- **Antes:** Venta multiproducto con uno o más cobros (efectivo, débito, crédito, transferencia) cuya suma debe igualar el total; comprobante con número único; devoluciones referidas a una venta registrada, con reingreso a stock y reintegro.
- **Después:** Venta multiproducto con uno o más cobros (efectivo, débito, crédito, transferencia) cuya suma debe igualar el total; comprobante con número único; devoluciones referidas a una venta registrada, con reingreso a stock y reintegro por el medio de pago elegido.

### Tabla 1, fila nueva (C4)
- **Antes:** 7. Ventas, cobros, comprobante y devoluciones
- **Después:** Compras / ingreso al CD

### Tabla 1, fila nueva (C4)
- **Antes:** Venta multiproducto con uno o más cobros (efectivo, débito, crédito, transferencia) cuya suma debe igualar el total; comprobante con número único; devoluciones referidas a una venta registrada, con reingreso a stock y reintegro por el medio de pago elegido.
- **Después:** Ingreso de mercadería de un proveedor al CD: registra proveedor, producto, cantidad y costo unitario; suma el stock del CD con un movimiento de tipo COMPRA y actualiza el costo del producto. No pasa por verificación logística.

### Tabla 2, fila 1 (C1)
- **Antes:** El ingreso al stock del local ocurre únicamente en la transición Recibido → Verificado, controlada por el patrón State.
- **Después:** El ingreso al stock del local ocurre únicamente en la transición Recibido → Verificado, controlada por el patrón State. La condición del precinto se registra al recibir y se resuelve al verificar: si está roto, el bulto pasa a Rechazado.

### Tabla 2, fila 5 (C3)
- **Antes:** Deben referenciar una venta registrada y no superar lo vendido menos lo ya devuelto; el reintegro usa el precio histórico de la venta.
- **Después:** Deben referenciar una venta registrada y un producto incluido en ella, no superar lo vendido menos lo ya devuelto y corresponder a mercadería apta para reingreso. El reintegro usa el precio histórico de la venta y se registra con su medio de pago.

### Tabla 3, fila 1 (C3)
- **Antes:** Cobrado, reintegrado y neto, agrupados por local y medio de pago.
- **Después:** Cobrado, reintegrado y neto (cobrado − reintegrado), agrupados por local y medio de pago; cada devolución guarda el medio por el que se reintegró.

### 2.2 Fuera del alcance (C4)
- **Antes:** Fuera del alcance. No se implementaron los procesos opcionales (órdenes de compra sugeridas, promociones y listas de precios, lotes y vencimientos, clientes frecuentes y cuentas corrientes, inventario físico), ni autenticación por roles, facturación fiscal, pagos reales o despliegue público. Las compras se cubren con el ingreso de mercadería de un proveedor al CD, con cantidad y costo.
- **Después:** Fuera del alcance. No se implementaron los procesos opcionales (órdenes de compra sugeridas, promociones y listas de precios, lotes y vencimientos, clientes frecuentes y cuentas corrientes, inventario físico), ni autenticación por roles, facturación fiscal, pagos reales o despliegue público. Las compras se registran como ingresos de mercadería de un proveedor al CD: proveedor, producto, cantidad y costo unitario, con un movimiento de stock de tipo COMPRA. No hay órdenes de compra ni una entidad de compra con detalle.

### 2.2 Arquitectura (C7, DAO)
- **Antes:** Arquitectura. Navegador → API HTTP local → servicios (Sistema) → modelos y DAO → SQLite. La interfaz solo valida tipos; las reglas de negocio viven en los servicios y en el modelo de dominio.
- **Después:** Arquitectura. Navegador → API HTTP local → servicios (Sistema) → modelos y DAO → SQLite. La persistencia la resuelven BaseDatos (conexión, esquema, triggers y transacciones) y un DAO genérico con consultas parametrizadas; no figuran en el diagrama de clases porque este modela el dominio. La interfaz solo valida tipos; las reglas de negocio viven en los servicios y en el modelo de dominio.

### 2.3 Nota (C6)
- **Antes:** Nota: los diagramas representan el modelo de diseño. En el código algunos nombres y estructuras se simplificaron.
- **Después:** Nota: los diagramas representan el modelo de diseño. El código implementa el mismo comportamiento con un esquema más compacto; estas diferencias quedan pendientes de alinear en el código:

### 2.3 Nota, viñeta nueva (C6)
- **Antes:** (nuevo)
- **Después:** •	Inventario. stock usa la clave (sucursal, producto) con cantidad, reservada y minimo; movimiento_stock se llama movimiento y se asocia a sucursal y producto, sin costo. Los ingresos de proveedor están en la tabla ingreso, y la tabla aviso registra cada notificación del Observer.

### 2.3 Nota, viñeta nueva (C6)
- **Antes:** (nuevo)
- **Después:** •	Logística. orden_reposicion, detalle_orden_reposicion y cambio_estado_bulto se llaman orden, detalle_orden e historial; la orden no tiene estado ni cantidad_enviada (lo enviado se calcula sumando los bultos) y el remito no tiene número ni fecha. No hay Recepcion: la condición del precinto y el motivo de rechazo se guardan en bulto (integro, motivo).

### 2.3 Nota, viñeta nueva (C6)
- **Antes:** (nuevo)
- **Después:** •	Ventas. El comprobante es una columna de venta; el medio de pago es un texto de valores fijos en cobro y devolucion, sin tabla medio_pago. Cada devolución es de un producto (sin detalle_devolucion) y no guarda motivo.

### 2.3 Nota, viñeta nueva (C6)
- **Antes:** (nuevo)
- **Después:** •	Clases. Solo Bulto y sus estados, Stock, ObservadorStock y GeneradorReposicionAutomatica son clases; las demás entidades son tablas que opera Sistema mediante el DAO. Los cuatro reportes están en una sola clase Reportes (no hay interfaz Reporte) y el estado del remito se recalcula dentro de Sistema.verificar().

### Tabla 4, En tránsito (C1)
- **Antes:** recibir()
- **Después:** recibir(integro)

### Tabla 4, En tránsito (C1)
- **Antes:** Registra la llegada; todavía no habilita venta.
- **Después:** Registra la llegada y la condición del precinto; todavía no habilita venta.

### Tabla 4, Recibido roto (C1)
- **Antes:** verificar() con precinto roto
- **Después:** verificar(motivo) con precinto roto

### Tabla 4, Recibido roto (C1, C5)
- **Antes:** Registra el motivo; no impacta el stock vendible.
- **Después:** Registra el motivo (obligatorio); no impacta el stock del local ni devuelve unidades al CD.

### 2.4 párrafo nuevo (C5)
- **Antes:** (nuevo)
- **Después:** Bulto rechazado. Un bulto Rechazado no ingresa al stock del local. Como el stock del CD ya se descontó al despachar, sus unidades no vuelven al CD ni se registran como movimiento de merma: solo quedan identificadas en el reporte de bultos rechazados (limitación conocida). Al resolverse el bulto, esas unidades dejan de contarse como pendientes de la orden, por lo que, si el local sigue bajo su mínimo, el Observer las vuelve a pedir en una nueva orden de reposición.

### 3. State (C1)
- **Antes:** State. El bulto mantiene un objeto estado y le delega cada operación. EstadoBulto define todas las acciones lanzando error por defecto y cada estado concreto sobrescribe solo las que permite; por eso un reintento sobre un bulto Verificado no vuelve a ingresar stock. El estado se guarda como texto en la base y se reconstruye como objeto al recuperarlo.
- **Después:** State. El bulto mantiene un objeto estado y le delega cada operación. EstadoBulto define todas las acciones lanzando error por defecto y cada estado concreto sobrescribe solo las que permite; por eso un reintento sobre un bulto Verificado no vuelve a ingresar stock. Recibido.verificar() resuelve el destino con la condición del precinto registrada al recibir: Verificado si estaba íntegro, Rechazado si estaba roto. El estado se guarda como texto en la base y se reconstruye como objeto al recuperarlo.

### 3. Observer (C6)
- **Antes:** Observer. Stock.notificar() compara el disponible con el mínimo y llama a actualizar() de cada observador registrado. GeneradorReposicionAutomatica consolida el faltante en una orden de reposición desde el CD. Se puede agregar otro observador sin modificar el sujeto.
- **Después:** Observer. Stock.notificar() compara el disponible (cantidad menos reservada) con el mínimo y, si queda por debajo, llama a actualizar(stock) de cada observador registrado. Sistema lo invoca después de vender, verificar un bulto o definir un mínimo. GeneradorReposicionAutomatica registra un aviso y consolida el faltante en la orden abierta del CD hacia ese local (o crea una), descontando lo ya pedido y todavía pendiente. Se puede agregar otro observador sin modificar el sujeto.

### 4. Recepción por bulto (C2)
- **Antes:** •	Recepción por bulto. Cada bulto se verifica individualmente; un remito con bultos verificados y rechazados queda parcialmente aceptado.
- **Después:** •	Recepción por bulto. Cada bulto se verifica individualmente. El remito pasa a En tránsito al despacharse y se recalcula tras cada verificación: En revisión mientras falten bultos, y Verificado, Rechazado o Parcialmente aceptado cuando todos terminaron.

### 4. viñeta nueva (C5)
- **Antes:** (nuevo)
- **Después:** •	Bulto rechazado. No ingresa al stock del local ni vuelve al CD, y no se registra un movimiento de merma: las unidades solo quedan identificadas en el reporte de rechazos (limitación conocida). Si el local sigue bajo su mínimo, el Observer las vuelve a pedir.

### 4. viñeta nueva (C3)
- **Antes:** (nuevo)
- **Después:** •	Devoluciones sin verificación logística. Lo devuelto reingresa directamente al stock vendible del local: la mercadería no viajó ni estuvo precintada, la inspecciona quien atiende y solo se acepta si se marca como apta para reingreso.

### 4. viñeta nueva (C4)
- **Antes:** (nuevo)
- **Después:** •	Compra vs. reposición. La compra (proveedor → CD) ingresa stock al CD sin verificación logística porque el CD no vende al público; solo la mercadería que llega a un local pasa por Recibido → Verificado.


## 9. Cambios por la merma (C5, opción B)

### Tabla 2, fila 2 (C5)
- **Antes:** Cada transición inserta un registro de historial (estado anterior y nuevo, fecha y responsable). Triggers de SQLite bloquean UPDATE y DELETE sobre el historial y los movimientos de stock.
- **Después:** Cada transición inserta un registro de historial (estado anterior y nuevo, fecha y responsable). Triggers de SQLite bloquean UPDATE y DELETE sobre el historial, los movimientos de stock y las mermas.

### Tabla 3, fila 3 (C5)
- **Antes:** Bultos rechazados por rotura de precinto: unidades, motivo, destino y fecha.
- **Después:** Bultos rechazados por rotura de precinto: unidades, motivo, destino, fecha y merma valorizada al costo del producto.

### Tabla 4, Recibido roto (C5)
- **Antes:** Registra el motivo (obligatorio); no impacta el stock del local ni devuelve unidades al CD.
- **Después:** Registra el motivo (obligatorio) y la merma; no impacta el stock del local ni devuelve unidades al CD.

### 2.4 Bulto rechazado (C5)
- **Antes:** Bulto rechazado. Un bulto Rechazado no ingresa al stock del local. Como el stock del CD ya se descontó al despachar, sus unidades no vuelven al CD ni se registran como movimiento de merma: solo quedan identificadas en el reporte de bultos rechazados (limitación conocida). Al resolverse el bulto, esas unidades dejan de contarse como pendientes de la orden, por lo que, si el local sigue bajo su mínimo, el Observer las vuelve a pedir en una nueva orden de reposición.
- **Después:** Bulto rechazado. Un bulto Rechazado no ingresa al stock del local ni vuelve al CD, cuyo stock ya se descontó al despachar. Su contenido se registra como merma (producto, cantidad, costo vigente y motivo) en un registro inmutable, y el reporte de bultos rechazados la valoriza. Al resolverse el bulto, esas unidades dejan de contarse como pendientes de la orden, por lo que, si el local sigue bajo su mínimo, el Observer las vuelve a pedir en una nueva orden de reposición.

### 4. Bulto rechazado (C5)
- **Antes:** •	Bulto rechazado. No ingresa al stock del local ni vuelve al CD, y no se registra un movimiento de merma: las unidades solo quedan identificadas en el reporte de rechazos (limitación conocida). Si el local sigue bajo su mínimo, el Observer las vuelve a pedir.
- **Después:** •	Bulto rechazado. No ingresa al stock del local ni vuelve al CD; su contenido queda registrado como merma, valorizada al costo vigente del producto, y la muestra el reporte de rechazos. Si el local sigue bajo su mínimo, el Observer vuelve a pedir esas unidades.

### 2.3 Nota, Inventario (ingreso y merma ya figuran en el DER)
- **Antes:** •	Inventario. stock usa la clave (sucursal, producto) con cantidad, reservada y minimo; movimiento_stock se llama movimiento y se asocia a sucursal y producto, sin costo. Los ingresos de proveedor están en la tabla ingreso, y la tabla aviso registra cada notificación del Observer.
- **Después:** •	Inventario. stock usa la clave (sucursal, producto) con cantidad, reservada y minimo; movimiento_stock se llama movimiento y se asocia a sucursal y producto, sin costo. La tabla aviso registra cada notificación del Observer.


## 10. Ajuste posterior

- Se quitó de la sección 4 la viñeta "Devoluciones sin verificación logística": la única condición es que la mercadería esté apta (buen estado), ya indicada en la Tabla 2; no hay reglas de fechas.

## 11. Observaciones de revisión (figuras, Merma, verificar, devoluciones)

- **Figuras 1 y 2:** su sección del documento pasa a A4 horizontal y las imágenes se agrandan (Fig. 1: 18,8 → 25,6 cm de ancho; Fig. 2: 19,0 → 24,0 cm). Las exportaciones JPG salen a escala 3×, así que se leen al hacer zoom en el PDF. Al reemplazarlas en Word usar «Cambiar imagen» (conserva el tamaño) y desactivar la compresión de imágenes al guardar.
- **Merma en el UML:** se agrega la clase `Merma` (logística, celda [3,5]) con `fecha`, `cantidad`, `costoUnitario`, `motivo` y `valorizar()`. Relaciones: `Bulto` ◆ 1 — 0..* `Merma` («si rechazado») y `Merma` 0..1 → 1 `DetalleBulto` («valoriza»). No cruza otras líneas.
- **Firma de verificar:** `EstadoBulto`/`Recibido.verificar(b, integro)` → `verificar(b, precintoIntegro)`. Coincide con el código (`modelos.Recibido.verificar(bulto, integro)`): `Sistema.verificar` lee `bulto.integro` registrado en `recibir` y se lo pasa al estado. El texto de State lo explica.
- **Devolución:** `Devolucion.validar()` → `validar(apta: boolean)` en el UML. Tabla 2 enumera los rechazos que hace `Sistema.devolver`: producto que no figura en la venta (`DAO.uno` lanza `ValueError`), unidades acumuladas mayores a las vendidas, operador indica que no está en buen estado (`apto is not True`) y medio de reintegro inválido. El buen estado no es un campo del DER porque las devoluciones rechazadas no se graban.
- Figura 2 cambió de nuevo: hay que volver a exportarla.
### 2.3 Figura 1
- **Antes:** página vertical, 18.8 × 11.4 cm
- **Después:** página horizontal, 25.6 × 15.5 cm

### 2.3 Figura 2
- **Antes:** página vertical, 19.0 × 12.3 cm
- **Después:** página horizontal, 24.0 × 15.5 cm

### 3. State (firma de verificar)
- **Antes:** State. El bulto mantiene un objeto estado y le delega cada operación. EstadoBulto define todas las acciones lanzando error por defecto y cada estado concreto sobrescribe solo las que permite; por eso un reintento sobre un bulto Verificado no vuelve a ingresar stock. Recibido.verificar() resuelve el destino con la condición del precinto registrada al recibir: Verificado si estaba íntegro, Rechazado si estaba roto. El estado se guarda como texto en la base y se reconstruye como objeto al recuperarlo.
- **Después:** State. El bulto mantiene un objeto estado y le delega cada operación. EstadoBulto define todas las acciones lanzando error por defecto y cada estado concreto sobrescribe solo las que permite; por eso un reintento sobre un bulto Verificado no vuelve a ingresar stock. Bulto.verificar(motivo) no recibe la condición del precinto: toma el precintoIntegro registrado en la recepción y se lo pasa al estado, Recibido.verificar(b, precintoIntegro), que resuelve Verificado si estaba íntegro o Rechazado si estaba roto. El motivo solo se exige en el rechazo. El estado se guarda como texto en la base y se reconstruye como objeto al recuperarlo.

### Tabla 2, Devoluciones válidas
- **Antes:** Deben referenciar una venta registrada y un producto incluido en ella, no superar lo vendido menos lo ya devuelto y corresponder a mercadería apta para reingreso. El reintegro usa el precio histórico de la venta y se registra con su medio de pago.
- **Después:** Se rechaza la devolución si el producto no figura en la venta, si las unidades, sumadas a las ya devueltas, superan las vendidas, si el operador indica que el producto no está en buen estado para volver a venderse o si el medio de reintegro no es válido. Las rechazadas no se graban, por eso el buen estado se valida al registrar y no es un campo de la tabla. Las aceptadas reintegran al precio histórico de la venta y devuelven las unidades al stock del local.

