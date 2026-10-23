"""Prueba manual de construcción ttk (requiere Tk y sesión gráfica).
Ejecutar: python3 -m tests.smoke_ui
"""
import tkinter as tk
from distribucion.db import BaseDatos
from distribucion.servicios import Sistema
from distribucion.demo import cargar
from distribucion.ui import Aplicacion
from distribucion.reportes import Reportes


def main():
    base=BaseDatos(':memory:')
    root=None
    try:
        sistema=Sistema(base);cargar(sistema)
        root=tk.Tk();root.withdraw()
        app=Aplicacion(root,sistema);root.update_idletasks()
        for tabla in ('stock','bulto','historial','venta'):
            app.mostrar(sistema.listar(tabla));root.update_idletasks()
        for tipo in ('ventas','margen','rechazos','transito'):
            app.mostrar(Reportes(sistema).generar(tipo));root.update_idletasks()
        print('UI smoke OK: formularios, tablas y cuatro reportes')
    finally:
        if root is not None:root.destroy()
        base.cerrar()

if __name__=='__main__':main()
