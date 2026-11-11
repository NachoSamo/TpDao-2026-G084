# Cómo probar, decisiones y registros

Esta guía describe la implementación de la rama `rama-juani`. Es una base funcional para revisar entre los tres, no una aprobación de la cátedra de los supuestos adoptados.

## 1. Clonar y arrancar

Requiere Git y Python **3.12 o superior**. La app web usa solo la biblioteca estándar: no requiere npm, pip, Tkinter ni un servidor de base separado.

```bash
git clone --branch rama-juani https://github.com/NachoSamo/TpDao-2026-G084.git
cd TpDao-2026-G084
python3 --version
python3 -m distribucion.demo_web --db demo-anden.db
python3 main.py --web --db demo-anden.db --port 8080
```

En **Windows**, usar `py` en lugar de `python3`. Abrir **http://127.0.0.1:8080**. En macOS también se puede abrir `Abrir TP.command` con doble clic.

La demo se carga **una sola vez en una base vacía**. Las siguientes veces ejecutar únicamente:

```bash
python3 main.py --web --db demo-anden.db --port 8080
```

Si el puerto está ocupado, usar `--port 8081` y abrir http://127.0.0.1:8081. Ctrl+C detiene el servidor; cerrar el navegador no borra datos ni detiene el proceso. Si ya tienen el repo: `git fetch origin` y `git switch --track origin/rama-juani` la primera vez; después `git switch rama-juani`.

## 2. Qué trae la demo

`distribucion/demo_web.py` ejecuta casos de uso reales, no inserta stock local arbitrariamente:

- Un CD Córdoba y tres locales: Centro, Nueva Córdoba y General Paz.
- Cuatro productos: yerba, arroz, aceite y fideos; categoría y proveedor de demostración.
- Diez bultos distribuidos entre los seis estados del tablero.
- Un remito mixto con bulto verificado y rechazado, venta con dos medios, devolución y reposición automática.
- Stock y movimientos que permiten probar el circuito desde el CD hasta el local.

La demo es sintética. Los IDs siguientes valen solo en la base recién generada; en una base usada pueden diferir. No volver a cargarla sobre trabajo existente: elegir otro archivo con `--db`.

## 3. Recorrido manual reproducible

### Logística y State

1. En **Tablero de bultos**, abrir BUL-003. Contiene 12 unidades de arroz, va al local Centro y comienza Preparado.
2. **Inventario:** antes del despacho esas 12 unidades están reservadas en el CD; aún no existen como vendibles en Centro.
3. Precintar con un código nuevo, por ejemplo `PRUEBA-003`, y responsable.
4. Despachar su remito. El bulto pasa a En tránsito; se descuenta existencia y se libera reserva del CD en la misma operación.
5. Registrar llegada con precinto íntegro. Pasa a Recibido: el stock del local todavía no aumenta.
6. Verificar. Pasa a Verificado y Centro incorpora 12 unidades disponibles de arroz, con movimiento e historial.
7. Ya no aparece una acción para volver a verificar. La API también rechaza el reintento: la protección está en el servidor, no solo en el botón.

Para el camino de rechazo, usar otro bulto en tránsito: recibir con precinto roto y luego verificar con motivo obligatorio. Debe terminar Rechazado y no aumentar el stock local. No se considera automáticamente una merma económica.

### Ventas, cobros y devoluciones

Después del recorrido anterior:

1. En **Ventas → Nueva venta**, elegir Centro.
2. Agregar 1 yerba ($2500.50) y 1 arroz ($1850.00): total **$4350.50**.
3. Cobrar $2500.50 en efectivo y $1850.00 con débito. Se genera comprobante `V-XXXXXXXX`, baja stock y registra movimientos.
4. Probar cobros que no sumen el total o vender una cantidad superior al stock: debe aparecer error y no guardarse una venta parcial.
5. Registrar devolución de 1 arroz de esa venta, apto para reingreso y medio de reintegro elegido. Deben volver 1 unidad al stock y registrarse $1850.00 de reintegro.
6. Intentar devolver nuevamente ese arroz: se rechaza porque ya se devolvió todo lo vendido de ese producto en esa venta.

### Observer

1. En **Inventario**, configurar mínimo 15 para arroz en Centro después de recibir las 12 unidades.
2. Aparece aviso y se pide el faltante en una orden hacia el CD.
3. Repetir la configuración no duplica las unidades pendientes. Puede registrar otro aviso porque hubo otro evento de control.
4. Vender una unidad puede incrementar la necesidad, descontando siempre lo que ya está solicitado y pendiente.

### Catálogo y reportes

- Crear y editar una categoría, un proveedor, un producto y una sucursal. Los selectores muestran nombres; los IDs son internos.
- Repetir un código de producto o CUIT de proveedor: se rechaza por unicidad.
- Dar de baja: la entidad queda inactiva y conserva historial; no es un borrado físico.
- Consultar **los cuatro reportes**, con período amplio y local Centro; exportar CSV. El reporte vacío es válido si el filtro no tiene operaciones.
- Reiniciar el servidor usando el mismo `--db`: los registros deben seguir ahí.

