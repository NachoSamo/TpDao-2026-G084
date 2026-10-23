# Defensa del TP — Andén, Centro de Distribución a Locales

Guion para entender y explicar la aplicación. Leer primero [pruebas-y-decisiones.md](pruebas-y-decisiones.md) y recorrerla; no defender solo de memoria una pantalla.

## 1. Qué problema resuelve

Un comercio tiene un depósito central y varios locales de venta. Los locales piden reposición, el CD prepara y despacha bultos precintados, y cada local controla lo que recibe. El sistema conecta ese movimiento físico con el inventario, las ventas y sus cobros.

La regla que articula el TP es: **recibir físicamente una caja no equivale a poder vender su contenido**. La mercadería debe verificarse. Un precinto roto provoca rechazo logístico y no habilita stock vendible.

## 2. Qué pide la consigna y dónde se ve

Fuente original: [tema3.pdf](../tema3.pdf).

| Exigencia | Implementación y demostración |
|---|---|
| Administrar sucursales y CD | Catálogo → Sucursales, tipos CD/LOCAL, alta/modificación/baja lógica. |
| Productos, categorías, precios, mínimos y proveedores | Catálogo e Inventario; relación producto/proveedor con costo y principal. |
| Orden de reposición con origen/destino | Reposición; valida CD → local y detalles con cantidades positivas. |
| Bultos, remito y precinto | Reposición y tablero; contenido no excede lo solicitado ni las unidades libres del CD. |
| Despacho | Acción por remito; todos sus bultos deben estar precintados. |
| Recepción con control de precinto | Tablero; Recibido aún no habilita stock; verificar aprueba o rechaza. |
| Venta de varios productos, cobros, comprobante y devolución | Ventas; pagos divididos, total exacto, stock/reintegro y comprobante único. |
| Historial inmutable | Detalle del bulto y triggers de SQLite contra UPDATE/DELETE. |
| No sobreventa ni duplicados | Servicios + restricciones de base; pruebas con cantidades insuficientes, código/CUIT repetidos. |
| Al menos dos patrones | State y Observer, aplicados a reglas de negocio concretas. |
| Al menos cuatro reportes no triviales | Ventas/ingresos, más vendidos/margen, rechazos y tiempo de tránsito, con filtros y CSV. |

Las compras se cubren con ingreso mínimo de proveedor al CD: cantidades, costos y movimiento. No existe un ciclo completo de órdenes de compra/deuda. Promociones, lotes/vencimientos, clientes frecuentes y conciliación física quedaron fuera del alcance inicial. Strategy fue una propuesta opcional y no está implementado.

## 3. Preparación para mostrarla

En una base nueva, sin tocar trabajo previo:

```bash
python3 -m distribucion.demo_web --db defensa.db
python3 main.py --web --db defensa.db --port 8080
```

Abrir http://127.0.0.1:8080. En Windows usar `py`. Si `defensa.db` ya tiene registros, iniciar sin volver a cargar demo o elegir otro nombre. Tener a mano [modelos.py](../distribucion/modelos.py), [servicios.py](../distribucion/servicios.py), [db.py](../distribucion/db.py) y la salida de los tests.

## 4. Recorrido sugerido — 10 a 15 minutos

### A. Presentar el flujo y el tablero

> “El tablero sigue bultos desde Preparado hasta Verificado o Rechazado. Cada tarjeta muestra destino, remito y contenido; al abrirla se ve el historial. El próximo botón depende de su estado.”

Mostrar que no es un tablero de tareas libre: no se arrastran tarjetas para saltar controles. La API también valida las acciones; ocultar un botón no es la regla de seguridad del dominio.

### B. Reposición y reserva

Mostrar orden → remito → bulto. En la demo, BUL-003 contiene 12 arroces para Centro.

> “La orden expresa lo solicitado. El remito agrupa el despacho y el bulto identifica la unidad física precintada. Preparar un bulto reserva stock del CD, pero todavía no lo descuenta físicamente.”

En Inventario distinguir:

