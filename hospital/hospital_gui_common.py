'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza
license: modified BSD

Common utilities for the graphic interface
'''

import tkFileDialog
from Tkinter import *
from idlelib.WidgetRedirector import WidgetRedirector

import os


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


class ReadOnlyEntry(Entry):

    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
            "insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register(
            "delete", lambda *args, **kw: "break")


class FileFrame(object):

    def __init__(self, parent, text, row=0, dtitle=None, filetypes=[],
                defaultextension="", validation=None):

        self.parent = parent
        self.dialogtitle = dtitle
        self.filetypes = filetypes
        self.defaultextension = defaultextension
        self.validation = validation

        self.file = StringVar()
        self.label = Label(parent, text=text + ":")

        self.fileentry = ReadOnlyEntry(
            parent, textvariable=self.file, width=50)
        # TODO check why on notebook tab change, it gets focus
        # self.fileentry.bind("<FocusIn>", self._filenetry_focus)
        self.fileentry.bind("<Button-1>", self._filenetry_focus)

        self.button = Button(parent, text="Examinar",
                             command=lambda s=self: s.selectfile())

        self.label.grid(row=row, column=0, sticky='E', padx=(20, 10))
        self.fileentry.grid(row=row, column=1)
        self.button.grid(row=row, column=2, padx=7)

    def _filenetry_focus(self, event):
        # if you click the entry and it is not already focused
        if self.parent.focus_get() != self.fileentry:
            self.selectfile()

    def selectfile(self):
        fargs = {
            "title": self.dialogtitle,
            "filetypes": self.filetypes,
            "defaultextension": self.defaultextension,
        }

        path, base = os.path.split(self.file.get())
        filename = tkFileDialog.askopenfilename(
            initialdir=path,
            initialfile=base,
            **fargs
        )

        valid = 0
        if self.validation:
            valid = self.validation.validate(filename)

        if valid != 0:
            self.validation.error()
        elif filename:
            self.file.set(filename)
            self.fileentry.xview(END)
