# Registro de pruebas — 23/10/2026

## Alcance verificado

Implementación local Andén, Python + SQLite + API HTTP + HTML/CSS/JS. Las verificaciones usaron bases de pruebas independientes: no se borró ni se reutilizó como fixture la base demo visible.

| Verificación | Resultado | Evidencia reproducible |
|---|---|---|
| Dominio/persistencia | 17 pruebas aprobadas | `python3 -m unittest tests.test_sistema -v` |
| API HTTP y archivos estáticos | 8 pruebas aprobadas | `python3 -m unittest tests.test_web -v` |
| Suite conjunta | **25/25 aprobadas** | `python3 -m unittest discover -s tests -v` |
| Navegador Chromium | **Recorrido E2E aprobado** | `python3 -m tests.smoke_web` con Playwright/Chromium instalados |
| JavaScript | Sintaxis válida | `node --check distribucion/static/app.js` — Node solo para este control, no para ejecutar la app |
| Python | Compilación sin errores | `python3 -m compileall -q distribucion main.py tests` |
| Parches Git | Sin errores de whitespace | `git diff --check` |

Suite de dominio probada durante esta sesión en Python 3.12 y 3.14; suite HTTP conjunta y recorrido final de navegador ejecutados en macOS con Python 3.14. No se probó Windows. La prueba Tkinter anterior verifica construcción de formularios, no sustituye las pruebas de la web actual.

## Qué cubre el E2E

- Seis secciones y ausencia de overflow horizontal del documento a 1440 px y 390 px. El tablero y las tablas sí tienen desplazamiento horizontal interno deliberado.
- Abrir detalle de bulto con nombre accesible e historial.
- Buscar un bulto y filtrar por destino.
- Alta/edición de categoría desde controles reales.
- Bulto 3: precintar → despachar remito → recibir → verificar.
- Configurar mínimo y ejecutar el flujo Observer.
- Venta de dos productos, dos medios de pago, comprobante y devolución de uno de los productos.
- Consultar los cuatro reportes con fechas y sucursal, descargar CSV.
- Sin errores JavaScript/CSP ni recursos fallidos en el recorrido final.

Capturas del tablero: [desktop](../.impeccable/review/desktop.png) y [móvil](../.impeccable/review/mobile.png).

## Correcciones encontradas durante las pruebas

1. Un control llamado `id` ocultaba la propiedad `form.id`, por lo que el listener no interceptaba algunos formularios de logística. Se usa `matches('#action-form')` y se verificó el ciclo completo después del cambio.
2. Se asignaron nombres accesibles explícitos a selectores para que el lector de pantalla/test encuentre el label sin incorporar las opciones.
3. Se agregó ícono local embebido para evitar el recurso `/favicon.ico` inexistente en consola.
4. La revisión visual pidió separar el botón de detalle del de transición, dar foco visible al buscador, mantener el aviso de demo en móvil y aumentar contraste del texto secundario. Se aplicaron esos cambios y se recapturaron ambas vistas.

El detector visual de Impeccable funcionó en modo regex degradado: no verificó contraste computed y su salida vacía **no equivale a una auditoría de accesibilidad completa**. La revisión visual inicial fue externa al hilo de implementación; la comprobación final de los cambios/capturas la realizó el agente principal porque los agentes auxiliares dejaron de estar disponibles por límite de uso. No se atribuye una aprobación final independiente inexistente.

## Qué no queda demostrado por estas pruebas

- Compatibilidad probada en Windows, Safari o Firefox.
- Conformidad integral WCAG ni prueba manual completa con lector de pantalla.
- Aceptación académica de remitos parcialmente aceptados, interfaz o alcance de compras.
- Uso productivo, autenticación, facturación fiscal o integración bancaria.
- Corrección de cualquier modificación futura sin volver a ejecutar el recorrido relevante.

Este registro informa el resultado observado; no convierte la implementación en una entrega académica ya aprobada.
