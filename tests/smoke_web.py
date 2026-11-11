"""E2E Playwright aislado. Requiere playwright y Chromium instalados.

python3 -m tests.smoke_web
PLAYWRIGHT_CHROMIUM_EXECUTABLE permite elegir un Chromium ya instalado.
No modifica las bases demo: crea archivo temporal y puerto efímero propios.
"""
import os
from pathlib import Path
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect

from distribucion.db import BaseDatos
from distribucion.demo_web import cargar_tablero
from distribucion.servicios import Sistema
from distribucion.web import ServidorLocal

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.impeccable' / 'review'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dao-e2e-') as temporal:
        ruta = str(Path(temporal) / 'e2e.db')
        base = BaseDatos(ruta)
        cargar_tablero(Sistema(base))
        base.cerrar()
        servidor = ServidorLocal(ruta, 0)
        thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{servidor.server_address[1]}'
        try:
            probar(url)
        finally:
            servidor.shutdown()
            servidor.server_close()
            thread.join()


def probar(url):
    errores = []
    with sync_playwright() as playwright:
        opciones = {'headless': True}
        if os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE'):
            opciones['executable_path'] = os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE']
        navegador = playwright.chromium.launch(**opciones)
        try:
            page = navegador.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
            page.on('pageerror', lambda error: errores.append(str(error)))
            page.on('console', lambda mensaje: errores.append(mensaje.text) if mensaje.type == 'error' else None)
            page.goto(url)
            page.wait_for_load_state('networkidle')
            expect(page.get_by_role('heading', name='Todo en movimiento.')).to_be_visible()
            expect(page.get_by_role('button', name='Ver bulto 3', exact=True)).to_be_visible()
            page.screenshot(path=str(OUTPUT / 'desktop.png'), full_page=True)
            sin_overflow(page)
            page.get_by_role('button', name='Ver bulto 3', exact=True).click()
            expect(page.get_by_role('dialog', name='Bulto BUL-003')).to_be_visible()
            expect(page.get_by_role('heading', name='Recorrido del bulto')).to_be_visible()
            page.get_by_role('button', name='Cerrar', exact=True).click()
            page.get_by_role('textbox', name='Buscar bulto', exact=True).fill('BUL-003')
            expect(page.locator('.parcel')).to_have_count(1)
            page.get_by_role('textbox', name='Buscar bulto', exact=True).fill('')
            page.get_by_role('combobox', name='Filtrar por destino').select_option('3')
            assert page.locator('.parcel').count() > 0
            page.get_by_role('combobox', name='Filtrar por destino').select_option('')

            movil = navegador.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
            movil.on('pageerror', lambda error: errores.append(str(error)))
            movil.on('console', lambda mensaje: errores.append(mensaje.text) if mensaje.type == 'error' else None)
            movil.goto(url)
            movil.wait_for_load_state('networkidle')
            expect(movil.get_by_role('heading', name='Todo en movimiento.')).to_be_visible()
            sin_overflow(movil)
            movil.screenshot(path=str(OUTPUT / 'mobile.png'), full_page=True)
            movil.close()

            for ruta in ('reposicion', 'inventario', 'catalogo', 'ventas', 'reportes', 'tablero'):
                navegar(page, ruta)
                sin_overflow(page)

            # Catálogo: alta y edición usando los controles reales.
            navegar(page, 'catalogo')
            page.locator('[data-action="catalog-tab"][data-table="categoria"]').click()
            page.locator('[data-action="edit"][data-table="categoria"]').first.click()
            expect(page.get_by_role('dialog', name='Agregar categoría')).to_be_visible()
            page.get_by_label('Nombre', exact=True).fill('Categoría E2E')
            confirmar(page)
            fila = page.get_by_role('row').filter(has_text='Categoría E2E')
            fila.locator('[data-action="edit"]').click()
            page.get_by_label('Nombre', exact=True).fill('Categoría editada E2E')
            confirmar(page)
            expect(page.get_by_role('row').filter(has_text='Categoría editada E2E')).to_be_visible()

            # Completar el siguiente recorrido real del bulto 3 (arroz, local Centro).
            navegar(page, 'tablero')
            transicion(page, 3)
            page.get_by_label('Código de precinto', exact=True).fill('E2E-PREC-003')
            confirmar(page)
            transicion(page, 3)
            confirmar(page)
            transicion(page, 3)
            page.get_by_label('Condición del precinto').select_option('true')
            confirmar(page)
            transicion(page, 3)
            confirmar(page)
            datos = page.request.get(url + '/api/datos').json()
            assert next(b for b in datos['bulto'] if b['id'] == 3)['estado'] == 'VERIFICADO'

            # Mínimo + Observer.
            navegar(page, 'inventario')
            page.get_by_role('button', name='Configurar mínimo', exact=True).click()
            page.get_by_label('Sucursal', exact=True).select_option('2')
            page.get_by_label('Producto', exact=True).select_option('2')
            page.get_by_label('Stock mínimo', exact=True).fill('15')
            confirmar(page)

            # Venta con dos productos disponibles y dos medios de pago.
            navegar(page, 'ventas')
            page.get_by_role('button', name='Nueva venta', exact=True).click()
            expect(page.get_by_role('dialog', name='Nueva venta')).to_be_visible()
            page.get_by_label('Local de venta', exact=True).select_option('2')
            filas = page.locator('[data-list="items"] .item-row')
            filas.nth(0).locator('[name="producto"]').select_option('1')
            filas.nth(0).locator('[name="cantidad"]').fill('1')
            page.get_by_role('button', name='+ Agregar otro producto', exact=True).click()
            filas.nth(1).locator('[name="producto"]').select_option('2')
            filas.nth(1).locator('[name="cantidad"]').fill('1')
            cobros = page.locator('[data-list="pagos"] .item-row')
            cobros.nth(0).locator('[name="medio"]').select_option('EFECTIVO')
            cobros.nth(0).locator('[name="monto"]').fill('2500.50')
            page.get_by_role('button', name='+ Agregar otro medio de pago', exact=True).click()
            cobros.nth(1).locator('[name="medio"]').select_option('DEBITO')
            cobros.nth(1).locator('[name="monto"]').fill('1850.00')
            venta = confirmar(page)['resultado']
            expect(page.get_by_role('row').filter(has_text=f'V-{venta:08d}').first).to_be_visible()

            page.get_by_role('button', name='Registrar devolución', exact=True).click()
            page.get_by_label('Comprobante', exact=True).select_option(str(venta))
            page.get_by_label('Producto vendido', exact=True).select_option('2')
            page.get_by_label('Cantidad', exact=True).fill('1')
            page.get_by_label('Medio de reintegro', exact=True).select_option('EFECTIVO')
            page.get_by_role('checkbox').check()
            confirmar(page)

            # Reportes, filtros inclusivos y descarga CSV.
            navegar(page, 'reportes')
            for tipo in ('ventas', 'margen', 'rechazos', 'transito'):
                page.locator(f'[data-action="report-tab"][data-type="{tipo}"]').click()
                page.get_by_label('Desde', exact=True).fill('2000-01-01')
                page.get_by_label('Hasta', exact=True).fill('2100-12-31')
                page.get_by_label('Sucursal', exact=True).select_option('2')
                with page.expect_response(lambda r: '/api/reportes?' in r.url):
                    page.get_by_role('button', name='Consultar', exact=True).click()
                expect(page.locator('#report-result table')).to_be_visible()
                with page.expect_download() as descarga:
                    page.get_by_role('button', name='CSV', exact=True).click()
                archivo = descarga.value
                assert archivo.suggested_filename == 'reporte.csv'
                assert archivo.failure() is None
            assert not errores, errores
            print('E2E OK: 6 rutas, catálogo alta/edición, ciclo State, Observer, venta 2 productos/2 pagos, devolución, 4 reportes/CSV, búsqueda/filtros, diálogos accesibles, desktop/móvil sin overflow ni errores JS/CSP.')
            print(f'Capturas: {OUTPUT / "desktop.png"}, {OUTPUT / "mobile.png"}')
        except Exception:
            page.screenshot(path=str(OUTPUT / 'failure.png'), full_page=True)
            print('Diálogo al fallar:', page.locator('#dialog-content').inner_text())
            raise
        finally:
            navegador.close()


def navegar(page, ruta):
    page.locator(f'#nav a[href="#{ruta}"]').click()
    expect(page.locator(f'#nav a[href="#{ruta}"]')).to_have_attribute('aria-current', 'page')


def sin_overflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Overflow horizontal del documento'


def transicion(page, bulto):
    page.locator('.parcel').filter(has=page.get_by_role('button', name=f'Ver bulto {bulto}', exact=True)).locator('[data-action="transition"]').click()
    expect(page.get_by_role('dialog')).to_be_visible()


def confirmar(page):
    invalidos = page.locator('#action-form :invalid').evaluate_all('(els) => els.map(e => ({name:e.name, value:e.value, message:e.validationMessage}))')
    assert not invalidos, invalidos
    with page.expect_response(lambda r: r.request.method == 'POST' and '/api/acciones' in r.url) as respuesta:
        page.locator('#action-form [type="submit"]').click()
    resultado = respuesta.value.json()
    assert resultado.get('ok'), resultado
    expect(page.get_by_role('dialog')).not_to_be_visible()
    page.wait_for_load_state('networkidle')
    return resultado


if __name__ == '__main__':
    main()