```text
Disponible para una nueva operación = cantidad − reservada
```

Esto evita apartar las mismas unidades para dos bultos. No se puede empaquetar más de lo solicitado en la orden, aunque haya stock de sobra.

### C. State y logística

Precintar BUL-003, despachar su remito, recibirlo con precinto íntegro y verificarlo.

> “Cada estado es un objeto con comportamiento. Bulto le delega la acción. Preparado sabe precintar, Precintado sabe despachar y Recibido decide verificación según el precinto. Las acciones no permitidas heredan un error.”

Mostrar que:

- Despachar descuenta stock CD y libera reserva juntos.
- Recibir no aumenta stock local.
- Verificar un bulto íntegro incorpora el contenido al local.
- Verificado/Rechazado son terminales: repetir no duplica movimientos.
- El historial registra anterior/nuevo, fecha y responsable.

Mostrar también el rechazo de la demo: no significa automáticamente pérdida o retorno. El remito mixto se identifica como parcialmente aceptado.

**Aclaración académica:** habilitar individualmente los bultos correctos es una decisión de implementación pendiente de validar contra la frase de la consigna que exige remito y contenedor verificados. No presentarla como una aprobación de la cátedra.

Diagrama y código Mermaid: [patrones-de-diseno.md](patrones-de-diseno.md#1-state-ciclo-de-vida-del-bulto).

### D. Venta y consistencia

En Centro, vender una yerba y un arroz después de verificar el arroz. Total $4350.50; dividir en efectivo $2500.50 y débito $1850.00.

> “Una venta guarda detalle con precio y costo del momento, cobros y comprobante; descuenta stock y evalúa mínimos. Todo pertenece a la misma transacción.”

Intentar otra venta con unidades excesivas o pagos incompletos. Mostrar el mensaje y que no aparece un comprobante parcial. El backend es la autoridad del precio y stock; el total que calcula JavaScript es una ayuda visual.

### E. Observer y reposición automática

Configurar un mínimo mayor al disponible de arroz en Centro. Mostrar aviso y orden nueva/consolidada.

> “Stock solo conoce una lista de observadores y les avisa cuando queda bajo mínimo. GeneradorReposicionAutomatica reacciona y le pide al servicio consolidar el faltante. Así se puede agregar otro observador sin cambiar el sujeto.”

Repetir control: puede crear otro aviso, pero no duplica unidades ya pedidas y pendientes. La notificación es síncrona, no un correo ni un evento en background. Si falla la venta después de avisar, también se revierten aviso y orden.

Diagrama y código Mermaid: [patrones-de-diseno.md](patrones-de-diseno.md#2-observer-stock-bajo-y-reposicion).

### F. Devolución

Devolver el arroz de esa venta como apto para reingreso.

> “No es un ingreso libre: debe referenciar una venta real y no superar lo vendido menos lo devuelto anteriormente. Se usa el precio histórico de la venta para el reintegro.”

Mostrar aumento de stock e importe reintegrado. Repetir la devolución para demostrar el límite acumulado. El reintegro se registra contablemente; no se mueve dinero real.

### G. Los cuatro reportes

1. **Ventas/ingresos:** agrupa cobros y reintegros por local/medio. Una venta dividida aparece en más de un medio; no sumar sus conteos como ventas únicas globales.
2. **Más vendidos/margen:** unidades netas, ingresos y margen con precio/costo histórico; una edición posterior del catálogo no cambia el pasado. Las devoluciones descuentan en su propio período.
3. **Rechazos:** bultos, unidades, motivo y destino. Merma “no determinada”, porque rechazo no prueba pérdida económica.
4. **Tránsito:** promedio y máximo del tiempo entre En tránsito y Recibido por destino. El filtro usa fecha de llegada, aunque el bulto después sea rechazado.

Mostrar filtros y exportación CSV. Estos reportes combinan tablas, agrupan o calculan; no son solo listados de ABM.

### H. Persistencia y transacciones

Mostrar `BaseDatos`, `DAO` y el decorador `atomico`.

> “SQLite persiste en un archivo; GitHub lleva el código y los generadores, no la base de cada integrante. Al arrancar se crea el esquema si falta. Reiniciar con el mismo archivo mantiene todos los registros.”

Explicar el recorrido:

```text
Navegador → API HTTP → Sistema → modelo/DAO → SQLite
```

- `web.py` recibe y valida tipos, sin definir reglas de negocio nuevas.
- `Sistema` coordina el caso de uso con `BEGIN IMMEDIATE`, commit o rollback.
- DAO usa consultas parametrizadas y no confirma transacciones por su cuenta.
- Cada conexión activa FK.
- Triggers bloquean editar/borrar historial y movimientos.
- Montos TEXT se convierten a Decimal. No se usa float para cálculos monetarios del backend.
- Estado se guarda como texto y se reconstruye con `ESTADOS`; los objetos Python no quedan serializados en la base.

Mostrar `test_falla_persistencia_revierte_venta_y_observer`: fuerza una falla tardía y prueba que no quedan venta, stock, aviso ni pedido a medias.

Más detalle: [persistencia.md](persistencia.md).

## 5. Preguntas probables y respuestas

**¿Por qué State y no un enum?** El enum identifica; State encapsula qué puede hacer cada estado y sus transiciones. Aquí hay clases concretas y delegación. El texto en SQLite solo permite reconstruirlas.

**¿Dónde está Observer si no hay una librería de eventos?** En `Stock.notificar`, el contrato `ObservadorStock.actualizar` y su implementación concreta. Observer no exige librerías ni asincronía.

**¿Son realmente dos patrones?** Sí, State y Observer. DAO es acceso a datos y arquitectura, no lo usamos para inflar el conteo. Strategy no está implementado.

**¿Hay DAO por entidad?** No. La implementación usa un DAO genérico y las consultas específicas viven en servicios/reportes. Si la cátedra pide uno por entidad, habría que refactorizar esa organización.

**¿Por qué SQLite?** Es suficiente para una demo académica local, incluye persistencia relacional, FK y transacciones sin instalar otro servicio. No implica que GitHub sincronice la base ni que la aplicación esté desplegada.

**¿Cómo se comparte la persistencia al clonar?** Se comparte el esquema y los scripts de demo. Cada integrante genera su propio archivo. Para registros compartidos en vivo hace falta un backend común; no está desplegado.

**¿Es seguro guardar montos como texto?** No se los trata como texto al calcular: pasan por Decimal y validación de escala. Así se conservan centavos sin la aproximación de float. Las sumas monetarias de reportes se hacen en Python con Decimal.

**¿Por qué no se puede cancelar un bulto?** No se implementó cancelación en el alcance inicial. Una reserva se libera despachando. Habría que definir transición, efecto sobre reserva e historial antes de agregarla.

**¿Qué demuestra el responsable del historial?** Lo ingresado manualmente; no identidad autenticada. Tampoco los triggers protegen contra un administrador que modifique el esquema.

**¿Qué pasa si hago doble clic en vender?** La pantalla deshabilita el botón mientras guarda. No hay clave de idempotencia de ventas: dos comandos nuevos válidos registran dos ventas. Los reintentos de transiciones terminales sí son rechazados por el dominio.

**¿Cuáles son las limitaciones?** Sin login/roles, facturación fiscal, pagos reales, cancelaciones, lotes/vencimientos ni despliegue público. Falta revisión del grupo y confirmar con la cátedra interfaz web, remitos mixtos, profundidad de compras y formato de entrega.

## 6. Qué revisar antes de entregar

- Repetir el recorrido con una base nueva y ejecutar los tests.
- Confirmar que los tres pueden explicar el código de State, Observer, el DAO y el rollback.
- Revisar los diagramas actuales contra el código, especialmente los HTML iniciales que son antecedentes.
- No afirmar que se implementaron los opcionales ni que ya está desplegada.
- Anotar respuestas de la cátedra y ajustar documentación, reglas y pruebas juntos.
