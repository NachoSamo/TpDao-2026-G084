"""Interfaz ttk: formularios por caso de uso, tablas y reportes exportables."""
import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .reportes import Reportes


def items(texto):
    resultado={}
    for par in texto.split(','):
        p,q=par.strip().split(':');p,q=int(p),int(q)
        if p in resultado:
            raise ValueError('Producto repetido en los ítems')
        resultado[p]=q
    return resultado


def pagos(texto):
    resultado={}
    for par in texto.split(','):
        medio,monto=par.strip().split(':')
        medio=medio.upper()
        if medio in resultado:
            raise ValueError('Medio de pago repetido')
        resultado[medio]=monto.strip()
    return resultado


class Aplicacion(ttk.Frame):
    def __init__(self,root,sistema):
        super().__init__(root,padding=12);self.pack(fill='both',expand=True)
        self.s=sistema;self.root=root
        root.title('G084 · Distribución y locales');root.geometry('1120x780')
        ttk.Label(self,text='Centro de distribución → locales',font=('',19,'bold')).pack(anchor='w')
        ttk.Label(self,text='Usá los ID de las tablas. Cantidades enteras · dinero con punto decimal · ítems: producto:cantidad,producto:cantidad').pack(anchor='w',pady=(4,12))
        tabs=ttk.Notebook(self);tabs.pack(fill='both',expand=True)
        for nombre,constructor in [('Catálogo',self.catalogo),('Inventario',self.inventario),('Logística',self.logistica),('Ventas',self.ventas),('Consultas y reportes',self.consultas)]:
            frame=ttk.Frame(tabs,padding=10);tabs.add(frame,text=nombre);constructor(frame)
        self.estado=tk.StringVar(value='Listo. Los cambios se guardan por operación completa.')
        ttk.Label(self,textvariable=self.estado).pack(anchor='w',pady=(8,0))

    def ejecutar(self,fn):
        try:
            resultado=fn();self.estado.set(f'Operación confirmada. Resultado: {resultado if resultado is not None else "OK"}')
            messagebox.showinfo('Confirmado',self.estado.get())
        except (ValueError,sqlite3.Error,KeyError) as error:
            self.estado.set(str(error));messagebox.showerror('No se pudo confirmar',str(error))

    def formulario(self,padre,titulo,campos,accion):
        marco=ttk.LabelFrame(padre,text=titulo,padding=8);marco.pack(fill='x',pady=5)
        variables={}
        for i,(nombre,defecto) in enumerate(campos):
            ttk.Label(marco,text=nombre).grid(row=i//3*2,column=i%3,sticky='w',padx=5)
            var=tk.StringVar(value=defecto);variables[nombre]=var
            ttk.Entry(marco,textvariable=var,width=32).grid(row=i//3*2+1,column=i%3,sticky='ew',padx=5,pady=(0,5))
        ttk.Button(marco,text='Confirmar',command=lambda:self.ejecutar(lambda:accion({k:v.get().strip() for k,v in variables.items()}))).grid(row=(len(campos)+2)//3*2,column=0,sticky='w',padx=5)
        for i in range(3):marco.columnconfigure(i,weight=1)

    def catalogo(self,f):
        ttk.Label(f,text='Alta o modificación: ID vacío crea; ID existente modifica. Baja conserva el historial.').pack(anchor='w')
        self.formulario(f,'Sucursal',[('ID',''),('nombre',''),('direccion',''),('tipo','LOCAL')],lambda d:self.s.guardar('sucursal',{k:d[k] for k in ('nombre','direccion','tipo')},int(d['ID']) if d['ID'] else None))
        self.formulario(f,'Categoría / proveedor',[('entidad','categoria'),('ID',''),('nombre',''),('cuit','')],lambda d:self.s.guardar(d['entidad'],dict(nombre=d['nombre'],**({'cuit':d['cuit']} if d['entidad']=='proveedor' else {})),int(d['ID']) if d['ID'] else None))
        self.formulario(f,'Producto',[('ID',''),('codigo',''),('nombre',''),('categoria_id','1'),('precio','0.00'),('costo','0.00')],lambda d:self.s.guardar('producto',dict(codigo=d['codigo'],nombre=d['nombre'],categoria_id=int(d['categoria_id']),precio=d['precio'],costo=d['costo']),int(d['ID']) if d['ID'] else None))
        self.formulario(f,'Baja lógica',[('entidad','producto'),('ID','')],lambda d:self.s.baja(d['entidad'],int(d['ID'])))

    def inventario(self,f):
        self.formulario(f,'Proveedor del producto',[('producto','1'),('proveedor','1'),('costo','0.00'),('principal (si/no)','si')],lambda d:self.s.asociar_proveedor(int(d['producto']),int(d['proveedor']),d['costo'],self.booleano(d['principal (si/no)'])))
        self.formulario(f,'Ingreso de proveedor al CD',[('CD','1'),('producto','1'),('proveedor','1'),('cantidad','1'),('costo','0.00')],lambda d:self.s.ingresar_proveedor(int(d['CD']),int(d['producto']),int(d['proveedor']),int(d['cantidad']),d['costo']))
        self.formulario(f,'Mínimo de stock y aviso Observer',[('sucursal','2'),('producto','1'),('minimo','5')],lambda d:self.s.definir_minimo(int(d['sucursal']),int(d['producto']),int(d['minimo'])))
        ttk.Label(f,text='El stock local se incorpora verificando bultos. No se modifica manualmente.\nAl quedar bajo mínimo, Observer registra un aviso y consolida el faltante descontando pedidos pendientes.').pack(anchor='w',pady=15)

    @staticmethod
    def booleano(texto):
        if texto.lower() not in ('si','sí','no'):raise ValueError('Ingresá si o no')
        return texto.lower()!='no'

    def logistica(self,f):
        self.formulario(f,'Orden CD → local',[('origen','1'),('destino','2'),('items','1:10')],lambda d:self.s.crear_orden(int(d['origen']),int(d['destino']),items(d['items'])))
        self.formulario(f,'Crear remito',[('orden','1')],lambda d:self.s.crear_remito(int(d['orden'])))
        self.formulario(f,'Preparar bulto y reservar stock',[('remito','1'),('items','1:10'),('responsable','Operario')],lambda d:self.s.preparar_bulto(int(d['remito']),items(d['items']),d['responsable']))
        self.formulario(f,'Precintar / despachar / recibir / verificar',[('accion','precintar'),('ID bulto o remito','1'),('responsable','Operario'),('precinto','PREC-001'),('integro (si/no)','si'),('motivo rechazo','')],self.accion_logistica)
        ttk.Label(f,text='Para despachar usá el ID de remito; las otras acciones usan ID de bulto.\nPreparado → Precintado → En tránsito → Recibido → Verificado / Rechazado.').pack(anchor='w')

    def accion_logistica(self,d):
        id=int(d['ID bulto o remito']);r=d['responsable'];a=d['accion']
        if a=='precintar':return self.s.precintar(id,d['precinto'],r)
        if a=='despachar':return self.s.despachar(id,r)
        if a=='recibir':return self.s.recibir(id,self.booleano(d['integro (si/no)']),r)
        if a=='verificar':return self.s.verificar(id,r,d['motivo rechazo'])
        raise ValueError('Acción inválida')

    def ventas(self,f):
        self.formulario(f,'Venta y comprobante',[('sucursal','2'),('items','1:1'),('pagos','EFECTIVO:2500.50')],lambda d:self.s.vender(int(d['sucursal']),items(d['items']),pagos(d['pagos'])))
        ttk.Label(f,text='Pagos: EFECTIVO, DEBITO, CREDITO o TRANSFERENCIA. Ejemplo: EFECTIVO:1000.00,DEBITO:1500.50\nConsultá producto para el precio y venta para el comprobante V-XXXXXXXX.').pack(anchor='w',pady=8)
        self.formulario(f,'Devolución y reintegro',[('venta','1'),('producto','1'),('cantidad','1'),('apto (si/no)','si'),('medio','EFECTIVO')],lambda d:self.s.devolver(int(d['venta']),int(d['producto']),int(d['cantidad']),self.booleano(d['apto (si/no)']),d['medio']))

    def consultas(self,f):
        barra=ttk.Frame(f);barra.pack(fill='x')
        self.tabla=tk.StringVar(value='stock')
        ttk.Combobox(barra,textvariable=self.tabla,values=sorted(['sucursal','categoria','proveedor','producto','producto_proveedor','stock','movimiento','ingreso','orden','detalle_orden','remito','bulto','detalle_bulto','historial','venta','detalle_venta','cobro','devolucion','aviso']),state='readonly').pack(side='left')
        ttk.Button(barra,text='Consultar tabla',command=lambda:self.ejecutar(lambda:self.mostrar(self.s.listar(self.tabla.get())))).pack(side='left',padx=5)
        ttk.Button(barra,text='Exportar CSV',command=self.exportar).pack(side='right')
        self.formulario(f,'Reporte',[('tipo','ventas'),('desde','2000-01-01'),('hasta','2100-12-31'),('sucursal (opcional)',''),('top','10')],lambda d:self.mostrar(Reportes(self.s).generar(d['tipo'],d['desde'],d['hasta'],int(d['sucursal (opcional)']) if d['sucursal (opcional)'] else None,int(d['top']))))
        ttk.Label(f,text='Tipos: ventas · margen · rechazos · transito. Fechas UTC inclusive, formato AAAA-MM-DD.').pack(anchor='w')
        cont=ttk.Frame(f);cont.pack(fill='both',expand=True,pady=10)
        self.tree=ttk.Treeview(cont,show='headings');self.tree.grid(row=0,column=0,sticky='nsew')
        sy=ttk.Scrollbar(cont,orient='vertical',command=self.tree.yview);sy.grid(row=0,column=1,sticky='ns')
        sx=ttk.Scrollbar(cont,orient='horizontal',command=self.tree.xview);sx.grid(row=1,column=0,sticky='ew')
        self.tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);cont.rowconfigure(0,weight=1);cont.columnconfigure(0,weight=1)
        self.filas=[]

    def mostrar(self,filas):
        self.filas=filas;self.tree.delete(*self.tree.get_children())
        columnas=list(filas[0]) if filas else ['resultado']
        self.tree['columns']=columnas
        for c in columnas:self.tree.heading(c,text=c);self.tree.column(c,width=140,stretch=False)
        for f in filas:self.tree.insert('', 'end',values=list(f.values()))
        return f'{len(filas)} filas'

    def exportar(self):
        if not self.filas:return messagebox.showinfo('CSV','Consultá datos primero')
        ruta=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if ruta:
            with open(ruta,'w',encoding='utf-8-sig',newline='') as archivo:
                w=csv.DictWriter(archivo,fieldnames=list(self.filas[0]));w.writeheader();w.writerows(self.filas)
            self.estado.set(f'CSV exportado: {ruta}')
