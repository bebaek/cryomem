#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Manage database of MPMS measurement parameters
File format: SQLite
Tables: layer (dep structure), shape (chip dimensions), 
        mh (measured Ms and Hc), mt (superconducting Tc)

BB, 2015
"""

import sqlite3
import os

# Allow only alphanumerics or similar in SQL command
def scrub(name):
    return ''.join( chr for chr in name if chr.isalnum() or chr=='_' 
     or char=='.' )

# Build string: 'column1=?,column2=?,...'
def assigncolume(collist):
    s = ''
    for col in collist:
        s += col + '=?,'
    return s.rstrip(',')

class MPMSDB():
    def __init__(self, filename0='mpms.db'):
        dbpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        filename = dbpath + '/data/' + filename0
        self.tables = ['layer', 'shape', 'mhip', 'mhpp', 'mt']
        
        # Table structures
        self.colnames = {
                'layer': ['wafer', 'structure', 'fm_name',
                    'fm_thickness', 'seed_name', 'seed_thickness'],
                'shape': ['wafer', 'shape', 'dim1', 'dim2'],
                'mhip': ['wafer', 'temperature', 'ms', 'hc'],
                'mhpp': ['wafer', 'temperature', 'ms', 'hc'],
                'mt': ['wafer', 'field', 'tc']
                }
        self.datatypes = {'wafer': 'string', 'structure': 'string',
                'shape':'string', 'fm_name': 'string', 'fm_thickness': 'float',
                'seed_name': 'string', 'seed_thickness': 'float',
                'dim1': 'float', 'dim2': 'float', 'temperature': 'float',
                'ms': 'float', 'hc': 'float', 'field': 'float', 'tc': 'float'}
        
        # Default values
        self.val0 = {'wafer': 'B150512', 'structure': 'Ta/Cu/Co/Cu/Ta', 
                'shape':'square', 'fm_name': 'Co', 'fm_thickness': '2e-9',
                'seed_name': 'Cu', 'seed_thickness': '3e-9',
                'dim1': '6e-3', 'dim2': '6e-3', 'temperature': 10, 
                'ms': '10e-9', 'hc': '30e-4', 'field': '0', 'tc': '5'}

        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def create_table(self, table):
        if table == 'layer':
            self.c.execute(
              'CREATE TABLE layer '
              '(wafer text, structure text, '
              'fm_name text, fm_thickness real, '
              'seed_name text, seed_thickness real) ') 
        elif table == 'shape':
            self.c.execute(
              'CREATE TABLE shape '
              '(wafer text, shape text, dim1 real, dim2 real) ') 
        elif table == 'mhip':
            self.c.execute(
              'CREATE TABLE mhip '
              '(wafer text, temperature real, ms real, hc real) ') 
        elif table == 'mhpp':
            self.c.execute(
              'CREATE TABLE mhpp '
              '(wafer text, temperature real, ms real, hc real) ') 
        elif table == 'mt':
            self.c.execute(
              'CREATE TABLE mt '
              '(wafer text, field real, tc real) ') 
        else:
            print('Invalid table name:', table)

    def create_tables_old(self, *dbfile):
        
        # Create layer structure table
        self.c.execute('''CREATE TABLE layer
                (wafer text, structure text,
                fm_name text, fm_thickness real,
                seed_name text, seed_thickness real)''') 
        
        # Create chip shape table
        self.c.execute('''CREATE TABLE shape
                (wafer text, shape text, dim1 real, dim2 real)''') 

        # Create in-plane M-H measurement result table
        self.c.execute('''CREATE TABLE mhip
                (wafer text, temperature real, ms real, hc real)''') 

        # Create perpendicular-to-plane M-H measurement result table
        self.c.execute('''CREATE TABLE mhpp
                (wafer text, temperature real, ms real, hc real)''') 

        # Create M-T measurement result table
        self.c.execute('''CREATE TABLE mt
                (wafer text, field real, tc real)''') 

    def drop_table(self, table):
        self.c.execute('DROP TABLE %s' % scrub(table))

    def close(self, save=True):
        if save: self.conn.commit()  # save
        self.conn.close()

    # Insert a row in a table
    def insert_row(self, table, arg):
        s1 = 'INSERT INTO %s VALUES ' % scrub(table)
        s2 = '(' + '?,'*(len(arg)-1) + '?)'
        self.c.execute(s1+s2, arg)
    
    def print_table(self, table):
        print(self.colnames[table])
        for row in self.c.execute('SELECT * FROM %s'%scrub(table)):
            print(row)
    #def print_table(self, table, ordercol):
        #for row in self.c.execute('SELECT * FROM %s ORDER BY ?'%scrub(table),\
        #        (ordercol,)):

    def list_tables(self):
        cmd = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        for row in self.c.execute(cmd):
            print(row)

    def delete_row(self, table, args):
        self.c.execute('DELETE FROM %s WHERE wafer=?' % scrub(table), args)

    # arg = list of columns
    def update_row(self, table, arg):
        s1 = 'UPDATE %s SET ' % scrub(table)
        s2 = assigncolumn(arg)
        s3 = 'WHERE'
        self.c.execute(s1+s2, arg)

    def isfloat(self, s):
        try:
            val = float(s)
        except ValueError:
            return False
        else:
            return True

    def search_mhip(self, **kwargs):
        '''**kwargs: searchcol, searchval
            examples: 
            searchcol=['structure', 'fm_thickness'], 
            searchval=['Ta/Cu/Co/Cu/Ta', 1e-9]
        '''
        searchcol = kwargs['searchcol']
        searchval = kwargs['searchval']

        # build SQL command "INNER JOIN"
        cond = ''
        if type(searchcol) is str:      # need list type
            searchcol, searchval = [searchcol], [searchval]
        for k, col in enumerate(searchcol):
            if self.isfloat(searchval[k]):
                cond += col + '=' + str(searchval[k]) + ' AND '
            else:
                cond += col + '=\'' + str(searchval[k]) + '\' AND '

        cond = cond[:-5]    # strip " AND "

        #cmd = ('SELECT layer.wafer, layer.structure, layer.fm_name, '
        #       'layer.fm_thickness, shape.shape, shape.dim1, shape.dim2, '
        #       'mhip.ms, mhip.hc '
        #       'FROM layer '
        #       'JOIN mhip '
        #       'ON {} AND layer.wafer=mhip.wafer '
        #       'LEFT JOIN shape '
        #       'ON layer.wafer=shape.wafer=mhip.wafer '
        #      ).format(cond)
        #cmd = ('SELECT layer.wafer, layer.structure, layer.fm_name, '
        #       'layer.fm_thickness, shape.shape, shape.dim1, shape.dim2, '
        #       'mhip.ms, mhip.hc '
        #       'FROM layer '
        #       'JOIN mhip '
        #       'ON layer.wafer=mhip.wafer '
        #       'LEFT JOIN shape '
        #       'ON layer.wafer=shape.wafer=mhip.wafer '
        #       'WHERE {} '
        #      ).format(cond)
        cmd = ('SELECT layer.wafer, layer.structure, layer.fm_name, '
               'layer.fm_thickness, shape.shape, shape.dim1, shape.dim2, '
               'mhip.ms, mhip.hc '
               'FROM layer '
               'JOIN shape '
               'ON layer.wafer=shape.wafer '
               'JOIN mhip '
               'ON layer.wafer=mhip.wafer '
               'WHERE {} '
              ).format(cond)
        print('cmd:', cmd)
        return self.c.execute(cmd).fetchall()
 
    def search_mhpp(self, **kwargs):
        pass

    def search_mt(self, **kwargs):
        pass

# Derived class for interactive shell execution
class MPMSDBInteract(MPMSDB):
    def create_db(self, *arg):
        self.create_tables(*arg)  # pass filename

    def tables(self):
        self.list_tables()

    def print(self, table):
        self.print_table(table)

    # Get inputs from argument or interactively
    # Use val0 as default for interactive case
    def input_param(self, key, val0='0', **kwargs):
        interact = kwargs.get('interact', True)
        datatype = kwargs.get('datatype', 'string')
        if interact:
            msg = input(key + '? [%s] '%str(val0))
            if msg == '': msg = val0          # empty input means default

            if datatype == 'string': val = msg
            if datatype == 'int': val = int(msg)
            if datatype == 'float': val = float(msg)
        else:
            val = val0
        return val

    def insert(self, table):
        vals = ()
        for col in self.colnames[table]:
            vals = vals + (self.input_param(col, self.val0[col],\
                    datatype=self.datatypes[col], interact=True),)

        self.insert_row(table, vals)

    def delete(self, table, *args):
        self.delete_row(table, args)
    
    # Pass on any SQL statement
    def execsql(self, *cmd):
        print('Executing: %s' % cmd[0])
        self.c.execute(cmd[0])

# main shell interface (run MPMSDBInteract class)
def app(argv):
    """Execute in system shell
    """
    if len(argv) < 2:
        print(
          "Usage: python sql_mpms.py <command> <table or SQL statement>\n" 
          "       <command>: create_db, tables, print, insert, delete, or execsql\n"
          "       <table>: layer, shape, mhip, mhpp, or mt\n"
          "\n"
          "Examples:\n"
          "       python sql_mpms.py print\n"
          "       python sql_mpms.py insert mhip\n"
          "       python sql_mpms.py delete shape B150512\n"
          "       python sql_mpms.py execsql \"update mh set"
          " ms=30e-4 where wafer=\'B150323a\'\"\n"
          "\n"
          "Use MKS units (m, T, K, A/m, etc).\n")
        sys.exit(0)

    db = MPMSDBInteract()
    methodname = argv[1]
    print(argv[2:])
    getattr(db, methodname)(*argv[2:])
    db.close()

# simple test run
def app2(argv):
    db = MPMSDB()
    #db.create_tables()
    db.insert_row('barrier', ('B150413', '22', 'Fe/Cu/Ni/Cu', 'Fe', 1e-9,\
            'Ni', 2.4e-9))
    db.print_table('barrier', 'chip')
    db.close()

if __name__ == '__main__':
    import sys
    print(sys.version)
   
    app(sys.argv)
    print('Bye!')
