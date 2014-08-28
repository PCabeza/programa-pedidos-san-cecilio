from Tkinter import *
from ttk import *

import sys,os

from lista_compra_gui import ListaCompraFrame
from programa_pedidos_gui import PedidosPendientesFrame
from hospital_gui_common import *

if __name__=='__main__':

    # If using pyinstaller, static assets are in sys._MEIPASS instead of .
    try: base_path= sys._MEIPASS
    except Exception: base_path = os.path.abspath("./compile")

    # define root window and its properties
    v = Tk()
    v.title("Programa de cruces")
    v.resizable(0,0)
    if base_path:
        try: v.iconbitmap(os.path.join(base_path,'icon.ico'))
        except TclError: pass

    #scheduledimage=PhotoImage(...)
    note = Notebook(v)

    listacompratab = ListaCompraFrame(note)
    pedidospendtab = PedidosPendientesFrame(note)

    note.add(listacompratab, text = "Lista de compra")
    note.add(pedidospendtab, text = "Pedidos pendientes")

    note.pack()


    # Actual loop and center widgets
    centrar(v)
    v.mainloop()
