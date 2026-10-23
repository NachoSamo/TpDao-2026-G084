import sqlite3
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
from distribucion.db import BaseDatos
from distribucion.servicios import Sistema
from distribucion.reportes import Reportes
from distribucion.demo import cargar
from distribucion.modelos import dinero

class CasoSistema(unittest.TestCase):
    def setUp(self):
        self.base=BaseDatos(':memory:');self.s=Sistema(self.base)
        self.cd=self.s.guardar('sucursal',dict(nombre='CD',direccion='A',tipo='CD'))
        self.local=self.s.guardar('sucursal',dict(nombre='Local',direccion='B',tipo='LOCAL'))
        self.cat=self.s.guardar('categoria',dict(nombre='Comida'))
        self.prov=self.s.guardar('proveedor',dict(nombre='Proveedor',cuit='123'))
        self.p=self.producto('P','10.10','4.05')
        self.s.ingresar_proveedor(self.cd,self.p,self.prov,100,'4.05')

    def tearDown(self):self.base.cerrar()

    def producto(self,codigo,precio,costo):
        return self.s.guardar('producto',dict(codigo=codigo,nombre=codigo,categoria_id=self.cat,precio=precio,costo=costo))

    def stock(self,sucursal):
        return self.s.dao.uno('SELECT * FROM stock WHERE sucursal_id=? AND producto_id=?',(sucursal,self.p))

    def bulto(self,q=20):
        o=self.s.crear_orden(self.cd,self.local,{self.p:q});r=self.s.crear_remito(o)
        b=self.s.preparar_bulto(r,{self.p:q},'Operario')
        return r,b

    def abastecer(self,q=20):
        r,b=self.bulto(q);self.s.precintar(b,f'P-{b}','A');self.s.despachar(r,'A');self.s.recibir(b,True,'B');self.s.verificar(b,'B')
        return r,b

    def test_flujo_completo_dinero_historico_reportes(self):
        self.abastecer()
        v=self.s.vender(self.local,{self.p:3},{'EFECTIVO':'20.20','DEBITO':'10.10'})
        self.s.guardar('producto',dict(codigo='P',nombre='P',categoria_id=self.cat,precio='999.00',costo='888.00'),self.p)
        self.s.devolver(v,self.p,1,True,'EFECTIVO')
        self.assertEqual(self.stock(self.local)['cantidad'],18)
        self.assertEqual(self.stock(self.cd)['cantidad'],80)
        rep=Reportes(self.s)
        ventas=rep.generar('ventas');self.assertEqual(sum(Decimal(x['neto']) for x in ventas),Decimal('20.20'))
        margen=rep.generar('margen')[0];self.assertEqual(margen['unidades_netas'],2);self.assertEqual(Decimal(margen['margen']),Decimal('12.10'))
        self.assertEqual(rep.generar('transito')[0]['bultos'],1)
        self.assertEqual(rep.generar('rechazos'),[])
        self.assertEqual(rep.generar('ventas','2000-01-01','2000-01-02'),[])

    def test_reserva_y_no_sobreempaquetado(self):
        r,b=self.bulto(60)
        self.assertEqual(self.stock(self.cd)['reservada'],60)
        with self.assertRaises(ValueError):self.s.preparar_bulto(r,{self.p:1},'A')
        o=self.s.crear_orden(self.cd,self.local,{self.p:50});r2=self.s.crear_remito(o)
        with self.assertRaises(ValueError):self.s.preparar_bulto(r2,{self.p:50},'A')
        self.assertEqual(self.stock(self.cd)['reservada'],60)

    def test_despacho_atomico_todos_precintados(self):
        o=self.s.crear_orden(self.cd,self.local,{self.p:20});r=self.s.crear_remito(o)
        b=self.s.preparar_bulto(r,{self.p:10},'A');b2=self.s.preparar_bulto(r,{self.p:10},'A');self.s.precintar(b,'P','A')
        with self.assertRaises(ValueError):self.s.despachar(r,'A')
        self.assertEqual(self.stock(self.cd)['cantidad'],100)
        self.assertEqual(self.s.listar('bulto')[0]['estado'],'PRECINTADO')
        self.assertFalse(any(h['nuevo']=='EN_TRANSITO' for h in self.s.listar('historial')))

    def test_rechazo_y_remito_mixto(self):
        o=self.s.crear_orden(self.cd,self.local,{self.p:20});r=self.s.crear_remito(o)
        bs=[self.s.preparar_bulto(r,{self.p:10},'A') for _ in range(2)]
        for b in bs:self.s.precintar(b,f'P{b}','A')
        self.s.despachar(r,'A')
        self.s.recibir(bs[0],True,'B');self.s.verificar(bs[0],'B')
        self.assertEqual(self.stock(self.local)['cantidad'],10)
        self.s.recibir(bs[1],False,'B')
        with self.assertRaises(ValueError):self.s.verificar(bs[1],'B')
        self.s.verificar(bs[1],'B','Roto')
        self.assertEqual(self.stock(self.local)['cantidad'],10)
        self.assertEqual(self.s.listar('remito')[0]['estado'],'PARCIALMENTE_ACEPTADO')
        self.assertEqual(Reportes(self.s).generar('rechazos')[0]['unidades'],10)

    def test_state_no_doble_ingreso_despacho_recepcion(self):
        r,b=self.abastecer()
        for fn in (lambda:self.s.verificar(b,'A'),lambda:self.s.recibir(b,True,'A'),lambda:self.s.despachar(r,'A'),lambda:self.s.precintar(b,'Otro','A')):
            with self.assertRaises(ValueError):fn()
        self.assertEqual(self.stock(self.local)['cantidad'],20)
        self.assertEqual(len(self.s.listar('historial')),5)

    def test_venta_fallida_revierte_todo(self):
        self.abastecer(2)
        with self.assertRaises(ValueError):self.s.vender(self.local,{self.p:3},{'EFECTIVO':'30.30'})
        self.assertEqual(self.s.listar('venta'),[]);self.assertEqual(self.s.listar('detalle_venta'),[])
        self.assertEqual(self.stock(self.local)['cantidad'],2)
        with self.assertRaises(ValueError):self.s.vender(self.local,{self.p:1},{'EFECTIVO':'10.00'})
        self.assertEqual(self.s.listar('venta'),[])

    def test_falla_persistencia_revierte_venta_y_observer(self):
        self.abastecer(20);self.s.definir_minimo(self.local,self.p,20)
        self.base.conexion.execute("CREATE TRIGGER fallo BEFORE INSERT ON cobro BEGIN SELECT RAISE(ABORT,'Fallo simulado'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.s.vender(self.local,{self.p:1},{'EFECTIVO':'10.10'})
        self.assertEqual(self.stock(self.local)['cantidad'],20);self.assertEqual(self.s.listar('venta'),[])
        self.assertEqual(self.s.listar('aviso'),[])
        self.assertEqual(len(self.s.listar('orden')),1)

    def test_observer_no_duplica_pendientes_y_varios_observadores(self):
        self.abastecer(20);self.s.definir_minimo(self.local,self.p,20)
        class Espia:
            def __init__(self):self.llamadas=0
            def actualizar(self,stock):self.llamadas+=1
        espia=Espia();self.s.observadores.append(espia)
        self.s.vender(self.local,{self.p:2},{'EFECTIVO':'20.20'})
        self.s.definir_minimo(self.local,self.p,20)
        pendientes=self.s.dao.todos('SELECT * FROM detalle_orden WHERE orden_id>1')
        self.assertEqual(sum(x['cantidad'] for x in pendientes),2)
        self.s.vender(self.local,{self.p:1},{'EFECTIVO':'10.10'})
        self.assertEqual(sum(x['cantidad'] for x in self.s.dao.todos('SELECT * FROM detalle_orden WHERE orden_id>1')),3)
        self.assertEqual(espia.llamadas,3)

    def test_devolucion_acumulada_y_no_apto(self):
        self.abastecer();v=self.s.vender(self.local,{self.p:2},{'EFECTIVO':'20.20'})
        with self.assertRaises(ValueError):self.s.devolver(v,self.p,1,False,'EFECTIVO')
        self.s.devolver(v,self.p,1,True,'EFECTIVO');self.s.devolver(v,self.p,1,True,'EFECTIVO')
        with self.assertRaises(ValueError):self.s.devolver(v,self.p,1,True,'EFECTIVO')
        with self.assertRaises(ValueError):self.s.devolver(999,self.p,1,True,'EFECTIVO')
        self.assertEqual(self.stock(self.local)['cantidad'],20)

    def test_integridad_historial_movimientos_fk(self):
        self.abastecer()
        for sql in ('DELETE FROM historial','UPDATE historial SET responsable="Otro"','DELETE FROM movimiento','UPDATE movimiento SET cantidad=999'):
            with self.assertRaises(sqlite3.IntegrityError):self.base.conexion.execute(sql)
        with self.assertRaises(sqlite3.IntegrityError):self.base.conexion.execute("INSERT INTO stock VALUES (999,999,0,0,0)")
        self.assertEqual(self.base.conexion.execute('PRAGMA foreign_keys').fetchone()[0],1)

    def test_catalogo_bajas_duplicados_y_proveedores(self):
        with self.assertRaises(sqlite3.IntegrityError):self.producto('P','10','4')
        with self.assertRaises(sqlite3.IntegrityError):self.s.guardar('proveedor',dict(nombre='Otro',cuit='123'))
        self.s.asociar_proveedor(self.p,self.prov,'4.05',True)
        p2=self.s.guardar('proveedor',dict(nombre='Otro',cuit='456'));self.s.asociar_proveedor(self.p,p2,'5',True)
        self.assertEqual(sum(x['principal'] for x in self.s.listar('producto_proveedor')),1)
        self.s.baja('producto',self.p)
        with self.assertRaises(ValueError):self.s.crear_orden(self.cd,self.local,{self.p:1})
        self.assertEqual(len(self.s.listar('producto')),1)

    def test_transito_exactamente_dos_horas_y_filtros(self):
        r,b=self.bulto(5);self.s.precintar(b,'P','A')
        with patch('distribucion.servicios.ahora',return_value='2026-10-01T10:00:00+00:00'):
            self.s.despachar(r,'A')
        with patch('distribucion.servicios.ahora',return_value='2026-10-01T12:00:00+00:00'):
            self.s.recibir(b,True,'B')
        fila=Reportes(self.s).generar('transito','2026-10-01','2026-10-01',self.local)[0]
        self.assertEqual(Decimal(fila['promedio_horas']),Decimal('2'))
        self.assertEqual(Reportes(self.s).generar('transito','2026-10-02','2026-10-02'),[])
        self.assertEqual(Reportes(self.s).generar('transito','2026-10-01','2026-10-01',self.cd),[])

    def test_venta_multiproducto_insuficiente_revierte_primer_producto(self):
        self.abastecer(5);p2=self.producto('OTRO','20.00','10.00')
        with self.assertRaises(ValueError):
            self.s.vender(self.local,{self.p:1,p2:1},{'EFECTIVO':'30.10'})
        self.assertEqual(self.stock(self.local)['cantidad'],5)
        self.assertEqual(self.s.listar('venta'),[])

    def test_logistica_iniciada_puede_concluir_con_destino_inactivo(self):
        r,b=self.bulto(5);self.s.precintar(b,'P','A');self.s.despachar(r,'A')
        self.s.baja('sucursal',self.local)
        self.s.recibir(b,True,'B');self.s.verificar(b,'B')
        self.assertEqual(self.stock(self.local)['cantidad'],5)

    def test_validaciones_y_dinero(self):
        for monto in (0.1,'NaN','Infinity','-1','1.001'):
            with self.assertRaises(ValueError):dinero(monto)
        for q in (0,-1,1.2,True):
            with self.assertRaises(ValueError):self.s.crear_orden(self.cd,self.local,{self.p:q})
        with self.assertRaises(ValueError):self.s.crear_orden(self.local,self.cd,{self.p:1})
        with self.assertRaises(ValueError):self.s.vender(self.cd,{self.p:1},{'EFECTIVO':'10.10'})
        with self.assertRaises(ValueError):self.s.listar('sqlite_master')

class TestDemo(unittest.TestCase):
    def test_persistencia_archivo_y_fk_en_cada_conexion(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta=str(Path(carpeta)/'test.db')
            base=BaseDatos(ruta);s=Sistema(base);cargar(s);base.cerrar()
            base=BaseDatos(ruta);s=Sistema(base)
            self.assertEqual(s.listar('venta')[0]['comprobante'],'V-00000001')
            self.assertEqual(base.conexion.execute('PRAGMA foreign_keys').fetchone()[0],1)
            self.assertEqual(Reportes(s).generar('margen')[0]['margen'],'1800.50')
            base.cerrar()

    def test_demo_reproducible_y_reportes(self):
        for _ in range(2):
            b=BaseDatos(':memory:');s=Sistema(b);cargar(s)
            self.assertEqual(Reportes(s).generar('margen')[0]['margen'],'1800.50')
            self.assertEqual(Reportes(s).generar('transito')[0]['bultos'],2)
            self.assertEqual(len(Reportes(s).generar('rechazos')),1)
            with self.assertRaises(ValueError):cargar(s)
            b.cerrar()

if __name__=='__main__':unittest.main()
