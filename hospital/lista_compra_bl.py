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
    '''Write the final result file from a db cursor'''

    workbook = xlsxw.Workbook(output)
    worksheet = workbook.add_worksheet('Sheet 1')

    # header style
    hstyle = workbook.add_format({'bold': True, 'bg_color': 'gray'})

    # get, prepare  and write header row
    description = [i[0] for i in c.description]
    headers=[ i.replace("_"," ").decode('utf8') for i in description]
    for i,v in enumerate(headers):
        worksheet.write(0,i,v,hstyle)
    worksheet.freeze_panes(1, 0) # freeze first row and no column


    # Extra information of column style and formula cells
    money_format = u"0.00 €"
    colstyle = {}
    #     "precio final envase": {"num_format": money_format},
    #     "coste/ud con iva": {"num_format": money_format},
    #     "coste/linea": {"num_format": money_format},
    # }

    formula_cells = {}
    #     "coste/linea": {
    #         "formula": "={0}*{1}",
    #         "parameters": ["cantidad_a_pedir","coste/ud_con_iva"],
    #         "valor": lambda n0,n1: n0*n1,
    #     },
    #     "cantidad_a_pedir": {
    #         "formula": "=ROUNDUP({0}/{1},0)*{1}",
    #         "parameters": ["cant.","unidades/caja"],
    #         "valor": lambda n0,n1: ceil(n0/n1)*n1,
    #     }
    # }


    # prepare column-width array to be computed during processing
    colwidth = [len(i) for i in headers]

    # process each row of data
    for i,r in enumerate(c):
        l = list(r)

        # process and write the row
        for j,v in enumerate(l):

            # some meta information update
            colwidth[j] = max(colwidth[j],len(unicode(v)))
            style = workbook.add_format( colstyle.get(headers[j],{}) )

            # if it is a formula cell, do an special processing
            if description[j] in formula_cells:
                f = formula_cells[description[j]] # get formula description
                # get the actual value for paramenters
                paramsi = list(f["parameters"]); params = list(f["parameters"])
                for k,p in enumerate(params):
                    paramsi[k]= description.index(p)
                    params[k]= l[paramsi[k]]
                    paramsi[k] = xlrd.cellname(i+1,paramsi[k])

                # Lets try to compute the value
                try: v = f["valor"](*params) # compuete value for cell
                except TypeError: v='#VALOR!'

                l[j] = v # update cell value

                # write actual formula and value
                worksheet.write_formula(i+1,j,f["formula"].format(*paramsi),value=v,cell_format=style)

            # if it is a normat cell
            else: worksheet.write(i+1,j,v,style)

    # update cells widths
    for i,cw in enumerate(colwidth):
        if cw!=None: worksheet.set_column(i,i,cw)

    workbook.close()



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

        FROM lista_de_compra INNER JOIN pedidos_pendientes
            ON pedidos_pendientes.GC=lista_de_compra.cod_ec
                and
                pedidos_pendientes.referencia_fabricante=lista_de_compra.cod_nac
    '''
	# ..., cod_nac,compute_0017,cod_ec
	# pedidos_pendientes.GC=lista_de_compra.cod_ec and pedidos_pendientes.referencia_fabricante=lista_de_compra.cod_nac

    log("INFO",u"Obteniendo cruces de los archivos...")
    c = conn.execute(query)


    log("INFO",u"Escribiendo el archivo %s..." % output)
    writecrossxls(output,c,log=log)
    
    # some cleanup
    log("INFO",u"Eliminando archivos temporales...")
    conn.close()
    os.close(temp[0])
    os.unlink(temp[1])
