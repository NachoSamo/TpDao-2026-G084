# Dudas para la cátedra

Cómo usarlo: cualquiera agrega una fila apenas aparece la duda. La columna **Si no responden** es lo que hacemos por defecto para no frenarnos. Cuando el profe responde, se completa **Respuesta** y se pasa a "Respondidas" (si cambia una regla, se actualiza también [negocio.md](conocimiento/negocio.md)).

## Abiertas

| # | Pregunta | Por qué importa | Si no responden | Quién |
|---|---|---|---|---|
| 1 | ¿Hay que entregar frontend + backend + base de datos, o alcanza con una app de escritorio que acceda a la base? | Define si hacemos UI Tkinter o una API + front web. Cambia la arquitectura entera. | App de escritorio Tkinter con capas modelo / servicios / DAO / UI. | Nacho |
| 2 | ¿Es obligatorio implementar algún proceso de negocio opcional? ¿Suma nota? | Los opcionales (promociones, lotes, inventario físico...) cuestan tiempo. | Solo los 7 obligatorios. El Strategy de precios ya cubre parte de "promociones". | Nacho |
| 3 | ¿Se puede usar un ORM (SQLAlchemy, Peewee) o hay que usar `sqlite3` directo como en el material? | El material de la cátedra solo muestra `sqlite3` + cursor. | `sqlite3` directo con clases DAO. | Nacho |
| 4 | ¿Se permiten librerías externas como pydantic para validar? | Usamos pydantic para las validaciones del backend. | Usar pydantic. | Nacho |
| 5 | ¿Qué cuenta como reporte "no trivial"? ¿Tiene que tener gráfico, filtros, exportación? | Hay que implementar mínimo 4. | Consultas con JOIN + agrupación + filtros por fecha/sucursal, en tabla. | |
| 6 | ¿Qué reglas de devolución esperan? (plazo máximo, estado del producto, medio de reintegro) | La consigna dice "reglas establecidas" pero no las define (RN-06). | Solo validar venta existente y cantidad devolvible. | |
| 7 | ¿Cómo es la entrega? (repositorio, informe, defensa oral, fecha) | Para planificar. | — | |

## Respondidas

| # | Pregunta | Respuesta | Fecha |
|---|---|---|---|
