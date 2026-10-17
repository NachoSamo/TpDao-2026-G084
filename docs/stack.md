# Stack del proyecto

Regla: **todo lo que trae Python de fábrica, antes que una librería externa.** Si alguien quiere sumar una dependencia, se discute en el grupo y se agrega a esta tabla.

## Herramientas y versiones

| Qué | Herramienta | Versión | Notas |
|---|---|---|---|
| Lenguaje | Python | **3.12 o superior** | Aprobado por la cátedra. No usar features exclusivas de 3.13+ para que corra en las tres máquinas. |
| Base de datos | SQLite | 3.x (viene con Python) | Módulo estándar `sqlite3`, sin instalar nada. Un solo archivo `.db`. |
| Acceso a datos | `sqlite3` + clases DAO propias | — | **Sin ORM**: el material de la cátedra (guía "Objetos de Acceso" y "Material conceptual") solo usa `sqlite3` con conexión, cursor, `execute` con parámetros `?`, `commit`/`rollback`. Ver [Dudas #3](Dudas.md). |
| Validaciones | pydantic | 2.x | Valida los datos que entran a los servicios (tipos, obligatorios, rangos). Las RN-xx que necesitan consultar la base quedan en los servicios. Ver [Dudas #4](Dudas.md). |
| Interfaz | Tkinter + `ttk` | viene con Python | Propuesta: depende de [Dudas #1](Dudas.md). |
| Tests | `unittest` | viene con Python | La base de test es `:memory:`. |
| Gráficos de reportes | matplotlib | 3.9+ | Opcional: solo si un reporte lo necesita. |
| Control de versiones | Git + GitHub | — | Una rama por US (ver [user-stories](user-stories/README.md)). |
| Editor | VS Code + extensión Python | — | |
| Ver la base | DB Browser for SQLite | — | Para inspeccionar datos a mano. |

## Correspondencia de tipos

El diagrama de clases usa tipos estilo Java. Así se traducen:

| Diagrama | Python | SQLite |
|---|---|---|
| `Long` (id) | `int` | `INTEGER PRIMARY KEY` |
| `int` | `int` | `INTEGER` |
| `String` | `str` | `TEXT` |
| `boolean` | `bool` | `INTEGER` (0/1) |
| `BigDecimal` | `decimal.Decimal` | `TEXT` (nunca `float`: pierde centavos) |
| `LocalDate` / `LocalDateTime` | `datetime.date` / `datetime` | `TEXT` ISO-8601 (`2026-10-16`, `2026-10-16T21:30:00`) |
| enums (`TipoSucursal`, ...) | `enum.Enum` | `TEXT` + `CHECK (... IN (...))` |
| `List<X>` | `list[X]` | tabla hija con FK |
| interface / abstract | `abc.ABC` + `@abstractmethod` | no se persiste |

## Convenciones obligatorias

- **`PRAGMA foreign_keys = ON`** en cada conexión: SQLite las trae **desactivadas** por defecto y sin esto las FK no se validan.
- Montos: siempre `Decimal`, y en reportes SQL `ROUND(SUM(CAST(monto AS REAL)), 2)`.
- Estilo PEP 8: `snake_case` para funciones y variables, `PascalCase` para clases. Nombres en español, igual que el diagrama.
- Validaciones de negocio (RN-xx) en el modelo/servicios; la base agrega `UNIQUE`, `CHECK`, `FK` y triggers como segunda barrera.
s

## Comandos

```bash
py -m venv .venv
```

```bash
.venv/Scripts/python -m pip install "pydantic>=2,<3"
```

```bash
py main.py
```

```bash
py -m unittest discover tests
```

(`py` es el lanzador de Python en Windows; en Linux/Mac usar `python3`.)
