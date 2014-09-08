'''
Common utilities for the graphic interface
'''

from Tkinter import END

def centrar(ventana):
    "Centra la ventana"
    ventana.update_idletasks()
    w=ventana.winfo_width()
    h=ventana.winfo_height()
    extraW=ventana.winfo_screenwidth()-w
    extraH=ventana.winfo_screenheight()-h
    ventana.geometry("%dx%d%+d%+d" % (w,h,extraW/2,extraH/2))

def textwidgetlog(level,*args, **kwargs):
    '''
    Log the elements in *args to a Text element passed a parameter

    :kwarg "text": The Text widget
    '''
    text = kwargs.get('text')
    if level=="ERROR":
        text.insert(END,"ERROR: "+' '.join(args)+'\n')
    else: text.insert(END,' '.join(args)+'\n')
    text.master.update_idletasks()
