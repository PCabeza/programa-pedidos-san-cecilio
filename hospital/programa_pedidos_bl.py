# -*- coding: utf-8 -*-
from __future__ import print_function # use print as a function

# depends on packages: xlrd xlswriter and optionally chardet
import xlrd, xlsxwriter as xlsxw # read and write xls(x) files

import sqlite3, datetime, re, tempfile, os, sys, codecs
from os import path
from math import ceil

##################################
# DML general statements for mysql
##################################

CREATE= u'''CREATE TABLE %s ("primary_id" INTEGER PRIMARY KEY AUTOINCREMENT, %s)'''
INSERT= u'''INSERT INTO {} ({}) VALUES(%s)'''
INSERTNODEF = u'''INSERT INTO {} VALUES(%s)'''


###########################################################################
# XLRD cell types and their equivalent in mysql, used for converting htypes
###########################################################################

XLRD_ORDER = [ xlrd.XL_CELL_ERROR, xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BOOLEAN,
               xlrd.XL_CELL_DATE, xlrd.XL_CELL_NUMBER, xlrd.XL_CELL_TEXT, ]

XLRD_TYPES = [ "INT", "TEXT", "BOOLEAN", "REAL", "REAL", "TEXT" ]

#################################
# Auxiliary methods for db naming
#################################

def nfunc(i,v):
    "naming method for db table columns"
    return unicode(v).replace(' ','_').lower() if v else 'row%d' % i

def tfunc(fname):
    "naming method for db tables"
    return path.splitext(path.basename(nfunc(0,fname)))[0]


#####################
# Parsing input files
#####################

# TODO: check if row or table names already exists, it will fail otherwise
# TODO: save format to be used in output
def xls2sqlite(xlsfile,dbfile,table=None):
    "Dump an xls file column wise to a sqlite database"

    table = table or tfunc(xlsfile) # if table is not defined, get it from xlsfile

    # initialize workbook and get first sheet
    wb = xlrd.open_workbook(xlsfile)#,encoding_override="cp1252")#"latin-1")
    sh = wb.sheet_by_index(0)

    # infer types for database creation for each column, based on the most common type
    types = [[0 for j in range(len(XLRD_ORDER))] for i in range(sh.ncols)]
    for nrow in range(1,sh.nrows):
        for i,c in enumerate(sh.row(nrow)):
            types[i][XLRD_ORDER.index(c.ctype)]+=1

    # render create statement from the infered types using first row as column names
    header = ['"%s"'%nfunc(i,v) for i,v in enumerate(sh.row_values(0))]
    definition = ['%s %s' % (n,
                    XLRD_TYPES[types[i].index(max(types[i]))]) for i,n in enumerate(header)]
    create = CREATE % (table,','.join(definition))
    insert = INSERT.format(table,','.join(['"primary_id"']+header))


    dbfile.execute(create) # execute create

    # For each row insert them as strings, taking advantage of sqlite text based type sistem
    for nrow in range(1,sh.nrows):
        s = insert % (','.join( [unicode(nrow)]+\
                ["'%s'"%unicode(x).replace("'","''") if x!="" else "NULL"\
                                            for x in sh.row_values(nrow)]))
        dbfile.execute(s)

    dbfile.commit() #persist changes
    wb.release_resources()


