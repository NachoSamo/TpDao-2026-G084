> Actualización 23/10/2026: Juan autorizó implementación integral con un solo agente. El reparto de abajo queda como propuesta de revisión/defensa del grupo. Sistema implementado en `distribucion/`; decisiones aceptadas en [implementacion.md](implementacion.md). Sin ramas, commits ni push en esta sesión.

# Plan de desarrollo — propuesta para el grupo

Basado en el reparto de `user-stories/README.md`: Juan, Oli y Nacho. Validar responsables y contratos antes de empezar. Una US = rama y PR; otro integrante revisa. Este plan no cambia las decisiones pendientes de la cátedra.

## Acuerdos previos — juntos

- Cerrar verificación de remitos con bultos mixtos, ingreso inicial/compras al CD, descuento/reserva al despachar y destino de rechazos.
- Definir enums, cantidades válidas, bajas de entidades referenciadas y reglas mínimas de devolución.
- Acordar una conexión y una transacción por operación de negocio: el servicio confirma o revierte; los DAO no hacen commits independientes.
- Mantener los nombres del dominio del diagrama; acordar firmas Python en snake_case.
- No agregar Strategy ni otros opcionales hasta completar el flujo obligatorio.

## Reparto por entregable

| Responsable | Entregable | Dependencia | Terminado cuando |
|---|---|---|---|
| Juan | Base compartida: estructura, conexión SQLite, creación del esquema inicial y arranque de unittest | Revisión de esquema con los tres | La base se crea desde cero y cada conexión activa FK; el mismo código permite base temporal para pruebas |
| Juan | US-01: sucursales y CD, modelo + DAO + servicio + pantalla | Base compartida | Alta, consulta, modificación y baja según regla acordada; distingue LOCAL/CD |
| Juan | US-02: categorías, productos, proveedores y precios | US-01/base | Rechaza código/CUIT duplicados y persiste relaciones y costos |
| Juan | US-03: stock por sucursal, mínimos y movimientos | US-01/02 | Ingresos/egresos dejan movimientos; rechaza stock insuficiente |
| Juan | US-04: Observer de stock bajo | US-03 y contrato de órdenes con Oli | Venta bajo mínimo avisa; consolida necesidad sin duplicar lo ya pedido |
| Oli | US-05: órdenes y detalles | Sucursales/productos | Valida CD → local y cantidades; consolida pendientes |
| Oli | US-06/07: bultos, remitos, State y despacho | US-05 y stock | No excede la orden; no despacha sin precinto; aplica descuento/reserva acordado al CD |
| Oli | US-08/09: recepción, verificación e historial | US-06/07 | Precinto roto no habilita stock; verificación no ingresa dos veces; historial inmutable |
| Nacho | US-10/11: ventas, cobros y comprobantes | Catálogo y contrato de stock | No sobrevende; cobros igualan total; comprobante único; operación atómica |
| Nacho | US-12: devoluciones | US-10/11 | Referencia venta; limita cantidades acumuladas; registra stock y reintegro juntos |
| Juan | Reporte de más vendidos y margen (US-14) | Ventas con precio/costo histórico | Filtra período, agrupa productos y calcula unidades y margen |
| Oli | Reporte de rechazos (US-15) | Recepción/historial | Filtra período y destino; distingue rechazo de merma según regla acordada |
| Nacho | Reporte de ventas e ingresos (US-13) | Ventas/cobros | Filtra período/local y agrupa por medio de pago sin duplicar totales |
| Oli, con revisión de Juan | Reporte de tránsito (US-16) | Historial de estados | Calcula duración despacho → recepción y promedio con filtros |

Cada responsable entrega su pantalla además del dominio y persistencia, si se confirma Tkinter. No dejar toda la UI para el final.

## Orden para avanzar sin bloquearse

1. **Base y contratos:** Juan prepara infraestructura; Oli define State y orden; Nacho define Venta y sus detalles. Oli/Nacho pueden avanzar objetos y tests aislados mientras se integra la base.
2. **Catálogo y stock:** integrar US-01/02/03; en paralelo desarrollar órdenes, estados y ventas usando los contratos acordados.
3. **Primer flujo completo:** orden → bulto → despacho → recepción → verificación → venta. Integrar Observer con órdenes reales.
4. **Completar:** devoluciones, cuatro reportes y pantallas pendientes.
5. **Entrega:** probar base vacía y datos de demostración, documentar ejecución y ensayar defensa de State, Observer y transacciones. Confirmar formato/fecha con la cátedra.

## Contratos que cruzan responsables

| Proveedor | Consumidor | Acuerdo necesario |
|---|---|---|
| Juan: catálogo | Oli y Nacho | Cómo cargar producto/sucursal y obtener precios/costos |
| Juan: stock | Oli y Nacho | Consultar vendible, ingresar verificado, egresar y registrar movimiento dentro de la misma transacción |
| Oli: reposición | Juan: Observer | Buscar/crear orden pendiente y consolidar faltante considerando lo ya solicitado |
| Oli: logística | Juan: inventario | Momento exacto y referencia única del ingreso/egreso para evitar duplicación |
| Nacho: ventas | Reportes | Precio y costo guardados al vender; cobros y devoluciones consultables |

## Pruebas de integración mínimas

- Un despacho y recepción correctos trasladan las cantidades esperadas, sin duplicarlas al reintentar verificar.
- Un precinto roto no aumenta el stock vendible.
- Una venta mayor al disponible no guarda venta, cobros ni movimientos parciales.
- Una falla de persistencia revierte la operación completa.
- Venta bajo mínimo notifica y consolida reposición sin pedidos duplicados.
- Devoluciones sucesivas no superan la cantidad originalmente vendida.
- Los cuatro reportes coinciden con un conjunto pequeño de datos calculado a mano.
