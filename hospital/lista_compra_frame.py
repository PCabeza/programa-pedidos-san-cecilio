# -*- coding: utf-8 -*-
'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza
license: modified BSD

Frame for lista de compra
'''

from __future__ import print_function

from Tkinter import *
import tkFileDialog
import tkMessageBox
from idlelib.WidgetRedirector import WidgetRedirector

import sys
import os
import traceback

import hospital.lista_compra_bl as programa_pedidos
import hospital.hospital_common as common
from .hospital_gui_common import *


def calcCommand(listacompra, unico, pendientes, log):
    '''Callback for the "cross files" button that validates files and process them'''

    listacompra = listacompra.file.get()
    pendientes = pendientes.file.get()
    unico = unico.file.get()

    # Some file validation
    if not listacompra:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione lista de compra!")

    elif not unico:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione el fichero único!")

    elif not pendientes:
        tkMessageBox.showerror(u"No se encontró fichero",
                               u"Seleccione un fichero de pedidos pendientes!")

    elif 0 != common.readvalidate(listacompra):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer la lista de compra! Pruebe con otro archivo.")

    elif 0 != common.readvalidate(unico):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer el fichero único! Pruebe con otro archivo.")

    elif 0 != common.readvalidate(pendientes):
        tkMessageBox.showerror(
            u"Problema de lectura", u"No se puede leer el archivo de pedidos pendientes! Pruebe con otro archivo.")

    # if all files are valid, procede
    else:
        # read destination of output
        tkMessageBox.showinfo(
            u'Fichero de cruces', u'Escoja la ubicación donde escribir el fichero de cruces.')

        outputext = "xlsx"
        output = None
        output = tkFileDialog.asksaveasfilename(title="Seleccione la ubicación donde guardar el archivo final (.%s)" % outputext,
                                                filetypes=[('Microsoft Excel 2007', '.%s' % outputext)],
                                                defaultextension=outputext)

        if not output:
            tkMessageBox.showerror(
                "Error", u"Tiene que especificar un archivo!, vuelva a intentarlo escogiendo uno.")
        elif not common.wincheckwriteperm(output):
            tkMessageBox.showerror(
                "Error", u"El archivo está bloqueado por otro programa! Vuelva a intentarlo cuando no esté bloqueado.")
        else:
            try:
                programa_pedidos.processfiles(
                    unico, pendientes, listacompra, output, log=lambda *args: log(*args))
            except Exception as e:
                if os.isatty(sys.stdin.fileno()):
                    traceback.print_exc()  # print traceback on console
                err = str(e).decode('utf-8')
                log("ERROR", err)

                functionmap = {
                    'writecrossxls': u"Error al escribir el archivo de cruce",
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
            log("INFO", msg_exito)


class ListaCompraFrame(Frame):

    def __init__(self, *args, **kwargs):
        log = kwargs.pop('log')
        Frame.__init__(self, *args, **kwargs)

        # set an offset of rows to show file inmputs
        brow = 1
        count = 3
        for i in range(brow):
            self.grid_rowconfigure(i, weight=0, minsize=25)

        filetypes = [
            ('Microsoft Excel 97-2003', '.xls'),
            ('Microsoft Excel 2007', '.xlsx'),
            ('Todos', '*'),
        ]

        # show actual file inputs widgets
        unico = FileFrame(self, u"Fichero único",
                          dtitle=u"Seleccione el fichero único", row=brow,
                          filetypes=filetypes)
        pendientes = FileFrame(self, u"Pedidos pendientes",
                               dtitle=u"Seleccione el fichero de pedidos pendientes", row=brow + 1,
                               filetypes=filetypes)
        listacompra = FileFrame(
            self, u"Lista compra", dtitle=u"Seleccione el fichero lista de compra", row=brow + 2,
            filetypes=filetypes)

        # configure input widgets rows
        for i in range(count):
            self.grid_rowconfigure(brow + i, weight=0, pad=7)

        # Configure "cross files" button with callback
        calcular = Button(self, text=u"Cruzar archivos",
                          command=lambda l=listacompra, u=unico, p=pendientes, log=log: calcCommand(l, u, p, log))
        calcular.grid(row=brow + 3, column=0, columnspan=3, sticky='E',
                      padx=7, pady=(0, 7))
        self.grid_rowconfigure(brow + 3, weight=1)
