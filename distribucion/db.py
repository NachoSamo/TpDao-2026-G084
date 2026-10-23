"""Persistencia SQLite. Los DAO nunca confirman transacciones."""
import sqlite3
from contextlib import contextmanager

SCHEMA = '''
CREATE TABLE IF NOT EXISTS sucursal(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,direccion TEXT NOT NULL,tipo TEXT NOT NULL CHECK(tipo IN ('LOCAL','CD')),activo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS categoria(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL UNIQUE,activo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS proveedor(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,cuit TEXT NOT NULL UNIQUE,activo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS producto(id INTEGER PRIMARY KEY,codigo TEXT NOT NULL UNIQUE,nombre TEXT NOT NULL,categoria_id INTEGER NOT NULL REFERENCES categoria(id),precio TEXT NOT NULL,costo TEXT NOT NULL,activo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS producto_proveedor(producto_id INTEGER REFERENCES producto(id),proveedor_id INTEGER REFERENCES proveedor(id),costo TEXT NOT NULL,principal INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(producto_id,proveedor_id));
CREATE UNIQUE INDEX IF NOT EXISTS proveedor_principal ON producto_proveedor(producto_id) WHERE principal=1;
CREATE TABLE IF NOT EXISTS stock(sucursal_id INTEGER REFERENCES sucursal(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL DEFAULT 0 CHECK(cantidad>=0),reservada INTEGER NOT NULL DEFAULT 0 CHECK(reservada>=0 AND reservada<=cantidad),minimo INTEGER NOT NULL DEFAULT 0 CHECK(minimo>=0),PRIMARY KEY(sucursal_id,producto_id));
CREATE TABLE IF NOT EXISTS movimiento(id INTEGER PRIMARY KEY,fecha TEXT NOT NULL,sucursal_id INTEGER REFERENCES sucursal(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL,tipo TEXT NOT NULL,referencia TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ingreso(id INTEGER PRIMARY KEY,fecha TEXT NOT NULL,proveedor_id INTEGER REFERENCES proveedor(id),sucursal_id INTEGER REFERENCES sucursal(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL,costo TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orden(id INTEGER PRIMARY KEY,fecha TEXT NOT NULL,origen_id INTEGER REFERENCES sucursal(id),destino_id INTEGER REFERENCES sucursal(id));
CREATE TABLE IF NOT EXISTS detalle_orden(orden_id INTEGER REFERENCES orden(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL CHECK(cantidad>0),PRIMARY KEY(orden_id,producto_id));
CREATE TABLE IF NOT EXISTS remito(id INTEGER PRIMARY KEY,orden_id INTEGER REFERENCES orden(id),estado TEXT NOT NULL DEFAULT 'PREPARADO');
CREATE TABLE IF NOT EXISTS bulto(id INTEGER PRIMARY KEY,remito_id INTEGER REFERENCES remito(id),estado TEXT NOT NULL,precinto TEXT UNIQUE,integro INTEGER,motivo TEXT);
CREATE TABLE IF NOT EXISTS detalle_bulto(bulto_id INTEGER REFERENCES bulto(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL CHECK(cantidad>0),PRIMARY KEY(bulto_id,producto_id));
CREATE TABLE IF NOT EXISTS historial(id INTEGER PRIMARY KEY,bulto_id INTEGER REFERENCES bulto(id),fecha TEXT NOT NULL,anterior TEXT,nuevo TEXT NOT NULL,responsable TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS venta(id INTEGER PRIMARY KEY,fecha TEXT NOT NULL,sucursal_id INTEGER REFERENCES sucursal(id),total TEXT NOT NULL,comprobante TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS detalle_venta(venta_id INTEGER REFERENCES venta(id),producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL CHECK(cantidad>0),precio TEXT NOT NULL,costo TEXT NOT NULL,PRIMARY KEY(venta_id,producto_id));
CREATE TABLE IF NOT EXISTS cobro(id INTEGER PRIMARY KEY,venta_id INTEGER REFERENCES venta(id),medio TEXT NOT NULL CHECK(medio IN ('EFECTIVO','DEBITO','CREDITO','TRANSFERENCIA')),monto TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS devolucion(id INTEGER PRIMARY KEY,venta_id INTEGER REFERENCES venta(id),fecha TEXT NOT NULL,producto_id INTEGER REFERENCES producto(id),cantidad INTEGER NOT NULL CHECK(cantidad>0),monto TEXT NOT NULL,medio TEXT NOT NULL CHECK(medio IN ('EFECTIVO','DEBITO','CREDITO','TRANSFERENCIA')));
CREATE TABLE IF NOT EXISTS aviso(id INTEGER PRIMARY KEY,fecha TEXT NOT NULL,sucursal_id INTEGER REFERENCES sucursal(id),producto_id INTEGER REFERENCES producto(id),faltante INTEGER NOT NULL);
CREATE TRIGGER IF NOT EXISTS historial_no_update BEFORE UPDATE ON historial BEGIN SELECT RAISE(ABORT,'Historial inmutable'); END;
CREATE TRIGGER IF NOT EXISTS historial_no_delete BEFORE DELETE ON historial BEGIN SELECT RAISE(ABORT,'Historial inmutable'); END;
CREATE TRIGGER IF NOT EXISTS movimiento_no_update BEFORE UPDATE ON movimiento BEGIN SELECT RAISE(ABORT,'Movimiento inmutable'); END;
CREATE TRIGGER IF NOT EXISTS movimiento_no_delete BEFORE DELETE ON movimiento BEGIN SELECT RAISE(ABORT,'Movimiento inmutable'); END;
'''

class BaseDatos:
    def __init__(self, ruta='distribucion.db'):
        self.conexion = sqlite3.connect(ruta, isolation_level=None)
        self.conexion.row_factory = sqlite3.Row
        self.conexion.execute('PRAGMA foreign_keys=ON')
        self.conexion.executescript(SCHEMA)

    @contextmanager
    def transaccion(self):
        self.conexion.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.conexion.commit()
        except Exception:
            self.conexion.rollback()
            raise

    def cerrar(self):
        self.conexion.close()

class DAO:
    def __init__(self, base):
        self.db = base.conexion

    def ejecutar(self, sql, parametros=()):
        return self.db.execute(sql, parametros)

    def uno(self, sql, parametros=()):
        fila = self.ejecutar(sql, parametros).fetchone()
        if fila is None:
            raise ValueError('Registro inexistente')
        return dict(fila)

    def todos(self, sql, parametros=()):
        return [dict(f) for f in self.ejecutar(sql, parametros).fetchall()]

    def insertar(self, tabla, **datos):
        # Tabla/columnas son constantes internas, nunca texto de la interfaz.
        columnas = ','.join(datos)
        marcas = ','.join('?' for _ in datos)
        return self.ejecutar(f'INSERT INTO {tabla} ({columnas}) VALUES ({marcas})', tuple(datos.values())).lastrowid