# TODO use chardet to find file encoding, now is latin-1 fixed
def parseCustomFile(fname,gbeg,gheaders,gtypes,conn,basetable=None):
    '''
    Parse mercury file with the column based format given,
    It creates 2 tables, one for the actual data and one for groups.
    '''

    # Table names
    gtablename = (basetable or tfunc(fname))+"_group"
    dtablename = (basetable or tfunc(fname))+"_data"

    # Table create and insert statements
    gschema = CREATE % (gtablename, ','.join([u'"%s" TEXT'%nfunc(i,s) for i,s in enumerate(gbeg)]))
    dschema = CREATE % (dtablename, ','.join([u'"%s" %s'%(nfunc(i,s),gtypes[i]) for i,s in enumerate(gheaders)]+[u'"group_ref" INTEGER REFERENCES "%s"("primary_id")'%gtablename]))

    ginsert = INSERTNODEF.format(gtablename)
    dinsert = INSERT.format(dtablename,','.join(['"%s"'%nfunc(i,v) for i,v in enumerate(gheaders)]+['"group_ref"']))


    conn.execute(gschema); conn.execute(dschema) # Create both tables


    # Various constants for file processiong
    reheader = re.compile(''.join([r'\s*%s:\s*(.+)'%s for s in gbeg]),re.U|re.I) # header match regex
    ngroup = 0; newgroup = False; offsets = None; grouprow = None

    with codecs.open(fname, "rb", "latin-1") as f:
        for line in f: # process the file line-wise

            header = reheader.match(line) # try to match group header with regex

            if header is not None: ## it is a header
                ngroup+=1; newgroup=True
                conn.execute(ginsert % ','.join(\
                    [unicode(ngroup)] + ["'%s'"%m.strip() for m in header.groups()]))

            elif not line.strip(): continue ## white line

            elif newgroup: ## header of a group
                newgroup = False

                # compute column boundaries based on header element offsets
                def offsetgen(off):
                    i=0; prev = -1
                    for i in range(len(off)):
                        n = int(ceil((off[i]+len(gheaders[i])+off[i+1]+1)/2)) if i!=len(off)-1 else None
                        yield (prev+1, n)
                        prev = n

                off = [line.find(g) for g in gheaders]
                offsets = list(offsetgen(off))

            else: ## standard data line
                # get data using offsets pairs
                data = [line[b:e].strip() for b,e in offsets]

                # render and execute insert
                insert = dinsert % ','.join(["'%s'"%d for d in data]+[unicode(ngroup)])
                conn.execute(insert)

    conn.commit() # save changes


#############################################
# Auxiliary methods to check file permissions
#############################################

def wincheckwriteperm(file):
    '''Check if a file has write permission compatible with win 8'''
    if not path.exists(file):
        return True

    try:
        f = open(file, 'wb')
        f.close()
    except IOError:
        return False

    return True

def readvalidate(file):
    '''Validates that a file is readable'''
    if not path.exists(file): return 1
    elif not file: return 2
    else: return 0

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

                v = f["valor"](*params) # compuete value for cell
                l[j] = v # update cell value

                # write actual formula and value
                worksheet.write_formula(i+1,j,f["formula"].format(*paramsi),value=v,cell_format=style)

            # if it is a normat cell
            else: worksheet.write(i+1,j,v,style)

    # update cells widths
    for i,cw in enumerate(colwidth):
        if cw!=None: worksheet.set_column(i,i,cw)

    workbook.close()



def processfiles(unico,pendientes,mercurio,output,log=print,outputext="xlsx"):
    '''Main process of reading files and writing the output'''
    temp = tempfile.mkstemp()
    log(u"Creando archivo sqlite temporal:",temp[1])
    conn = sqlite3.connect(temp[1])

    log(u"Leyendo %s..." % unico)
    xls2sqlite(unico,conn,table="fichero_unico")

    log(u"Leyendo %s..." % pendientes)
    xls2sqlite(pendientes,conn,table="pedidos_pendientes")

    groups = ['Grupo','Sistemas']
    headers = [u"Código",u"Artículo",u"Almacén Rep.",u"Ubic.Ext",u"Unidad.Ext",u"Stk.Min",u"Stk.Max",u"Rep.Fija",u"Stk.Act",u"Cant."]
    htypes  = ['TEXT'   , 'TEXT'    , 'TEXT'        , 'TEXT'    , 'REAL'       , 'REAL'  , 'REAL'   , 'REAL'    , 'REAL'    ,'INT'  ]

    log(u"Leyendo %s..." % mercurio)
    parseCustomFile(mercurio,groups,headers,htypes,conn,basetable="fichero_mercurio")

    query = '''
        SELECT código,artículo,"stk.min","stk.max","stk.act","cant.",
               NULL as cantidad_a_pedir,
               NULL as "coste/linea",

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

    log(u"Obteniendo cruces de los archivos...")
    c = conn.execute(query)


    log(u"Escribiendo el archivo %s..." % output)
    writecrossxls(output,c,log=log)

    # some cleanup
    log(u"Eliminando archivos temporales...")
    conn.close()
    os.close(temp[0])
    os.unlink(temp[1])
