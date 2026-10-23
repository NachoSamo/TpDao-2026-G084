"""Servidor HTTP local: API de casos de uso y archivos estáticos explícitos."""
import csv
import io
import json
import mimetypes
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from .db import BaseDatos
from .reportes import Reportes
from .servicios import Sistema

TABLAS = ('sucursal', 'categoria', 'proveedor', 'producto',
          'producto_proveedor', 'stock', 'movimiento', 'ingreso', 'orden',
          'detalle_orden', 'remito', 'bulto', 'detalle_bulto', 'historial',
          'venta', 'detalle_venta', 'cobro', 'devolucion', 'aviso')
MAX_PAYLOAD = 65536
STATIC = Path(__file__).parent / 'static'


def entero(valor):
    if type(valor) is not int or valor < 1:
        raise ValueError('El ID o la cantidad debe ser un entero positivo')
    return valor


def booleano(valor):
    if type(valor) is not bool:
        raise ValueError('El valor debe ser booleano')
    return valor


def texto(valor):
    if not isinstance(valor, str):
        raise ValueError('Se esperaba texto')
    return valor


def convertir_items(filas):
    if not isinstance(filas, list) or not filas:
        raise ValueError('Los ítems deben ser una lista no vacía')
    resultado = {}
    for fila in filas:
        if not isinstance(fila, dict) or set(fila) != {'producto', 'cantidad'}:
            raise ValueError('Cada ítem requiere producto y cantidad')
        producto, unidades = entero(fila['producto']), entero(fila['cantidad'])
        if producto in resultado:
            raise ValueError('Producto duplicado')
        resultado[producto] = unidades
    return resultado


def convertir_pagos(filas):
    if not isinstance(filas, list) or not filas:
        raise ValueError('Los pagos deben ser una lista no vacía')
    resultado = {}
    for fila in filas:
        if not isinstance(fila, dict) or set(fila) != {'medio', 'monto'}:
            raise ValueError('Cada pago requiere medio y monto')
        medio = texto(fila['medio'])
        if medio in resultado:
            raise ValueError('Medio de pago duplicado')
        resultado[medio] = texto(fila['monto'])
    return resultado


def ejecutar_accion(sistema, cuerpo):
    if not isinstance(cuerpo, dict):
        raise ValueError('El cuerpo debe ser un objeto JSON')
    campos = {
        'guardar': ({'tabla', 'datos'}, {'id'}),
        'baja': ({'tabla', 'id'}, set()),
        'asociar_proveedor': ({'producto_id', 'proveedor_id', 'costo', 'principal'}, set()),
        'definir_minimo': ({'sucursal', 'producto', 'minimo'}, set()),
        'ingresar_proveedor': ({'sucursal', 'producto', 'proveedor', 'unidades', 'costo'}, set()),
        'crear_orden': ({'origen', 'destino', 'items'}, set()),
        'crear_remito': ({'orden'}, set()),
        'preparar_bulto': ({'remito', 'items', 'responsable'}, set()),
        'precintar': ({'id', 'codigo', 'responsable'}, set()),
        'despachar': ({'remito', 'responsable'}, set()),
        'recibir': ({'id', 'integro', 'responsable'}, set()),
        'verificar': ({'id', 'responsable'}, {'motivo'}),
        'vender': ({'sucursal', 'items', 'pagos'}, set()),
        'devolver': ({'venta', 'producto', 'unidades', 'apto', 'medio'}, set()),
    }
    accion = cuerpo.get('accion')
    if not isinstance(accion, str) or accion not in campos:
        raise ValueError('Acción desconocida')
    requerido, opcional = campos[accion]
    datos = {k: v for k, v in cuerpo.items() if k != 'accion'}
    if not requerido <= datos.keys() or datos.keys() - requerido - opcional:
        raise ValueError('Campos incompletos o desconocidos')
    for clave in ('id', 'sucursal', 'producto', 'proveedor', 'producto_id',
                  'proveedor_id', 'origen', 'destino', 'orden', 'remito',
                  'venta', 'unidades'):
        if clave in datos:
            if accion == 'guardar' and clave == 'id' and datos[clave] is None:
                continue
            entero(datos[clave])
    if 'minimo' in datos:
        if type(datos['minimo']) is not int or datos['minimo'] < 0:
            raise ValueError('El mínimo debe ser un entero no negativo')
    for clave in ('principal', 'integro', 'apto'):
        if clave in datos:
            booleano(datos[clave])
    for clave in ('tabla', 'costo', 'responsable', 'codigo', 'motivo', 'medio'):
        if clave in datos:
            texto(datos[clave])
    if 'items' in datos:
        datos['items'] = convertir_items(datos['items'])
    if 'pagos' in datos:
        datos['pagos'] = convertir_pagos(datos['pagos'])
    if accion == 'guardar':
        if not isinstance(datos['datos'], dict):
            raise ValueError('Datos debe ser un objeto')
        for clave, valor in datos['datos'].items():
            if clave == 'categoria_id':
                entero(valor)
            else:
                texto(valor)
    return getattr(sistema, accion)(**datos)


