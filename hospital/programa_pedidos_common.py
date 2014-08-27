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

def nfunc(i,v,collision_dict=None):
    "naming method for db table columns, collision_dict is used to rename duplacate names"
    name = unicode(v).replace(' ','_').lower() if v else 'row%d' % i
    if collision_dict is None: pass
    elif name in collision_dict:
        collision_dict[name] += 1
        name += u'_%d' % collision_dict[name]
    else: collision_dict[name] = 0
    return name

def tfunc(fname,collision_dict=None):
    "naming method for db tables"
    return path.splitext(path.basename(nfunc(0,fname,collision_dict=collision_dict)))[0]


#####################
# Parsing input files
#####################

# TODO: check if table names already exists, it will fail otherwise
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
    colld = {} # collision dict for duplicate collumns
    header = ['"%s"'%nfunc(i,v,collision_dict=colld) for i,v in enumerate(sh.row_values(0))]
    definition = ['%s %s' % (n,
                    XLRD_TYPES[types[i].index(max(types[i]))]) for i,n in enumerate(header)]
    create = CREATE % (table,','.join(definition))
    insert = INSERT.format(table,','.join(['"primary_id"']+header).replace('%','%%'))


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
