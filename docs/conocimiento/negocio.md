# Conocimiento del negocio — Tema 3: Centro de Distribución a Locales

Fuente: [tema3.pdf](../../tema3.pdf). Este documento es la referencia única del dominio: si algo del código o de una user story contradice esto, se discute y se actualiza acá primero.

## 1. Contexto

Un comercio minorista con varios **locales** se abastece desde un **Centro de Distribución (CD)** central.
Cada local vende al público, controla su stock y pide reposición al CD. El CD arma **bultos**, los despacha y el local los recibe.

> Regla de oro: **nada ingresa a stock vendible sin verificación.**

El sistema integra compras, ventas, inventario y logística interna, y permite conocer el resultado económico por período.

## 2. Glosario

| Término | Significado |
|---|---|
| Sucursal | Local de venta **o** el Centro de Distribución (se distingue por `TipoSucursal`). |
| Centro de Distribución (CD) | Sucursal especial que prepara y despacha mercadería. No vende al público. |
| Producto | Artículo comercializable. Identificador único: `codigo`. |
| Categoría | Agrupación de productos. |
| Proveedor | Quien vende al comercio. Identificador único: `cuit`. |
| Stock | Existencia de **un producto en una sucursal**. Tiene `stockMinimo`. |
| Movimiento de stock | Registro inmutable de cada entrada/salida (venta, recepción, devolución, ajuste). |
| Orden de reposición | Consolida las necesidades de un local hacia el CD. Tiene **origen (CD)** y **destino (local)**. |
| Remito | Documento de despacho que agrupa uno o más bultos de una orden. |
| Bulto / Contenedor | Unidad física que viaja del CD al local, con **precinto de seguridad**. |
| Precinto | Código de seguridad del bulto. Si llega roto → rechazo logístico. |
| Recepción | Registro de llegada del bulto al local, indicando si el precinto está íntegro. |
| Venta | Operación con uno o más productos, cobrada con uno o más medios de pago. |
| Comprobante | Documento emitido por la venta. |
| Devolución | Reintegro total o parcial de productos de una venta registrada. |

## 3. Procesos obligatorios

1. **ABM de sucursales y CD.**
2. **ABM de productos, categorías, precios, stock mínimo y proveedores.**
3. **Orden de reposición:** consolidar necesidades de un local en una orden CD → local.
4. **Empaquetado:** armar bultos con mercadería de la orden, asignar remito y precinto.
5. **Despacho:** registrar la salida de los bultos desde el CD.
6. **Recepción:** registrar la llegada al local verificando el precinto.
7. **Ventas:** venta con N productos, cobro con medios de pago, comprobante, devoluciones con impacto en stock y caja.

Opcionales (solo si sobra tiempo): órdenes de compra sugeridas, promociones/listas de precios, lotes/vencimientos, clientes frecuentes, inventario físico.

## 4. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Cada bulto verificado habilita su contenido; remito mixto queda parcialmente aceptado. Interpretación de la condición literal bulto/remito verificados, pendiente de cátedra: ver [implementación](../implementacion.md). |
| RN-02 | Si el precinto llega roto, el bulto pasa a **Rechazado** y no habilita venta. |
| RN-03 | El historial de estados del bulto es **inmutable** (solo inserciones). |
| RN-04 | No se puede vender más que el stock **disponible y verificado** del local. |
| RN-05 | No pueden existir dos productos con el mismo `codigo` ni dos proveedores con el mismo `cuit`. |
| RN-06 | Una devolución debe referenciar una venta registrada y no superar lo vendido menos lo ya devuelto (`cantidadDevolvible()`). |
| RN-07 | Una orden de reposición tiene origen = CD y destino = local (no CD → CD, no local → local). |
| RN-08 | Un bulto solo puede contener productos de la orden de su remito y no más de lo pendiente de enviar. |
| RN-09 | Cuando un stock queda por debajo de su mínimo se notifica a los observadores (patrón Observer). |
| RN-10 | La suma de los cobros de una venta debe igualar el total. |
| RN-11 | Una devolución reingresa stock y genera egreso de caja (`montoReintegrado`). |

## 5. Patrones de diseño (mínimo 2 obligatorios)

| Patrón | Dónde | Para qué |
|---|---|---|
| **State** | `EstadoBulto` + `EstadoPreparado`, `EstadoPrecintado`, `EstadoEnTransito`, `EstadoRecibido`, `EstadoVerificado`, `EstadoRechazado` | Cada estado decide qué transiciones permite; elimina los `if estado == ...`. Ciclo de vida: [maquina-estados-bulto.html](../diagramas/maquina-estados-bulto.html). |
| **Observer** | `Stock` (sujeto) → `ObservadorStock` → `GeneradorReposicionAutomatica` | Avisar cuando un producto queda bajo el mínimo. |
| Strategy (extra) | `EstrategiaPrecio` → `PrecioLista`, `PrecioPromocional`, `PrecioPorVolumen` | Cálculo de precio intercambiable. Opcional. |

## 6. Reportes (mínimo 4 no triviales)

| Reporte | Clase | Datos |
|---|---|---|
| Ventas e ingresos por período, local y medio de pago | `ReporteVentasPorPeriodo` | Venta, Cobro, MedioPago, Sucursal |
| Más vendidos y margen estimado | `ReporteMasVendidosYMargen` | DetalleVenta (`precioUnitario` − `costoUnitario`) |
| Bultos rechazados / mermas por precinto | `ReporteBultosRechazados` | CambioEstadoBulto, Recepcion |
| Tiempo promedio de tránsito CD → local | `ReporteTiempoTransito` | CambioEstadoBulto (En tránsito → Recibido) |

Otros sugeridos: existencias actuales y productos en stock mínimo, valorización del inventario.

## 7. Decisiones pendientes

- [x] Lenguaje y base de datos: Python + SQLite → [stack.md](../stack.md).
- [x] Valores de los enums implementados en el esquema y servicios; ver [implementación](../implementacion.md). Propuesta inicial: `TipoSucursal`, `EstadoOrden`, `EstadoRemito`, `TipoMovimiento`, `TipoMedioPago`.
- [x] Preparar reserva; despachar descuenta y libera reserva.
- [x] Solo apta, venta registrada y cantidades acumuladas limitadas. Sin plazo máximo impuesto.
- [x] Rechazado no habilita venta; no es automáticamente merma ni retorno.
