Programa pedidos para el hospital
=================================

Programa para que el servicio de farmacia del hospital San Cecilio de
Granada realice una serie de cruces de manera automatizada a la hora
de realizar pedidos.

Dependencias
------------

El programa depende de los siguientes paquetes:

- xlrd: lectura de archivos xls, xlsx

- xlsxreader: escritura de archivos xlsx

- ttk: widgets avanzados para la interfaz de tkinter, en este caso
  Notebook

Compilar
--------

Usando pyinstaller para compilar todo desde windows, para ello hace
falta instalar pywin32 y el mismo pyinstaller.

Para compilarlo todo se incluye el script compile.py, que se ejecuta
con:

     python compile.py -s cruces
Hay otras opciones que se pueden consultar con ```-h```

Estructura
----------

Hay dos programas que pueden funcionar de forma independiente:

- programa_pedidos
- lista_compra

Ambos tienen un archivo **_bl.py* que contiene el proceso de cruce y un archivo **_frame.py* que contiene la interfaz para usarlo.

Las funciones de lectura, escritura de los archivos .xls y otras funciones comunes están en la librería común *hospital_common.py*.

Para unir los dos programas de cruces en uno solo, la aplicación se ejecuta desde *hospital_gui.py*, que contiene una interfaz unificada.
