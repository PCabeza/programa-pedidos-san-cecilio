# -*- coding: utf-8 -*-
'''
programa_pedidos_san_cecilio v1.0 | (c) 2014 Pablo Cabeza 
license: modified BSD

Business logic for lista de compra
'''

from __future__ import print_function # use print as a function
import sqlite3, tempfile, os
import hospital_common as common


def writecrossxls(output,c,log=print):
    "Wrapper for common.writecxlsfromsqlite to add extra configuration"

    money_format=u'0.00 €'
    colstyle = {
        "precio final envase": {"num_format": money_format},
        "coste/ud con iva": {"num_format": money_format},
        "coste/linea": {"num_format": money_format},
    }

    formula_cells = {
        "coste/linea": {
            "formula": "={0}*{1}",
            "parameters": ["cantidad","coste/ud_con_iva"],
            "valor": lambda n0,n1: n0*n1,
        },
    }

    common.writecxlsfromsqlite(output,c,colstyle=colstyle,formula_cells=formula_cells,log=log)



def processfiles(unico,pendientes,compra,output,log=print,outputext="xlsx"):
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

    log("INFO",u"Leyendo %s..." % unico)
    try: common.xls2sqlite(compra,conn,table="lista_de_compra")
    except Exception as e:
        setattr(e,"file",u"lista compra")
        raise

    query = '''
        SELECT  cod_nac as "codigo%5Fnacional",
                cod_ec as gc,
                '02018_2' as "almacen%5Ffarmacia", -- constant column
                compute_0017 as cantidad,

                -- these columns are from file mercurio
                -- código,
                -- artículo,
                -- "stk.min",
                -- "stk.max",
                -- "stk.act",
                -- "cant.",
                CAST(NULL AS REAL) as "coste/linea",

                fichero_unico.observaciones,
                especialidad_farmaceutica,
                "unidades/caja",
                precio_final_envase,
                "coste/ud_con_iva",
                laboratorio,
                fichero_unico.descripcion_tipo_envase

        FROM
        (lista_de_compra LEFT JOIN fichero_unico ON fichero_unico.generico_de_centro=lista_de_compra.cod_ec)
        LEFT JOIN pedidos_pendientes
        ON pedidos_pendientes.gc=lista_de_compra.cod_ec
            and
            pedidos_pendientes.referencia_fabricante=lista_de_compra.cod_nac
        WHERE pedidos_pendientes.primary_id IS NULL
    '''

    log("INFO",u"Obteniendo cruces de los archivos...")
    c = conn.execute(query)


    log("INFO",u"Escribiendo el archivo %s..." % output)
    #common.writecxlsfromsqlite(output,c,log=log)
    writecrossxls(output,c,log=log)

    # some cleanup
    log("INFO",u"Eliminando archivos temporales...")
    conn.close()
    os.close(temp[0])
    os.unlink(temp[1])
