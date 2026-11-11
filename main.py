"""Ejecutar: python3 main.py --demo --db demo.db."""
import argparse
from distribucion.db import BaseDatos
from distribucion.servicios import Sistema
from distribucion.demo import cargar


def main():
    parser=argparse.ArgumentParser(description='TP DAO G084')
    parser.add_argument('--db',default='distribucion.db',help='Archivo SQLite (se crea si no existe)')
    parser.add_argument('--demo',action='store_true',help='Cargar datos demo en base vacía')
    parser.add_argument('--sin-ui',action='store_true',help='Inicializar/cargar sin ventana')
    parser.add_argument('--web',action='store_true',help='Abrir servidor web local')
    parser.add_argument('--port',type=int,default=8080,help='Puerto web local (8080 por defecto)')
    args=parser.parse_args()
    if args.web and args.db == ':memory:':
        parser.error('--web requiere un archivo de base de datos')
    base=BaseDatos(args.db)
    try:
        sistema=Sistema(base)
        if args.demo:print('Demo:',cargar(sistema))
        if args.web:
            base.cerrar()
            from distribucion.web import servir
            servir(args.db,args.port)
        elif not args.sin_ui:
            try:
                import tkinter as tk
                from distribucion.ui import Aplicacion
                try:
                    root=tk.Tk()
                except tk.TclError as error:
                    raise SystemExit(f'No se pudo iniciar Tcl/Tk: {error}. Probá un Python con Tk operativo o --sin-ui.') from error
                Aplicacion(root,sistema);root.mainloop()
            except ImportError as error:
                raise SystemExit('Este Python no incluye Tkinter. Instalá Python de python.org con Tcl/Tk o usá --sin-ui.') from error
    finally:
        base.cerrar()

if __name__=='__main__':main()
