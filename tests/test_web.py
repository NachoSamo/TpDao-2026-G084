"""Integración HTTP sobre archivo SQLite aislado y puerto efímero local."""
import concurrent.futures
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from distribucion.db import BaseDatos
from distribucion.demo import cargar
from distribucion.servicios import Sistema
from distribucion.web import ServidorLocal


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ruta = str(Path(self.temp.name) / 'prueba.db')
        base = BaseDatos(self.ruta)
        cargar(Sistema(base))
        base.cerrar()
        self.static = Path(self.temp.name) / 'static'
        self.static.mkdir()
        (self.static / 'index.html').write_text('<h1>TP DAO</h1>')
        (self.static / 'app.js').write_text('console.log("ok")')
        (self.static / 'styles.css').write_text('body { color: black }')
        (self.static / 'fonts').mkdir()
        (self.static / 'fonts' / 'test.woff2').write_bytes(b'font')
        self.servidor = ServidorLocal(self.ruta, 0, self.static)
        self.puerto = self.servidor.server_address[1]
        self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, metodo, ruta, datos=None, headers=None, raw=None):
        conexion = http.client.HTTPConnection('127.0.0.1', self.puerto, timeout=5)
        cabeceras = {'Content-Type': 'application/json'}
        cabeceras.update(headers or {})
        cuerpo = raw if raw is not None else json.dumps(datos) if datos is not None else None
        conexion.request(metodo, ruta, body=cuerpo, headers=cabeceras)
        respuesta = conexion.getresponse()
        contenido = respuesta.read()
        resultado = json.loads(contenido) if respuesta.getheader('Content-Type', '').startswith('application/json') else contenido
        salida = respuesta.status, dict(respuesta.getheaders()), resultado
        conexion.close()
        return salida

    def accion(self, accion, **datos):
        return self.request('POST', '/api/acciones', {'accion': accion, **datos})

    def test_datos_reportes_y_exportacion(self):
        estado, _, datos = self.request('GET', '/api/datos')
        self.assertEqual(estado, 200)
        self.assertEqual(datos['stock'][1]['cantidad'], 13)
        self.assertEqual(datos['remito'][0]['estado'], 'PARCIALMENTE_ACEPTADO')
        for tipo in ('ventas', 'margen', 'rechazos', 'transito'):
            estado, _, filas = self.request('GET', f'/api/reportes?tipo={tipo}&desde=2000-01-01&hasta=2100-12-31&sucursal=2&top=10')
            self.assertEqual(estado, 200)
            self.assertTrue(filas)
        estado, headers, csv = self.request('GET', '/api/reportes.csv?tipo=margen')
        self.assertEqual(estado, 200)
        self.assertIn('attachment;', headers['Content-Disposition'])
        self.assertIn(b'1800.50', csv)
        self.assertEqual(self.request('GET', '/api/reportes?desde=mal')[0], 400)
        self.assertEqual(self.request('GET', '/api/reportes?tipo=ventas&tipo=margen')[0], 400)

    def test_venta_devolucion_y_validaciones_estrictas(self):
        estado, _, salida = self.accion('vender', sucursal=2, items=[{'producto': 1, 'cantidad': 2}], pagos=[{'medio': 'EFECTIVO', 'monto': '5001.00'}])
        self.assertEqual(estado, 200)
        venta = salida['resultado']
        self.assertEqual(self.accion('devolver', venta=venta, producto=1, unidades=2, apto=True, medio='EFECTIVO')[0], 200)
        self.assertEqual(self.accion('devolver', venta=venta, producto=1, unidades=1, apto=True, medio='EFECTIVO')[0], 400)
        for falso_id in (True, '2', 2.0):
            self.assertEqual(self.accion('definir_minimo', sucursal=falso_id, producto=1, minimo=10)[0], 400)
        self.assertEqual(self.accion('recibir', id=1, integro='si', responsable='Test')[0], 400)
        self.assertEqual(self.accion('vender', sucursal=2, items=[{'producto': 1, 'cantidad': 1}, {'producto': 1, 'cantidad': 1}], pagos=[{'medio': 'EFECTIVO', 'monto': '5001.00'}])[0], 400)
        self.assertEqual(self.accion('vender', sucursal=2, items=[{'producto': 1, 'cantidad': 1}], pagos=[{'medio': 'EFECTIVO', 'monto': '2500.50'}, {'medio': 'EFECTIVO', 'monto': '2500.50'}])[0], 400)
        self.assertEqual(self.accion('vender', sucursal=2, items=[{'producto': 1, 'cantidad': 1}], pagos=[{'medio': 'EFECTIVO', 'monto': 2500.50}])[0], 400)
        self.assertEqual(self.accion('desconocida')[0], 400)

    def test_catalogo_y_conflictos(self):
        self.assertEqual(self.accion('guardar', tabla='categoria', datos={'nombre': 'Nueva'})[0], 200)
        self.assertEqual(self.accion('guardar', tabla='categoria', datos={'nombre': 'Nueva'})[0], 409)
        self.assertEqual(self.accion('guardar', tabla='categoria', id=2, datos={'nombre': 'Editada'})[0], 200)
        self.assertEqual(self.accion('baja', tabla='categoria', id=2)[0], 200)
        self.assertEqual(self.accion('asociar_proveedor', producto_id=1, proveedor_id=1, costo='1600.25', principal=True)[0], 200)
        self.assertEqual(self.accion('ingresar_proveedor', sucursal=1, producto=1, proveedor=1, unidades=5, costo='1600.25')[0], 200)

    def test_logistica_completa_por_api(self):
        def ok(accion, **datos):
            estado, _, resultado = self.accion(accion, **datos)
            self.assertEqual(estado, 200, resultado)
            return resultado['resultado']
        orden = ok('crear_orden', origen=1, destino=2, items=[{'producto': 1, 'cantidad': 2}])
        remito = ok('crear_remito', orden=orden)
        bulto = ok('preparar_bulto', remito=remito, items=[{'producto': 1, 'cantidad': 2}], responsable='Test')
        ok('precintar', id=bulto, codigo='WEB-1', responsable='Test')
        ok('despachar', remito=remito, responsable='Test')
        ok('recibir', id=bulto, integro=True, responsable='Test')
        ok('verificar', id=bulto, responsable='Test', motivo='')
        self.assertEqual(self.accion('verificar', id=bulto, responsable='Test')[0], 400)

    def test_static_sin_traversal_ni_archivos_privados(self):
        for ruta in ('/', '/index.html', '/app.js', '/styles.css', '/fonts/test.woff2'):
            estado, headers, _ = self.request('GET', ruta)
            self.assertEqual(estado, 200)
            self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        for ruta in ('/../prueba.db', '/%2e%2e/prueba.db', '/fonts/../../prueba.db', '/main.py', '/prueba.db', '/fonts/../index.html'):
            self.assertEqual(self.request('GET', ruta)[0], 404)

    def test_host_origen_payload_y_json(self):
        self.assertEqual(self.request('GET', '/api/datos', headers={'Host': 'externo.example'})[0], 403)
        self.assertEqual(self.request('GET', '/api/datos', headers={'Origin': 'https://externo.example'})[0], 403)
        accion = {'accion': 'crear_remito', 'orden': 1}
        self.assertEqual(self.request('POST', '/api/acciones', accion, {'Origin': 'https://externo.example'})[0], 403)
        self.assertEqual(self.request('POST', '/api/acciones', accion, {'Sec-Fetch-Site': 'cross-site'})[0], 403)
        self.assertEqual(self.request('POST', '/api/acciones', accion, {'Origin': f'http://127.0.0.1:{self.puerto}', 'Sec-Fetch-Site': 'same-origin'})[0], 200)
        self.assertEqual(self.request('POST', '/api/acciones', accion, {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('POST', '/api/acciones', raw='x' * 65537)[0], 413)
        self.assertEqual(self.request('POST', '/api/acciones', raw='{mal')[0], 400)
        self.assertEqual(self.request('POST', '/api/acciones', raw='[]')[0], 400)

    def test_concurrencia_usa_conexiones_independientes(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            estados = list(pool.map(lambda n: self.accion('guardar', tabla='categoria', datos={'nombre': f'Concurrente {n}'})[0], range(8)))
        self.assertEqual(estados, [200] * 8)
        datos = self.request('GET', '/api/datos')[2]
        self.assertEqual(len(datos['categoria']), 9)

    def test_csv_evitar_formulas(self):
        self.accion('guardar', tabla='producto', id=1, datos={'codigo': 'YER-01', 'nombre': '=HYPERLINK("mal")', 'categoria_id': 1, 'precio': '2500.50', 'costo': '1600.25'})
        contenido = self.request('GET', '/api/reportes.csv?tipo=margen')[2].decode('utf-8-sig')
        self.assertIn("'=HYPERLINK", contenido)

if __name__ == '__main__':
    unittest.main()
