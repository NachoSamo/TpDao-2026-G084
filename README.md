# Andén · TP DAO 2026 · G084

Sistema de Centro de Distribución a Locales. Python 3.12+, SQLite con DAO propios, Tkinter/ttk y unittest. Sin paquetes externos ni secretos. State controla el ciclo del bulto; Observer genera reposiciones al caer bajo el mínimo.

## Ejecutar la web

Python **3.12 o superior**, sin paquetes externos, sin Node y sin Tkinter. Desde la carpeta del repositorio:

```bash
# Primera vez: demo visual con bultos en todas las etapas
python3 -m distribucion.demo_web --db demo-anden.db
# Arrancar la web
python3 main.py --web --db demo-anden.db --port 8080
```

Abrir **http://127.0.0.1:8080**. En Windows reemplazar `python3` por `py`. La carga de demo exige una base vacía y se hace una sola vez. Las siguientes veces ejecutar solo el servidor. Para comenzar con datos propios: `python3 main.py --web --db trabajo.db`. El puerto se puede cambiar con `--port 8081`. Detener con Ctrl+C.

La interfaz web se llama **Andén**: tablero de bultos por estado como inicio; reposición, inventario, catálogo, ventas y reportes en la navegación. Los formularios seleccionan entidades por nombre. Clic en un bulto abre su contenido e historial; su botón ofrece el siguiente paso permitido. No hay arrastre que saltee verificaciones. Los datos mostrados inicialmente son de demostración.

`Abrir TP.command` inicia el servidor web en macOS. Si el servidor ya está corriendo, abrir la URL directamente.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```

Los tests HTTP necesitan permiso para abrir puertos locales. Las pruebas E2E opcionales requieren Playwright y Chromium; ver `tests/smoke_web.py` para uso y salida de capturas.

## Interfaz de escritorio (alternativa)

Se conserva Tkinter para compatibilidad, pero la interfaz principal ahora es web:

```bash
python3 main.py --db demo.db --demo
# Después de cargar la demo una vez:
python3 main.py --db demo.db
```

Requiere Python con Tcl/Tk. `python3 -m tkinter` debe abrir una ventana. Para demo sin ninguna interfaz: `python3 main.py --db demo-terminal.db --demo --sin-ui`.

## Procesos disponibles

- **Tablero:** bultos por estado, búsqueda y destino; detalle con contenido e historial y próxima acción válida.
- **Reposición:** órdenes CD → local, remitos y preparación de bultos con reserva de stock.
- **Inventario:** existencias, reservas, mínimos, ingresos al CD, proveedores y avisos Observer.
- **Catálogo:** alta/modificación/baja lógica de productos, categorías, proveedores y sucursales, elegidos por nombre.
- **Ventas:** carrito multiproducto, cobros divididos, comprobante y devolución con reintegro.
- **Reportes:** ventas, margen, rechazos y tránsito; filtros y exportación CSV.

Importes con punto decimal, hasta dos decimales; cantidades enteras positivas. EFECTIVO, DEBITO, CREDITO y TRANSFERENCIA. Fechas guardadas en UTC; interfaz en hora local y filtros por fecha UTC. No hay cobros bancarios ni facturación fiscal real.

## Documentación del grupo

- [Cómo probar, decisiones y registros](docs/pruebas-y-decisiones.md).
- [Patrones, diagramas y código Mermaid](docs/patrones-de-diseno.md).
- [Defensa: consigna, flujo, patrones y persistencia](docs/defensa.md).
- [Persistencia local, GitHub y respaldos](docs/persistencia.md).
- [Registro de pruebas](docs/registro-pruebas.md).
- [Mensaje para el grupo](docs/mensaje-grupo.md).

## Estructura y defensa

| Archivo | Responsabilidad |
|---|---|
| `distribucion/modelos.py` | State polimórfico de bultos, sujeto Stock, Observer y validaciones puras |
| `distribucion/db.py` | Esquema, FK, triggers, DAO parametrizado y transacción |
| `distribucion/servicios.py` | Casos de uso y reglas que consultan datos |
| `distribucion/reportes.py` | Cuatro reportes con dinero Decimal y filtros |
| `distribucion/ui.py` | Formularios ttk, consultas y exportación CSV |
| `distribucion/demo.py` | Escenario reproducible con operaciones reales del servicio |
| `tests/test_sistema.py` | Reglas, integración, fallas y reportes |

La web local reutiliza los mismos servicios y DAO. `distribucion/web.py` sirve API y archivos de `distribucion/static/`; la conexión SQLite se abre y cierra por solicitud. No hay autenticación ni despliegue público: el servidor escucha solo en loopback.

Ver [decisiones y límites](docs/implementacion.md), [guion de defensa](docs/defensa.md) y [secuencias Mermaid](docs/diagramas/secuencias.md). Los diagramas HTML originales son antecedentes del modelo; la implementación ajusta nombres/estructura según las decisiones aceptadas.

Estado: implementación local; falta revisión del grupo y confirmar con cátedra la interpretación de remitos mixtos, interfaz y formato de entrega. No se publicó ni se hizo push.
