#! python
# -*- coding: utf-8 -*-

from __future__ import print_function

import Tkinter as tkinter, tkFileDialog as filedialog, tkMessageBox as messsagebox
import programa_pedidos_bl as programa_pedidos

def readvalidfile(title=None,error=u"El fichero seleccionado no existe! Por favor, introduzca un arvhivo válido", once=True):
    while True:
        file = filedialog.askopenfilename(title=title)
        v = programa_pedidos.readvalidate(file)
        if v==1:
            print("Error:", error)
        elif v==2: print("Error:",u"Tiene que especificar un archivo!, vuelva a intentarlo escogiendo uno.")
        elif file: return file
        if once: exit(1)


if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()

    unico = readvalidfile(title="Seleccione el fichero único desde su ubicación")
    print(u"Usando fichero único:", unico)

    pendientes = readvalidfile(title="Seleccione el fichero de pedididos pendientes desde su ubicación")
    print(u"Archivo de pedidos pendientes:", pendientes)

    mercurio = readvalidfile(title="Seleccione el fichero mercurio-kardex desde su ubicación")
    print(u"Usando fichero mercurio", mercurio)

    outputext = "xlsx"
    output = filedialog.asksaveasfilename(title="Seleccione la ubicación donde guardar el archivo final (.%s)"%outputext,\
                    filetypes=[('Microsoft Excel 2007', '.%s'%outputext)])

    if not output: print("Error:",u"Tiene que especificar un archivo!, vuelva a intentarlo escogiendo uno.")
    elif not programa_pedidos.wincheckwriteperm(output):
        print("Error:",u"El archivo está bloqueado por otro programa! Vuelva a intentarlo cuando no esté bloqueado.")
    print(u"Archivo salida de los cruces:", output)

    programa_pedidos.processfiles(unico,pendientes,mercurio,output)