class ServidorLocal(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, ruta_db, puerto=8080, static=STATIC):
        if ruta_db == ':memory:':
            raise ValueError('El servidor requiere un archivo SQLite persistente')
        if type(puerto) is not int or not 0 <= puerto <= 65535:
            raise ValueError('Puerto inválido')
        self.ruta_db = str(Path(ruta_db).resolve())
        self.static = Path(static).resolve()
        super().__init__(('127.0.0.1', puerto), Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = 'DistribucionLocal'
    sys_version = ''

    def log_message(self, formato, *args):
        # Evita volcar datos del cliente o payloads al terminal.
        pass

    def _headers(self, estado, tipo, longitud, descarga=False):
        self.send_response(estado)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(longitud))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if descarga:
            self.send_header('Content-Disposition', 'attachment; filename="reporte.csv"')
        self.end_headers()

    def _json(self, estado, datos):
        contenido = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        self._headers(estado, 'application/json; charset=utf-8', len(contenido))
        self.wfile.write(contenido)

    def _local(self, escritura=False):
        puerto = self.server.server_address[1]
        hosts = {f'127.0.0.1:{puerto}', f'localhost:{puerto}'}
        host = self.headers.get('Host', '')
        if host not in hosts:
            return False
        origen = self.headers.get('Origin')
        # Cualquier Origin presente debe corresponder exactamente al Host.
        if origen is not None and origen != f'http://{host}':
            return False
        if escritura:
            if self.headers.get('Sec-Fetch-Site') not in (None, 'same-origin', 'none'):
                return False
            # Sin Origin se acepta solo cliente no navegador (p.ej. tests/curl).
            if origen is None and self.headers.get('Sec-Fetch-Site') is not None:
                return False
        return True

    def _reporte(self, sistema, consulta):
        parametros = parse_qs(consulta, keep_blank_values=True)
        if parametros.keys() - {'tipo', 'desde', 'hasta', 'sucursal', 'top'}:
            raise ValueError('Filtro desconocido')
        if any(len(v) != 1 for v in parametros.values()):
            raise ValueError('Filtro repetido')
        p = {k: v[0] for k, v in parametros.items()}
        sucursal = int(p['sucursal']) if p.get('sucursal') else None
        if sucursal is not None:
            entero(sucursal)
        return Reportes(sistema).generar(p.get('tipo', 'ventas'),
                                        p.get('desde') or '2000-01-01',
                                        p.get('hasta') or '2100-12-31',
                                        sucursal, int(p.get('top') or '10'))

    def do_GET(self):
        if not self._local():
            return self._json(403, {'ok': False, 'error': 'Acceso permitido solo desde el servidor local'})
        ruta = urlsplit(self.path)
        base = None
        try:
            if ruta.path in ('/api/datos', '/api/reportes', '/api/reportes.csv'):
                base = BaseDatos(self.server.ruta_db)
                sistema = Sistema(base)
                if ruta.path == '/api/datos':
                    # Snapshot coherente entre tablas frente a otras escrituras.
                    with base.transaccion():
                        resultado = {tabla: sistema.listar(tabla) for tabla in TABLAS}
                    return self._json(200, resultado)
                with base.transaccion():
                    resultado = self._reporte(sistema, ruta.query)
                if ruta.path == '/api/reportes':
                    return self._json(200, resultado)
                archivo = io.StringIO(newline='')
                if resultado:
                    escritor = csv.DictWriter(archivo, fieldnames=list(resultado[0]))
                    escritor.writeheader()
                    for fila in resultado:
                        # Impide fórmulas inyectadas al abrir CSV en una planilla.
                        escritor.writerow({k: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else v for k, v in fila.items()})
                contenido = ('\ufeff' + archivo.getvalue()).encode('utf-8')
                self._headers(200, 'text/csv; charset=utf-8', len(contenido), True)
                return self.wfile.write(contenido)
            nombre = unquote(ruta.path)
            permitido = nombre in ('/', '/index.html', '/app.js', '/styles.css')
            if nombre.startswith('/fonts/'):
                permitido = ('..' not in Path(nombre).parts and Path(nombre).suffix.lower() in ('.woff', '.woff2', '.ttf', '.otf'))
            archivo = (self.server.static / ('index.html' if nombre == '/' else nombre.lstrip('/'))).resolve()
            if not permitido or not archivo.is_relative_to(self.server.static) or not archivo.is_file():
                return self._json(404, {'ok': False, 'error': 'Recurso inexistente'})
            contenido = archivo.read_bytes()
            mime = mimetypes.guess_type(str(archivo))[0] or 'application/octet-stream'
            if archivo.suffix in ('.html', '.js', '.css'):
                mime += '; charset=utf-8'
            self._headers(200, mime, len(contenido))
            self.wfile.write(contenido)
        except (ValueError, TypeError, KeyError):
            self._json(400, {'ok': False, 'error': 'Parámetros de consulta inválidos'})
        except Exception:
            self._json(500, {'ok': False, 'error': 'No se pudo consultar la información'})
        finally:
            if base is not None:
                base.cerrar()

    def do_POST(self):
        if not self._local(escritura=True):
            return self._json(403, {'ok': False, 'error': 'Origen de solicitud no permitido'})
        if self.path != '/api/acciones':
            return self._json(404, {'ok': False, 'error': 'Recurso inexistente'})
        if self.headers.get_content_type() != 'application/json':
            return self._json(415, {'ok': False, 'error': 'Se requiere application/json'})
        if self.headers.get('Transfer-Encoding'):
            return self._json(400, {'ok': False, 'error': 'Transferencia no admitida'})
        try:
            longitud = int(self.headers.get('Content-Length', '-1'))
        except ValueError:
            longitud = -1
        if not 0 < longitud <= MAX_PAYLOAD:
            return self._json(413, {'ok': False, 'error': 'Cuerpo vacío o demasiado grande'})
        base = None
        try:
            cuerpo = json.loads(self.rfile.read(longitud).decode('utf-8'))
            base = BaseDatos(self.server.ruta_db)
            resultado = ejecutar_accion(Sistema(base), cuerpo)
            self._json(200, {'ok': True, 'resultado': resultado})
        except (ValueError, TypeError, KeyError, UnicodeError) as error:
            mensaje = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else 'Datos de solicitud inválidos'
            self._json(400, {'ok': False, 'error': mensaje})
        except sqlite3.IntegrityError:
            self._json(409, {'ok': False, 'error': 'La operación entra en conflicto con un registro existente o una regla de integridad'})
        except Exception:
            self._json(500, {'ok': False, 'error': 'No se pudo confirmar la operación'})
        finally:
            if base is not None:
                base.cerrar()


def servir(ruta_db, puerto=8080):
    with ServidorLocal(ruta_db, puerto) as servidor:
        print(f'TP DAO web: http://127.0.0.1:{servidor.server_address[1]} (Ctrl+C para salir)')
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
