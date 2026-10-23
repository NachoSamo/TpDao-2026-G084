"""Casos de uso: cada comando público confirma una única transacción."""
from datetime import datetime, timezone, date
from decimal import Decimal
from functools import wraps
from .db import DAO
from .modelos import dinero, cantidad, Bulto, ESTADOS, Stock, GeneradorReposicionAutomatica


def ahora():
    return datetime.now(timezone.utc).isoformat()


def atomico(metodo):
    @wraps(metodo)
    def ejecutar(self, *args, **kwargs):
        with self.base.transaccion():
            return metodo(self, *args, **kwargs)
    return ejecutar


class Sistema:
    def __init__(self, base):
        self.base = base
        self.dao = DAO(base)
        self.observadores = [GeneradorReposicionAutomatica(self)]

    def listar(self, tabla):
        permitidas = {'sucursal','categoria','proveedor','producto','producto_proveedor','stock','movimiento','ingreso','orden','detalle_orden','remito','bulto','detalle_bulto','historial','venta','detalle_venta','cobro','devolucion','aviso'}
        if tabla not in permitidas:
            raise ValueError('Tabla desconocida')
        return self.dao.todos(f'SELECT * FROM {tabla}')

    def entidad(self, tabla, id):
        if tabla not in {'sucursal','categoria','proveedor','producto'}:
            raise ValueError('Entidad inválida')
        obj = self.dao.uno(f'SELECT * FROM {tabla} WHERE id=?', (id,))
        if not obj['activo']:
            raise ValueError(f'{tabla} inactivo')
        return obj

    @atomico
    def guardar(self, tabla, datos, id=None):
        campos = {'sucursal': {'nombre','direccion','tipo'}, 'categoria': {'nombre'}, 'proveedor': {'nombre','cuit'}, 'producto': {'codigo','nombre','categoria_id','precio','costo'}}
        if tabla not in campos or set(datos) != campos[tabla]:
            raise ValueError('Completá todos los campos de la entidad')
        datos = dict(datos)
        for clave, valor in datos.items():
            if isinstance(valor, str):
                datos[clave] = valor.strip()
                if not datos[clave]:
                    raise ValueError('Campos obligatorios vacíos')
        if tabla == 'sucursal':
            if datos['tipo'] not in ('CD','LOCAL'):
                raise ValueError('Tipo debe ser CD o LOCAL')
            if id is not None and self.entidad(tabla,id)['tipo'] != datos['tipo']:
                raise ValueError('El tipo de sucursal no se modifica; crear otra sucursal')
        if tabla == 'producto':
            self.entidad('categoria',datos['categoria_id'])
            datos['precio'], datos['costo'] = str(dinero(datos['precio'])), str(dinero(datos['costo']))
        if id is None:
            return self.dao.insertar(tabla, **datos)
        self.entidad(tabla,id)
        self.dao.ejecutar(f'UPDATE {tabla} SET '+','.join(f'{k}=?' for k in datos)+' WHERE id=?', (*datos.values(),id))
        return id

    @atomico
    def baja(self, tabla, id):
        self.entidad(tabla,id)
        self.dao.ejecutar(f'UPDATE {tabla} SET activo=0 WHERE id=?',(id,))

    @atomico
    def asociar_proveedor(self, producto_id, proveedor_id, costo, principal=False):
        self.entidad('producto',producto_id)
        self.entidad('proveedor',proveedor_id)
        if principal:
            self.dao.ejecutar('UPDATE producto_proveedor SET principal=0 WHERE producto_id=?',(producto_id,))
        self.dao.ejecutar('INSERT INTO producto_proveedor VALUES (?,?,?,?) ON CONFLICT(producto_id,proveedor_id) DO UPDATE SET costo=excluded.costo,principal=excluded.principal',(producto_id,proveedor_id,str(dinero(costo)),int(principal)))

    def _stock(self, sucursal, producto):
        self.dao.ejecutar('INSERT OR IGNORE INTO stock(sucursal_id,producto_id) VALUES (?,?)',(sucursal,producto))
        return self.dao.uno('SELECT * FROM stock WHERE sucursal_id=? AND producto_id=?',(sucursal,producto))

    def _mover(self, sucursal, producto, unidades, tipo, referencia):
        s = self._stock(sucursal,producto)
        if s['cantidad'] + unidades < s['reservada']:
            raise ValueError('Stock disponible insuficiente')
        self.dao.ejecutar('UPDATE stock SET cantidad=cantidad+? WHERE sucursal_id=? AND producto_id=?',(unidades,sucursal,producto))
        self.dao.insertar('movimiento',fecha=ahora(),sucursal_id=sucursal,producto_id=producto,cantidad=unidades,tipo=tipo,referencia=referencia)

    def _avisar(self, sucursal, producto):
        s = self._stock(sucursal,producto)
        Stock(sucursal,producto,s['cantidad']-s['reservada'],s['minimo'],self.observadores).notificar()

    @atomico
    def definir_minimo(self, sucursal, producto, minimo):
        self.entidad('sucursal',sucursal)
        self.entidad('producto',producto)
        cantidad(minimo,True)
        self._stock(sucursal,producto)
        self.dao.ejecutar('UPDATE stock SET minimo=? WHERE sucursal_id=? AND producto_id=?',(minimo,sucursal,producto))
        self._avisar(sucursal,producto)

    @atomico
    def ingresar_proveedor(self, sucursal, producto, proveedor, unidades, costo):
        if self.entidad('sucursal',sucursal)['tipo'] != 'CD':
            raise ValueError('Los ingresos de proveedor se realizan al CD')
        self.entidad('producto',producto)
        self.entidad('proveedor',proveedor)
        cantidad(unidades)
        valor = str(dinero(costo))
        id = self.dao.insertar('ingreso',fecha=ahora(),proveedor_id=proveedor,sucursal_id=sucursal,producto_id=producto,cantidad=unidades,costo=valor)
        self._mover(sucursal,producto,unidades,'COMPRA',f'ingreso:{id}')
        self.dao.ejecutar('UPDATE producto SET costo=? WHERE id=?',(valor,producto))
        return id

    def _items(self, items):
        if not items:
            raise ValueError('Debe haber al menos un producto')
        for producto, unidades in items.items():
            self.entidad('producto',producto)
            cantidad(unidades)

    def _orden(self, origen, destino, items):
        if self.entidad('sucursal',origen)['tipo'] != 'CD' or self.entidad('sucursal',destino)['tipo'] != 'LOCAL':
            raise ValueError('La reposición debe ser CD → local')
        self._items(items)
        id = self.dao.insertar('orden',fecha=ahora(),origen_id=origen,destino_id=destino)
        for p,q in items.items():
            self.dao.insertar('detalle_orden',orden_id=id,producto_id=p,cantidad=q)
        return id

    @atomico
    def crear_orden(self, origen, destino, items):
        return self._orden(origen,destino,items)

    def consolidar_faltante(self, stock):
        # Callback Observer dentro de la transacción que produjo el faltante.
        destino = self.dao.uno('SELECT * FROM sucursal WHERE id=?',(stock.sucursal_id,))
        faltante = stock.minimo-stock.disponible
        self.dao.insertar('aviso',fecha=ahora(),sucursal_id=stock.sucursal_id,producto_id=stock.producto_id,faltante=faltante)
        if destino['tipo'] != 'LOCAL' or not destino['activo']:
            return
        cds = self.dao.todos("SELECT id FROM sucursal WHERE tipo='CD' AND activo=1 ORDER BY id")
        if not cds:
            raise ValueError('Configurá un CD activo antes de activar la reposición')
        # Pendiente = solicitado menos unidades ya recibidas o rechazadas.
        solicitado = self.dao.uno('SELECT COALESCE(SUM(d.cantidad),0) n FROM detalle_orden d JOIN orden o ON o.id=d.orden_id WHERE o.destino_id=? AND d.producto_id=?',(stock.sucursal_id,stock.producto_id))['n']
        terminado = self.dao.uno("SELECT COALESCE(SUM(d.cantidad),0) n FROM detalle_bulto d JOIN bulto b ON b.id=d.bulto_id JOIN remito r ON r.id=b.remito_id JOIN orden o ON o.id=r.orden_id WHERE o.destino_id=? AND d.producto_id=? AND b.estado IN ('VERIFICADO','RECHAZADO')",(stock.sucursal_id,stock.producto_id))['n']
        agregar = faltante-(solicitado-terminado)
        if agregar <= 0:
            return
        abiertas = self.dao.todos('SELECT o.id FROM orden o WHERE o.origen_id=? AND o.destino_id=? AND NOT EXISTS(SELECT 1 FROM remito r WHERE r.orden_id=o.id) ORDER BY o.id',(cds[0]['id'],stock.sucursal_id))
        if abiertas:
            self.dao.ejecutar('INSERT INTO detalle_orden VALUES (?,?,?) ON CONFLICT(orden_id,producto_id) DO UPDATE SET cantidad=cantidad+excluded.cantidad',(abiertas[0]['id'],stock.producto_id,agregar))
        else:
            self._orden(cds[0]['id'],stock.sucursal_id,{stock.producto_id:agregar})

    @atomico
    def crear_remito(self, orden):
        o = self.dao.uno('SELECT * FROM orden WHERE id=?',(orden,))
        self.entidad('sucursal',o['origen_id']); self.entidad('sucursal',o['destino_id'])
        return self.dao.insertar('remito',orden_id=orden)

    @atomico
    def preparar_bulto(self, remito, items, responsable):
        self._items(items)
        r = self.dao.uno('SELECT r.*,o.origen_id FROM remito r JOIN orden o ON o.id=r.orden_id WHERE r.id=?',(remito,))
        if r['estado'] != 'PREPARADO':
            raise ValueError('El remito ya fue despachado')
        self.entidad('sucursal',r['origen_id'])
        for p,q in items.items():
            pedido = self.dao.uno('SELECT cantidad FROM detalle_orden WHERE orden_id=? AND producto_id=?',(r['orden_id'],p))['cantidad']
            usado = self.dao.uno('SELECT COALESCE(SUM(d.cantidad),0) n FROM detalle_bulto d JOIN bulto b ON b.id=d.bulto_id JOIN remito r ON r.id=b.remito_id WHERE r.orden_id=? AND d.producto_id=?',(r['orden_id'],p))['n']
            if usado+q > pedido:
                raise ValueError('Cantidad superior al pendiente de la orden')
            s = self._stock(r['origen_id'],p)
            if s['cantidad']-s['reservada'] < q:
                raise ValueError('Stock CD insuficiente para reservar')
            self.dao.ejecutar('UPDATE stock SET reservada=reservada+? WHERE sucursal_id=? AND producto_id=?',(q,r['origen_id'],p))
        id = self.dao.insertar('bulto',remito_id=remito,estado='PREPARADO')
        for p,q in items.items():
            self.dao.insertar('detalle_bulto',bulto_id=id,producto_id=p,cantidad=q)
        self._historial(id,None,'PREPARADO',responsable)
        return id

    def _historial(self,id,anterior,nuevo,responsable):
        if not responsable or not responsable.strip():
            raise ValueError('Responsable obligatorio')
        self.dao.insertar('historial',bulto_id=id,fecha=ahora(),anterior=anterior,nuevo=nuevo,responsable=responsable.strip())

    def _transicion(self,id,accion,responsable,*args):
        fila = self.dao.uno('SELECT * FROM bulto WHERE id=?',(id,))
        obj = Bulto(id,ESTADOS[fila['estado']]())
        anterior,nuevo = obj.transicionar(accion,*args)
        self.dao.ejecutar('UPDATE bulto SET estado=? WHERE id=?',(nuevo,id))
        self._historial(id,anterior,nuevo,responsable)
        return fila

    @atomico
    def precintar(self, id, codigo, responsable):
        if not codigo or not codigo.strip():
            raise ValueError('Precinto obligatorio')
        self._transicion(id,'precintar',responsable)
        self.dao.ejecutar('UPDATE bulto SET precinto=? WHERE id=?',(codigo.strip(),id))

    @atomico
    def despachar(self, remito, responsable):
        r = self.dao.uno('SELECT r.*,o.origen_id FROM remito r JOIN orden o ON o.id=r.orden_id WHERE r.id=?',(remito,))
        if r['estado'] != 'PREPARADO':
            raise ValueError('Remito ya despachado')
        self.entidad('sucursal',r['origen_id'])
        bultos = self.dao.todos('SELECT id FROM bulto WHERE remito_id=?',(remito,))
        if not bultos:
            raise ValueError('Remito sin bultos')
        for b in bultos:
            self._transicion(b['id'],'despachar',responsable)
            for d in self.dao.todos('SELECT * FROM detalle_bulto WHERE bulto_id=?',(b['id'],)):
                self.dao.ejecutar('UPDATE stock SET reservada=reservada-? WHERE sucursal_id=? AND producto_id=?',(d['cantidad'],r['origen_id'],d['producto_id']))
                self._mover(r['origen_id'],d['producto_id'],-d['cantidad'],'DESPACHO',f'bulto:{b["id"]}')
        self.dao.ejecutar("UPDATE remito SET estado='EN_TRANSITO' WHERE id=?",(remito,))

    @atomico
    def recibir(self,id,integro,responsable):
        if type(integro) is not bool:
            raise ValueError('Indicá si el precinto está íntegro')
        self._transicion(id,'recibir',responsable)
        self.dao.ejecutar('UPDATE bulto SET integro=? WHERE id=?',(int(integro),id))

    @atomico
    def verificar(self,id,responsable,motivo=''):
        b = self.dao.uno('SELECT b.*,o.destino_id FROM bulto b JOIN remito r ON r.id=b.remito_id JOIN orden o ON o.id=r.orden_id WHERE b.id=?',(id,))
        if not b['integro'] and not motivo.strip():
            raise ValueError('Rechazo requiere motivo')
        self._transicion(id,'verificar',responsable,bool(b['integro']))
        self.dao.ejecutar('UPDATE bulto SET motivo=? WHERE id=?',(motivo.strip(),id))
        if b['integro']:
            for d in self.dao.todos('SELECT * FROM detalle_bulto WHERE bulto_id=?',(id,)):
                self._mover(b['destino_id'],d['producto_id'],d['cantidad'],'RECEPCION_VERIFICADA',f'bulto:{id}')
        estados = [x['estado'] for x in self.dao.todos('SELECT estado FROM bulto WHERE remito_id=?',(b['remito_id'],))]
        terminales = {'VERIFICADO','RECHAZADO'}
        estado = ('VERIFICADO' if set(estados)=={'VERIFICADO'} else 'RECHAZADO' if set(estados)=={'RECHAZADO'} else 'PARCIALMENTE_ACEPTADO') if set(estados)<=terminales else 'EN_REVISION'
        self.dao.ejecutar('UPDATE remito SET estado=? WHERE id=?',(estado,b['remito_id']))
        for d in self.dao.todos('SELECT producto_id FROM detalle_bulto WHERE bulto_id=?',(id,)):
            self._avisar(b['destino_id'],d['producto_id'])

    @atomico
    def vender(self,sucursal,items,pagos):
        if self.entidad('sucursal',sucursal)['tipo'] != 'LOCAL':
            raise ValueError('Solo los locales venden')
        self._items(items)
        total = Decimal('0')
        productos = {}
        for p,q in items.items():
            productos[p] = self.entidad('producto',p)
            total += dinero(productos[p]['precio'])*q
        if not pagos or any(m not in ('EFECTIVO','DEBITO','CREDITO','TRANSFERENCIA') for m in pagos):
            raise ValueError('Medio de pago inválido')
        if any(dinero(m)<=0 for m in pagos.values()) or sum((dinero(m) for m in pagos.values()),Decimal('0')) != total:
            raise ValueError('Los cobros deben sumar el total exacto')
        id = self.dao.insertar('venta',fecha=ahora(),sucursal_id=sucursal,total=str(total))
        self.dao.ejecutar('UPDATE venta SET comprobante=? WHERE id=?',(f'V-{id:08d}',id))
        for p,q in items.items():
            prod=productos[p]
            self.dao.insertar('detalle_venta',venta_id=id,producto_id=p,cantidad=q,precio=prod['precio'],costo=prod['costo'])
            self._mover(sucursal,p,-q,'VENTA',f'venta:{id}')
            self._avisar(sucursal,p)
        for medio,monto in pagos.items():
            self.dao.insertar('cobro',venta_id=id,medio=medio,monto=str(dinero(monto)))
        return id

    @atomico
    def devolver(self,venta,producto,unidades,apto,medio):
        cantidad(unidades)
        if apto is not True:
            raise ValueError('Solo se acepta mercadería apta para reingreso')
        if medio not in ('EFECTIVO','DEBITO','CREDITO','TRANSFERENCIA'):
            raise ValueError('Medio de reintegro inválido')
        v = self.dao.uno('SELECT * FROM venta WHERE id=?',(venta,))
        d = self.dao.uno('SELECT * FROM detalle_venta WHERE venta_id=? AND producto_id=?',(venta,producto))
        devuelto = self.dao.uno('SELECT COALESCE(SUM(cantidad),0) n FROM devolucion WHERE venta_id=? AND producto_id=?',(venta,producto))['n']
        if unidades+devuelto>d['cantidad']:
            raise ValueError('La devolución supera lo vendido pendiente')
        monto = dinero(d['precio'])*unidades
        id = self.dao.insertar('devolucion',venta_id=venta,fecha=ahora(),producto_id=producto,cantidad=unidades,monto=str(monto),medio=medio)
        self._mover(v['sucursal_id'],producto,unidades,'DEVOLUCION',f'devolucion:{id}')
        return id
