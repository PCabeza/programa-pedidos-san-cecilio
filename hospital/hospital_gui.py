'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza
license: modified BSD
'''
from Tkinter import *
from ttk import *

import sys
import os

from .lista_compra_frame import ListaCompraFrame
from .programa_pedidos_frame import PedidosPendientesFrame
from .hospital_gui_common import *

from pkgutil import get_data
from PIL import Image as PILImage, ImageTk
from StringIO import StringIO


def main():

    # define root window and its properties
    v = Tk()
    v.title("Programa de cruces")
    v.resizable(0, 0)

    icon = PILImage.open(StringIO(get_data("hospital", "data/icon.ico")))
    icontk = ImageTk.PhotoImage(icon)
    v.tk.call("wm", "iconphoto", v._w, icontk)

    # create notebook widget
    note = Notebook(v)

    # Create and add both frames
    listacompratab = ListaCompraFrame(note)
    pedidospendtab = PedidosPendientesFrame(note)

    note.add(listacompratab, text="Lista de compra")
    note.add(pedidospendtab, text="Pedidos pendientes")

    note.pack()  # the the notebook widget

    # Actual loop and center widgets
    centrar(v)
    v.mainloop()


if __name__ == '__main__': main()
