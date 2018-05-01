#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Manage database of SV JJ device fab/measurement parameters
File format: SQLite
Tables: barrier (dep structure), shape, josephson (measured params),
        trend (fitted Jc, RnA, IcRn)

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

class SVJJDB():
    def __init__(self, filename0='svjj.db'):
        dbpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        filename = dbpath + '/data/' + filename0
        self.tables = ['barrier', 'shape', 'josephson']

        # Table structures
        self.colnames = {
                'barrier': ['wafer', 'chip', 'structure', 'fm1_name',
                    'fm1_thickness', 'fm2_name', 'fm2_thickness'],
                'shape': ['wafer', 'chip', 'device', 'shape', 'dim1', 'dim2'],
                'josephson': ['wafer', 'chip', 'device', 'temperature',
                    'iv_model', 'ic_p', 'ic_ap', 'r_p', 'r_ap'],
                #'trend': ['wafer', 'structure', 'jc_p', 'jc_ap',
                #    'fm1_thickness', 'fm2_name', 'fm2_thickness'],
                }
        self.datatypes = {'wafer': 'string', 'chip':'string',
                'structure': 'string','shape':'string', 'fm1_name': 'string',
                'fm2_name': 'string', 'fm1_thickness': 'float',
                'fm2_thickness': 'float', 'device': 'string', 'dim1': 'float',
                'dim2': 'float', 'temperature': 'float', 'iv_model': 'string',
                'ic_p': 'float', 'ic_ap': 'float', 'r_p': 'float', 
                'r_ap': 'float'}
        
        # Default values
        self.val0 = {'wafer': 'B150323a', 'chip': '56',
                'structure': 'Fe/Cu/Ni/Cu', 'shape':'ellipse', 'fm1_name': 'Fe',
                'fm2_name': 'Ni', 'fm1_thickness': '1e-9',
                'fm2_thickness': '2.4e-9', 'device': 'A01', 'dim1': '1e-6',
                'dim2': '1e-6', 'temperature': 4, 'iv_model': 'rsj',
                'ic_p': '10e-6', 'ic_ap': '5e-6', 'r_p': '1', 'r_ap': '1'}

        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def create_table(self, table):
        if table == 'barrier':
            self.c.execute(
              'CREATE TABLE barrier '
              '(wafer text, chip text, structure text, '
              'fm1_name text, fm1_thickness real, '
              'fm2_name text, fm2_thickness real) ')
        elif table == 'shape':
            self.c.execute(
              'CREATE TABLE shape '
              '(wafer text, chip text, device text, '
              'shape text, dim1 real, dim2 real) ')
        elif table == 'josephson':
            self.c.execute(
              'CREATE TABLE josephson '
              '(wafer text, chip text, device text, temperature real, '
              'iv_model, ic_p real, ic_ap real, r_p real, r_ap real) ') 
        else:
            print('Invalid table name:', table)

    def create_tables_old(self):
        
        # Create barrier structure table
        self.c.execute('''CREATE TABLE barrier
                (wafer text, chip text, structure text,
                fm1_name text, fm1_thickness real,
                fm2_name text, fm2_thickness real)''') 
        
        # Create device shape table
        self.c.execute('''CREATE TABLE shape
                (wafer text, chip text, device text,
                shape text, dim1 real, dim2 real)''') 

        # Create josephson measurement result table
        self.c.execute('''CREATE TABLE josephson
                (wafer text, chip text, device text, temperature real,
                ic_p real, ic_ap real, r_p real, r_ap real)''') 

    def drop_table(self, table):
        self.c.execute('DROP TABLE %s' % scrub(table))

    def close(self, save=True):
        if save: self.conn.commit()  # save
        self.conn.close()

    # Insert a row in barrier table
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
        if table == 'barrier':
            self.c.execute('DELETE FROM %s WHERE wafer=? AND chip=?'
                    % scrub(table), args)
        elif table == 'shape' or table == 'josephson':
            self.c.execute('DELETE FROM %s WHERE '
                    'wafer=? AND chip=? AND device=?' % scrub(table), args)
        else:
            print('No table name: %s' % table)

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

    def search_josephson(self, **kwargs):
        '''**kwargs: searchcol, searchval
            examples: 
            searchcol=['structure', 'fm2_thickness'], 
            searchval=['Fe/Cu/Ni/Cu', 2.4e-9]
        '''
        searchcol = kwargs['searchcol']
        searchval = kwargs['searchval']

        # find relevant tables from searchcol and outcol
        #searchtables = [t for t in self.tables 
        #  if set(searchcol) & set(colnames[table]) != set()]

        # convert columns in outcol to "table.column" format
        #tables = [[t for t in self.tables if c in self.colnames[t]]
        #  for c in outcol]
        #outcol = [tables[k]+'.'+c for k,c in enumerate(outcol)]

        # find common columns in all the relevant tables to use as keys
        
        # build SQL command "INNER JOIN"
        cond = ''
        if type(searchcol) is str:      # need list type
            searchcol, searchval = [searchcol], [searchval]
        for k, col in enumerate(searchcol):
            if self.isfloat(searchval[k]):
                cond += col + '=' + str(searchval[k]) + ' AND '
            else:
                cond += col + '=\'' + str(searchval[k]) + '\' AND '

        cond = cond[:-5]

        #cmd = ('SELECT barrier.wafer, barrier.chip, josephson.device, '
        #       'barrier.structure, barrier.fm1_thickness, '
        #       'barrier.fm2_thickness, josephson.ic_p, josephson.ic_ap, '
        #       'josephson.r_p '
        #       'FROM barrier '
        #       'JOIN josephson '
        #       'ON {} AND barrier.wafer=josephson.wafer AND '
        #       'barrier.chip=josephson.chip '
        #       'LEFT JOIN shape '
        #       'ON barrier.wafer=shape.wafer=josephson.wafer '
        #       'AND barrier.chip=shape.chip=josephson.chip '
        #       'AND shape.device=josephson.device'
        #      ).format(cond)
        cmd = ('SELECT barrier.wafer, barrier.chip, josephson.device, '
               'barrier.structure, barrier.fm1_thickness, '
               'barrier.fm2_thickness, josephson.ic_p, josephson.ic_ap, '
               'josephson.r_p '
               'FROM barrier '
               'JOIN josephson '
               'ON barrier.wafer=josephson.wafer AND '
               'barrier.chip=josephson.chip '
               'WHERE {} '
              ).format(cond)
        print('cmd:', cmd)
        return self.c.execute(cmd).fetchall()
        
    def simplesearchdb1(self, barrierstr, fm2_thickness):
        cmd = ('SELECT barrier.wafer, barrier.chip, device '
               'FROM barrier '
               'LEFT JOIN shape '
               'ON barrier.wafer=shape.wafer AND barrier.chip=shape.chip ')
        args = ()
        #cmd = ('SELECT wafer, chip, device, fm1_thickness, ic_p '
        #       'FROM barrier '
        #       'INNER JOIN shape '
        #       'ON barrier.wafer=shape.wafer AND barrier.chip=shape.chip '
        #       'INNER JOIN josephson '
        #       'ON structure=? AND fm2_thickness=? '
        #       'AND josephson.device=shape.device')
        #args = (barrierstr, fm2_thickness)
        rows = self.c.execute(cmd, args)
        for row in rows:
            print(row)
        return rows

# Derived class for interactive shell execution
class SVJJDBInteract(SVJJDB):
    #def create_db(self, *arg):
    #    self.create_tables(*arg)  # pass filename

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

# main shell interface (run SVJJDBInteract class)
def app(argv):
    """Execute in system shell
    """
    if len(argv) < 2:
        print("Usage: python %s <command> <<table> or <SQL statement>>\n" 
              "       <command>: print, insert, delete, or execsql\n"
              "       <table>: barrier, shape, or josephson\n"
              "\n"
              "Examples:\n"
              "       python %s execsql \"update josephson set"
              " device=\'A02\' where"
              " wafer=\'B150323a\' and chip=\'56\' and device=\'a02\'\"\n"
              % (argv[0], argv[0]))
        sys.exit(0)

    db = SVJJDBInteract()
    methodname = argv[1]
    print(argv[2:])
    getattr(db, methodname)(*argv[2:])
    db.close()

# simple test run
def app2(argv):
    db = SVJJDB()
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
