"""Demo visual reproducible. Ejecutar: python3 -m distribucion.demo_web --db demo-web.db."""
import argparse
from .db import BaseDatos
from .servicios import Sistema
from .demo import cargar


def cargar_tablero(s):
    cargar(s)
    categoria=s.listar('categoria')[0]['id']
    productos=[]
    for codigo,nombre,precio,costo in [('ARR-01','Arroz largo fino · 1 kg','1850.00','1100.00'),('ACE-01','Aceite de girasol · 900 ml','3200.00','2300.00'),('FIE-01','Fideos secos · 500 g','1400.00','850.00')]:
        p=s.guardar('producto',dict(codigo=codigo,nombre=nombre,categoria_id=categoria,precio=precio,costo=costo))
        s.ingresar_proveedor(1,p,1,250,costo)
        productos.append(p)
    locales=[2]
    for nombre,direccion in [('Local Nueva Córdoba','Obispo Trejo 850'),('Local General Paz','25 de Mayo 1250')]:
        locales.append(s.guardar('sucursal',dict(nombre=nombre,direccion=direccion,tipo='LOCAL')))
    etapas=['PREPARADO','PREPARADO','PRECINTADO','PRECINTADO','EN_TRANSITO','EN_TRANSITO','RECIBIDO','VERIFICADO']
    for i,etapa in enumerate(etapas):
        p=productos[i%len(productos)]
        orden=s.crear_orden(1,locales[i%len(locales)],{p:12+i*2})
        remito=s.crear_remito(orden)
        bulto=s.preparar_bulto(remito,{p:12+i*2},'Lucía Fernández')
        if etapa=='PREPARADO':continue
        s.precintar(bulto,f'AND-{bulto:05d}','Lucía Fernández')
        if etapa=='PRECINTADO':continue
        s.despachar(remito,'Martín Sosa')
        if etapa=='EN_TRANSITO':continue
        s.recibir(bulto,True,'Carolina Díaz')
        if etapa=='RECIBIDO':continue
        s.verificar(bulto,'Carolina Díaz')
    return {'bultos':len(s.listar('bulto')),'locales':len(s.listar('sucursal'))-1}


def main():
    parser=argparse.ArgumentParser(description='Crea una base de demostración del tablero')
    parser.add_argument('--db',default='demo-web.db')
    args=parser.parse_args()
    base=BaseDatos(args.db)
    try:print(cargar_tablero(Sistema(base)))
    finally:base.cerrar()

if __name__=='__main__':main()
