# Decisiones de implementación

Aceptadas por Juan el 23/10/2026 para avanzar. Este documento resuelve las propuestas anteriores del negocio y plan; la validación académica sigue pendiente.

1. **Stock:** `cantidad` es existencia física segura; `reservada` pertenece a bultos preparados/precintados. Disponible = cantidad − reservada. Preparar reserva; despachar libera la reserva y descuenta existencia en la misma transacción. No se permite sobreempaquetar una orden ni sobrereservar el CD. No se ofrece cancelar bultos/órdenes: una reserva se libera despachando; anular logística queda fuera del alcance inicial.
2. **Ingreso CD:** ingreso mínimo de proveedor con cantidad y costo; crea movimiento y actualiza el costo de referencia del producto. No implementa cuentas corrientes, deuda ni ciclo de órdenes de compra. Cada ingreso confirmado es una compra distinta.
3. **Remito mixto:** cada bulto verificado habilita su contenido inmediatamente. El remito se considera EN_REVISION mientras quedan bultos sin resolver, y al finalizar VERIFICADO, RECHAZADO o PARCIALMENTE_ACEPTADO. **Es una interpretación de RN-01 pendiente de cátedra**, no una confirmación de su aceptación. No se requiere un estado Disponible del bulto.
4. **Rechazo:** conserva cantidades y motivo; no habilita venta ni constituye automáticamente merma/retorno. Los reportes indican “merma no determinada”. Un rechazo deja de contar como reposición pendiente y puede generar un pedido de reemplazo al avisar stock bajo.
5. **Devolución:** venta registrada, producto incluido, cantidad acumulada no mayor a la vendida; solo apto para reingreso. Sin plazo máximo impuesto. Stock e importe reintegrado al precio original se registran juntos. El medio de reintegro se elige explícitamente; no necesita coincidir con el cobro original.
6. **Observer:** toda venta y verificación chequea mínimo; definir mínimo también puede avisar. Registra aviso por evento bajo mínimo (puede haber avisos repetidos, pero no cantidades duplicadas). Faltante = mínimo − disponible − solicitado pendiente. Solicitado pendiente = detalle de órdenes menos bultos terminales. Consolida una orden aún sin remitos; si ya se inició logística crea otra. Si hay varios CD activos, usa el menor ID para reposición automática; la reposición manual permite elegir. Sin CD activo, un aviso de local revierte la operación para no perder reposición silenciosamente.
7. **Bajas:** lógicas en sucursales, categorías, proveedores y productos. Conservan FK y auditoría. Se impiden nuevas operaciones de catálogo/comerciales con entidades inactivas; la logística ya despachada y las devoluciones siguen pudiendo concluir para no dejar mercadería sin resolver. Tipo de sucursal inmutable luego del alta.
8. **Dinero:** Decimal validado, persistido como TEXT. Reportes agregan Decimal en Python. Se corrigió la propuesta previa de `CAST AS REAL` porque introduciría floats. Precio y costo de cada venta son históricos, las modificaciones del catálogo no los alteran. Costo de referencia: último ingreso del proveedor, sin costo promedio ponderado.
9. **Atomicidad:** `BEGIN IMMEDIATE` por comando, un commit/rollback del servicio. DAO sin commits; Observer participa de la misma transacción. Un fallo tardío revierte venta, cobros, movimientos y pedidos. Transiciones y cantidades protegen reintentos de despacho/verificación/devolución. Dos confirmaciones de venta o ingreso son dos operaciones distintas: no hay clave de idempotencia para comandos nuevos.
10. **Auditoría:** triggers prohíben UPDATE y DELETE del historial y movimientos; no protege de un administrador que modifique el esquema o el archivo SQLite. Responsable provisto manualmente; no hay autenticación ni roles.
11. **Stack:** solo biblioteca estándar; pydantic era una propuesta, no necesaria para estas validaciones. Python 3.12+, sin sintaxis exclusiva de 3.13. La web local es la interfaz principal; Tkinter se conserva como alternativa. El formato de interfaz sigue pendiente de confirmación académica.

## Reportes

- **ventas:** cobros y reintegros agrupados por sucursal/medio. Neto = cobrado − reintegrado. Cuenta ventas distintas por medio, por eso una venta con pagos divididos figura una vez en cada medio: **no sumar esos conteos para obtener ventas totales**. Los importes no se duplican por joins. Período según fecha de cobro (igual a venta) o devolución.
- **margen:** unidades e ingresos netos, margen estimado (precio − costo histórico) × cantidad; devoluciones descuentan al período de la devolución. Puede haber margen/unidades negativos en un período con devoluciones de ventas anteriores. Top por unidades netas, filtro opcional por local.
- **rechazos:** bultos rechazados, unidades, destino, fecha y motivo; merma no determinada. No convierte automáticamente unidades en pérdida económica.
- **transito:** duración de EN_TRANSITO a RECIBIDO, promedio y máximo por destino; incluye también los posteriormente rechazados. Filtra fecha de llegada. Reporte usa duración exacta en microsegundos y Decimal para horas.

Fechas UTC inclusive. Estado del inventario y precio/costo siempre consultados dentro de la transacción de negocio. SQLite serializa escrituras; es una aplicación académica local, no un sistema distribuido.

## Verificación de esta entrega

- Tests de integración en SQLite `:memory:`: flujo completo, reserva, no sobreventa, precintos, mixtos, devoluciones acumuladas, Observer múltiple y pendientes, FK, triggers, rollback tardío, reportes exactos y catálogo.
- Demo reproducida en dos bases independientes, y ejecución CLI sobre archivo.
- Compilación Python y smoke de construcción Tk con todas las pestañas/tablas/reportes. El Python del sistema no trae `_tkinter`; el runtime Python 3.12 de Codex sí permite la prueba con sesión gráfica fuera del sandbox. No se realizó una prueba de interacción visual completa por un humano ni en Windows.

## Interfaz web Andén

- La interfaz principal es ahora una aplicación web local. Mantiene servicios, State, Observer, transacciones y base existentes.
- Tablero por seis estados, contenido e historial de bultos, acciones válidas según estado y filtros de destino/búsqueda.
- CRUD de catálogo con baja lógica; ingresos, mínimos y proveedores; órdenes, remitos y bultos; ventas multiproducto con pagos divididos; devoluciones; reportes y CSV.
- Entidades seleccionadas por nombre; los IDs siguen existiendo internamente. Dinero enviado como texto a la API y calculado con Decimal en backend. El total previo de venta usa centavos enteros.
- El servidor local no es un despliegue público. Host/Origin locales, payload acotado, archivos estáticos permitidos, CSP sin recursos remotos y SQLite por solicitud.
- Demo visual reproducible: `python3 -m distribucion.demo_web --db demo-anden.db`, una vez sobre base vacía.
- El grupo debe confirmar con la cátedra el formato de interfaz aceptado y revisar los supuestos del dominio.
