'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza
license: modified BSD

Common utilities for the graphic interface
'''

from Tkinter import END, Text
from idlelib.WidgetRedirector import WidgetRedirector


def centrar(ventana):
    "Centra la ventana"
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    extraW = ventana.winfo_screenwidth() - w
    extraH = ventana.winfo_screenheight() - h
    ventana.geometry("%dx%d%+d%+d" % (w, h, extraW / 2, extraH / 2))


def textwidgetlog(level, *args, **kwargs):
    '''
    Log the elements in *args to a Text element passed a parameter

    :kwarg "text": The Text widget
    '''
    text = kwargs.get('text')
    if level == "ERROR":
        text.insert(END, "ERROR: " + ' '.join(args) + '\n')
    else:
        text.insert(END, ' '.join(args) + '\n')
    text.master.update_idletasks()


class ReadOnlyText(Text):

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
            "insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register(
            "delete", lambda *args, **kw: "break")
