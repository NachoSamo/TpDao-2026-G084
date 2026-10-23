"""Reportes con agregación Decimal: nunca CAST monetario a REAL."""
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

class Reportes:
    def __init__(self,sistema):
        self.s = sistema

    def generar(self,tipo,desde='2000-01-01',hasta='2100-12-31',sucursal=None,top=10):
        inicio,fin = date.fromisoformat(desde),date.fromisoformat(hasta)
        if inicio>fin or top<1:
            raise ValueError('Período o top inválido')
        def incluye(fecha,local):
            return inicio<=date.fromisoformat(fecha[:10])<=fin and (sucursal is None or local==sucursal)
        if tipo=='ventas':
            grupos=defaultdict(lambda: {'cobrado':Decimal('0'),'reintegrado':Decimal('0'),'ventas':set()})
            for c in self.s.dao.todos('SELECT c.*,v.fecha,v.sucursal_id FROM cobro c JOIN venta v ON v.id=c.venta_id'):
                if incluye(c['fecha'],c['sucursal_id']):
                    g=grupos[(c['sucursal_id'],c['medio'])];g['cobrado']+=Decimal(c['monto']);g['ventas'].add(c['venta_id'])
            for d in self.s.dao.todos('SELECT d.*,v.sucursal_id FROM devolucion d JOIN venta v ON v.id=d.venta_id'):
                if incluye(d['fecha'],d['sucursal_id']):
                    grupos[(d['sucursal_id'],d['medio'])]['reintegrado']+=Decimal(d['monto'])
            return [dict(local=k[0],medio=k[1],ventas=len(v['ventas']),cobrado=str(v['cobrado']),reintegrado=str(v['reintegrado']),neto=str(v['cobrado']-v['reintegrado'])) for k,v in sorted(grupos.items())]
        if tipo=='margen':
            grupos=defaultdict(lambda: [0,Decimal('0'),Decimal('0')])
            for d in self.s.dao.todos('SELECT d.*,v.fecha,v.sucursal_id,p.nombre FROM detalle_venta d JOIN venta v ON v.id=d.venta_id JOIN producto p ON p.id=d.producto_id'):
                if incluye(d['fecha'],d['sucursal_id']):
                    g=grupos[(d['producto_id'],d['nombre'])];g[0]+=d['cantidad'];g[1]+=Decimal(d['precio'])*d['cantidad'];g[2]+=(Decimal(d['precio'])-Decimal(d['costo']))*d['cantidad']
            for d in self.s.dao.todos('SELECT d.*,v.sucursal_id,dv.precio,dv.costo,p.nombre FROM devolucion d JOIN venta v ON v.id=d.venta_id JOIN detalle_venta dv ON dv.venta_id=d.venta_id AND dv.producto_id=d.producto_id JOIN producto p ON p.id=d.producto_id'):
                if incluye(d['fecha'],d['sucursal_id']):
                    g=grupos[(d['producto_id'],d['nombre'])];g[0]-=d['cantidad'];g[1]-=Decimal(d['monto']);g[2]-=(Decimal(d['precio'])-Decimal(d['costo']))*d['cantidad']
            return [dict(producto=k[0],nombre=k[1],unidades_netas=v[0],ingresos_netos=str(v[1]),margen=str(v[2])) for k,v in sorted(grupos.items(),key=lambda x:(-x[1][0],x[0][0]))[:top]]
        if tipo=='rechazos':
            filas=self.s.dao.todos("SELECT b.id,b.motivo,o.destino_id,h.fecha,SUM(d.cantidad) unidades FROM bulto b JOIN remito r ON r.id=b.remito_id JOIN orden o ON o.id=r.orden_id JOIN historial h ON h.bulto_id=b.id AND h.nuevo='RECHAZADO' JOIN detalle_bulto d ON d.bulto_id=b.id GROUP BY b.id")
            return [dict(bulto=f['id'],destino=f['destino_id'],fecha=f['fecha'],unidades=f['unidades'],motivo=f['motivo'],merma='NO DETERMINADA') for f in filas if incluye(f['fecha'],f['destino_id'])]
        if tipo=='transito':
            grupos=defaultdict(list)
            filas=self.s.dao.todos("SELECT b.id,o.destino_id,s.fecha salida,l.fecha llegada FROM bulto b JOIN remito r ON r.id=b.remito_id JOIN orden o ON o.id=r.orden_id JOIN historial s ON s.bulto_id=b.id AND s.nuevo='EN_TRANSITO' JOIN historial l ON l.bulto_id=b.id AND l.nuevo='RECIBIDO'")
            for f in filas:
                if incluye(f['llegada'],f['destino_id']):
                    delta=datetime.fromisoformat(f['llegada'])-datetime.fromisoformat(f['salida'])
                    micros=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
                    grupos[f['destino_id']].append(Decimal(micros)/Decimal('3600000000'))
            return [dict(destino=k,bultos=len(v),promedio_horas=str((sum(v)/len(v)).quantize(Decimal('.000001'))),maximo_horas=str(max(v).quantize(Decimal('.000001')))) for k,v in sorted(grupos.items())]
        raise ValueError('Reporte desconocido')
