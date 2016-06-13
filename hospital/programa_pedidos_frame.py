# -*- coding: utf-8 -*-
'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza
license: modified BSD

Frame for programa pedidos
'''

from __future__ import print_function

from Tkinter import *
import tkFileDialog
import tkMessageBox
from idlelib.WidgetRedirector import WidgetRedirector

import sys
import os
import traceback

import hospital.programa_pedidos_bl as programa_pedidos
import hospital.hospital_common as common
from .hospital_gui_common import *


class ReadOnlyEntry(Entry):

    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
            "insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register(
            "delete", lambda *args, **kw: "break")


class FileFrame(object):

    def __init__(self, parent, text, row=0, dtitle=None, filetypes=[], validation=None):
        # Frame.__init__(self,parent)
        # self.grid()

        self.parent = parent
        self.dialogtitle = dtitle
        self.filetypes = filetypes
        self.validation = validation

        self.file = StringVar()
        self.label = Label(parent, text=text + ":")
        self.fileentry = ReadOnlyEntry(
            parent, textvariable=self.file, width=40)
        self.button = Button(parent, text="Examinar",
                             command=lambda s=self: s.selectfile())

        self.label.grid(row=row, column=0, sticky='E', padx=10)
        self.fileentry.grid(row=row, column=1)
        self.button.grid(row=row, column=2, padx=5)

    def selectfile(self):
        filename = tkFileDialog.askopenfilename(
            title=self.dialogtitle, filetypes=self.filetypes)
        valid = 0
        if self.validation:
            valid = self.validation.validate(filename)

        if valid == 0:
            self.file.set(filename)
        else:
            self.validation.error()


def calcCommand(unico, pendientes, mercurio, log):
    '''Callback for the "cross files" button that validates files and process them'''

    unico = unico.file.get()
    pendientes = pendientes.file.get()
    mercurio = mercurio.file.get()

    # Some file validation
    if not unico:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione un fichero único!")

    elif not pendientes:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione un fichero de pedidos pendientes!")

    elif not mercurio:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione un fichero mercurio!")

    elif 0 != common.readvalidate(unico):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer el fichero único! Pruebe con otro archivo.")

    elif 0 != common.readvalidate(pendientes):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer el archivo de pedidos pendientes! Pruebe con otro archivo.")

    elif 0 != common.readvalidate(mercurio):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer el fichero mercurio! Pruebe con otro archivo.")

    # if all files are valid, procede
    else:
        # read destination of output
        tkMessageBox.showinfo(
            u'Fichero de cruces', u'Escoja la ubicación donde escribir el fichero de cruces.')

        outputext = "xlsx"
        output = None
        output = tkFileDialog.asksaveasfilename(title="Seleccione la ubicación donde guardar el archivo final (.%s)" % outputext,
                                                filetypes=[('Microsoft Excel 2007', '.%s' % outputext)])

        if not output:
            tkMessageBox.showerror(
                "Error", u"Tiene que especificar un archivo!, vuelva a intentarlo escogiendo uno.")
        elif not common.wincheckwriteperm(output):
            tkMessageBox.showerror(
                "Error", u"El archivo está bloqueado por otro programa! Vuelva a intentarlo cuando no esté bloqueado.")
        else:

            try:
                programa_pedidos.processfiles(
                    unico, pendientes, mercurio, output, log=lambda *args: log(*args))
            except Exception as e:
                if os.isatty(sys.stdin.fileno()):
                    traceback.print_exc()
                err = str(e).decode('utf-8')
                log("ERROR", err)

                functionmap = {
                    'writecrossxls': u"Error al escribir el archivo de cruce",
                    'parseCustomFile': u'Error al leer el archivo mercurio',
                    'xls2sqlite': lambda e: u'Error al leer el archivo %s' % e.file
                }

                tb = sys.exc_info()[2]
                errmsg = u'Se produjo un error al procesar los archivos'
                for t in traceback.extract_tb(tb):
                    if t[2] in functionmap:
                        r = functionmap[t[2]]
                        if hasattr(r, "__call__"):
                            errmsg = r(e)
                        else:
                            errmsg = r

                tkMessageBox.showerror(
                    u"Fallo al procesar", errmsg + u'\n\nMensaje de error: %s' % err)
                return

            msg_exito = u'Proceso de cruce finalizado con éxito!'
            tkMessageBox.showinfo('Proceso finalizado', msg_exito)
            log(msg_exito)


class PedidosPendientesFrame(Frame):

    def __init__(self, *args, **kwargs):
        log = kwargs.pop('log')
        Frame.__init__(self, *args, **kwargs)

        self.grid()

        # set an offset of rows to show file inmputs
        brow = 1
        for i in range(brow):
            self.grid_rowconfigure(i, weight=0, minsize=25)

        # show actual file inputs widgets
        unico = FileFrame(self, u"Fichero único",
                          dtitle=u"Seleccione el fichero único", row=brow)
        pendientes = FileFrame(self, u"Pedidos pendientes",
                               dtitle=u"Seleccione el fichero de pedidos pendientes", row=brow + 1)
        mercurio = FileFrame(self, u"Fichero mercurio",
                             dtitle=u"Seleccione el fichero mercurio", row=brow + 2)

        # configure input widgets rows
        for i in range(3):
            self.grid_rowconfigure(brow + i, weight=0, pad=5)

        # Console log widget to show feedback to the user
        # text = ReadOnlyText(self, height=11)
        # text.grid(row=0, column=4, rowspan=5, padx=20, pady=10)

        # Configure "cross files" button with callback
        calcular = Button(self, text=u"Cruzar archivos",
                          command=lambda u=unico, p=pendientes, m=mercurio, log=log: calcCommand(u, p, m, log))
        calcular.grid(row=brow + 3, column=0, columnspan=3, sticky='E')
        self.grid_rowconfigure(brow + 3, weight=1)


if __name__ == "__main__":

    # If using pyinstaller, static assets are in sys._MEIPASS instead of .
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./compile")

    # define root window and its properties
    v = Tk()
    v.title("Programa de cruces")
    v.resizable(0, 0)
    if base_path:
        try:
            v.iconbitmap(os.path.join(base_path, 'icon.ico'))
        except TclError:
            pass

    mainframe = PedidosPendientesFrame(v)
    mainframe.pack()

    # Actual loop and center widgets
    centrar(v)
    v.mainloop()