## 4. Pruebas automáticas

```bash
python3 -m unittest discover -s tests -v
```

Se incluyen 25 pruebas: 17 de dominio/persistencia y 8 HTTP. Usan bases temporales o `:memory:` y no alteran la demo ni la base de trabajo. Las pruebas HTTP abren puertos locales temporales.

Cubren reservas, sobreventa, precintos, remitos mixtos, reintentos, devoluciones acumuladas, precio/costo histórico, Observer y pendientes, FK, triggers de auditoría, rollback tardío, reportes/CSV, validación JSON y escrituras concurrentes.

### Prueba de navegador opcional

La app no tiene dependencias externas, pero la prueba E2E sí usa Playwright. Instalarlo en un entorno virtual aislado:

```bash
python3 -m venv .venv
# macOS/Linux:
.venv/bin/python -m pip install playwright
.venv/bin/python -m playwright install chromium
.venv/bin/python -m tests.smoke_web
```

En Windows, reemplazar `.venv/bin/python` por `.venv\Scripts\python.exe`. `tests/smoke_web.py` crea su propio servidor y base temporal, prueba las seis secciones, formularios, circuito State, Observer, venta con dos productos/pagos, devolución y los cuatro reportes con descarga CSV. Guarda capturas en `.impeccable/review/`. No modifica la base visible del grupo.

### Registro de verificación

Ver [registro-pruebas.md](registro-pruebas.md) para el resultado y los límites observados de esta entrega. Una prueba automatizada no sustituye recorrer la aplicación ni ensayar la defensa.

## 5. Por qué se tomaron estas decisiones

| Decisión | Motivo y consecuencia |
|---|---|
| Python + SQLite + DAO propios | Sigue el enfoque académico existente, funciona sin instalar servidor y permite ver SQL, relaciones y transacciones. No hay ORM. |
| Web local en lugar de depender de Tkinter | Se abre con URL y permite una interfaz más clara. HTML/CSS/JS livianos sin build; los servicios Python siguen validando todo. Tkinter se conserva como alternativa. |
| State + Observer | Dos patrones aplicados a reglas concretas: transiciones logísticas y reposición por stock bajo. Strategy queda opcional y **no está implementado**. |
| `cantidad` y `reservada` separadas | Preparar no significa despachar. Se evita comprometer dos veces las mismas unidades. |
| Bulto verificado habilita su propio contenido | Permite recepción parcial sin bloquear bultos correctos por otro rechazado. **Debe validarse con cátedra**: la consigna menciona remito y contenedor verificados. |
| Rechazo separado de merma/retorno | Un precinto roto no demuestra por sí solo pérdida física o regreso al CD. Se conserva el registro sin inventar una operación. |
| Baja lógica | No rompe referencias de ventas, movimientos e historial. |
| `Decimal` y montos TEXT | Evita errores binarios de float; los reportes agregan con Decimal. Precio y costo se guardan en cada detalle de venta. |
| Una transacción por comando | Venta, stock, cobros y reposición generada se confirman juntos o se revierten. DAO no confirma por su cuenta. |
| Historial y movimientos inmutables | Triggers bloquean modificaciones/borrados normales y preservan trazabilidad. No es una defensa contra un administrador del archivo. |
| Sin login ni pagos reales | El alcance es demostrar el TP localmente; responsable manual y cobros contables, sin integraciones bancarias/fiscales. |

Más detalle y límites: [implementacion.md](implementacion.md).

## 6. Qué significa “registros” en esta app

Los registros de negocio están en SQLite, no en la consola ni en el historial de Git:

| Tabla | Registra |
|---|---|
| `historial` | Cada cambio de estado: bulto, fecha UTC, estado anterior/nuevo y responsable. |
| `movimiento` | Cada entrada/salida: sucursal, producto, cantidad con signo, tipo y referencia de origen. |
| `ingreso` | Compra mínima a proveedor, cantidad y costo unitario. |
| `orden`, `detalle_orden` | Qué se pidió, de dónde y para qué local. |
| `remito`, `bulto`, `detalle_bulto` | Agrupación logística, precinto, resultado y contenido. |
| `venta`, `detalle_venta`, `cobro` | Comprobante, productos, precios/costos históricos y medios/importes cobrados. |
| `devolucion` | Venta/producto de origen, cantidad, importe reintegrado, medio y fecha. |
| `aviso` | Eventos en que Observer detectó faltante. No es una orden nueva por cada aviso. |

Las fechas se guardan en UTC y la interfaz las presenta en hora local. Los filtros de reportes usan fecha UTC. No se incluyó un sistema de logs de producción ni usuarios autenticados.

## 7. Persistencia y GitHub

Ver [persistencia.md](persistencia.md): se sube el esquema y los generadores, **no las bases `.db`**. Cada integrante genera su base; reiniciar no borra datos. GitHub aloja el código, no ejecuta este backend ni sincroniza los registros de los tres.
