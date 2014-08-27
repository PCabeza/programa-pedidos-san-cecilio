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

# TODO: improve width system
def writecrossxls(output,c,log=print):
    money_format=u'0.00 €'
    colstyle = {
        "precio final envase": {"num_format": money_format},
        "coste/ud con iva": {"num_format": money_format},
        "coste/linea": {"num_format": money_format},
    }

    formula_cells = {
        "coste/linea": {
            "formula": "={0}*{1}",
            "parameters": ["cantidad_a_pedir","coste/ud_con_iva"],
            "valor": lambda n0,n1: n0*n1,
        },
        "cantidad_a_pedir": {
            "formula": "=ROUNDUP({0}/{1},0)*{1}",
            "parameters": ["cant.","unidades/caja"],
            "valor": lambda n0,n1: ceil(n0/n1)*n1,
        }
    }

    common.writecxlsfromsqlite(output,c,colstyle=colstyle,formula_cells=formula_cells,log=log)


def processfiles(unico,pendientes,mercurio,output,log=print,outputext="xlsx"):
    '''Main process of reading files and writing the output'''
    temp = tempfile.mkstemp()
    log("INFO",u"Creando archivo sqlite temporal:",temp[1])
    conn = sqlite3.connect(temp[1])

    # Process both xls files, if any error happens capture exception and add xls file
    log("INFO",u"Leyendo %s..." % unico)
    try: common.xls2sqlite(unico,conn,table="fichero_unico")
    except Exception as e:
        setattr(e,"file",u"fichero único")
        raise

    log("INFO",u"Leyendo %s..." % pendientes)
    try: common.xls2sqlite(pendientes,conn,table="pedidos_pendientes")
    except Exception as e:
        setattr(e,"file",u"pedidos pendientes")
        raise

    # Generate schema information for mercurio file
    groups = ['Grupo','Sistemas']
    headers = [u"Código",u"Artículo",u"Almacén Rep.",u"Ubic.Ext",u"Unidad.Ext",u"Stk.Min",u"Stk.Max",u"Rep.Fija",u"Stk.Act",u"Cant."]
    htypes  = ['TEXT'   , 'TEXT'    , 'TEXT'        , 'TEXT'    , 'REAL'       , 'REAL'  , 'REAL'   , 'REAL'    , 'REAL'    ,'INT'  ]

    log("INFO",u"Leyendo %s..." % mercurio)
    common.parseCustomFile(mercurio,groups,headers,htypes,conn,basetable="fichero_mercurio")

    query = '''
        SELECT código,artículo,"stk.min","stk.max","stk.act","cant.",
               CAST(NULL AS REAL) as cantidad_a_pedir,
               CAST(NULL AS REAL) as "coste/linea",

               fichero_unico.observaciones,generico_de_centro,codigo_nacional,especialidad_farmaceutica,
               "unidades/caja",precio_final_envase,"coste/ud_con_iva",laboratorio

        FROM
            (fichero_unico INNER JOIN fichero_mercurio_data ON codigo_articulo_hsc="código")
                LEFT JOIN
            pedidos_pendientes
            ON gc=generico_de_centro
        WHERE pedidos_pendientes.primary_id IS NULL
        ORDER BY laboratorio, "artículo"
    '''

    log("INFO",u"Obteniendo cruces de los archivos...")
    c = conn.execute(query)


    log("INFO",u"Escribiendo el archivo %s..." % output)
    writecrossxls(output,c,log=log)

    # some cleanup
    log("INFO",u"Eliminando archivos temporales...")
    conn.close()
    os.close(temp[0])
    os.unlink(temp[1])
