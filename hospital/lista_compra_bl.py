# -*- coding: utf-8 -*-
from __future__ import print_function # use print as a function

# depends on packages: xlrd xlswriter and optionally chardet
import xlrd, xlsxwriter as xlsxw # read and write xls(x) files

import sqlite3, datetime, re, tempfile, os, sys, codecs
from os import path
from math import ceil

import programa_pedidos_common as common

#################################
# Actual main processing of files
#################################

def processfiles(unico,pendientes,output,log=print,outputext="xlsx"):
    '''Main process of reading files and writing the output'''
    temp = tempfile.mkstemp()
    log("INFO",u"Creando archivo sqlite temporal:",temp[1])
    conn = sqlite3.connect(temp[1])

    # Process both xls files, if any error happens capture exception and add xls file
    log("INFO",u"Leyendo %s..." % unico)
    try: common.xls2sqlite(unico,conn,table="lista_de_compra")
    except Exception as e:
        setattr(e,"file",u"fichero único")
        raise
    
    log("INFO",u"Leyendo %s..." % pendientes)
    try: common.xls2sqlite(pendientes,conn,table="pedidos_pendientes")
    except Exception as e:
        setattr(e,"file",u"pedidos pendientes")
        raise

    query = '''
        SELECT DISTINCT cod_nac, compute_0017, cod_ec

        FROM lista_de_compra LEFT JOIN pedidos_pendientes
            ON pedidos_pendientes.GC=lista_de_compra.cod_ec
                and
                pedidos_pendientes.referencia_fabricante=lista_de_compra.cod_nac
        WHERE pedidos_pendientes.primary_id IS NULL
    '''

    log("INFO",u"Obteniendo cruces de los archivos...")
    c = conn.execute(query)


    log("INFO",u"Escribiendo el archivo %s..." % output)
    common.writecxlsfromsqlite(output,c,log=log)
    
    # some cleanup
    log("INFO",u"Eliminando archivos temporales...")
    conn.close()
    os.close(temp[0])
    os.unlink(temp[1])
