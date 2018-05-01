# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Get Jc, RA, etc from measured parameter DB

BB, 2015
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# display units
unit_i = 1e-6  # uA
unit_v = 1e-6   # uV
unit_r = 1      # Ohm
unit_i1 = 1e-3  # mA; control I
unit_v1 = 1e-3  # mV; control V
unit_h = 10    # mT

def setplotparams():
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['legend.frameon'] = False

def plot_svjj(filenames, **kwargs):
    whichplot = kwargs('whichplot', 'hic')
    if whichplot == 'hic':  # H vs Ic
        ix = 1; iy = 3
    #for fn = in filenames:
    #    data = np.loadtxt(filename, 

class LinFitSVJJ():
    def __init__(self, filename='svjj.db'):
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        setplotparams()

    def get_area(self, row):
        if row[0] == 'circle':
            return np.pi*row[1]**2/4
        elif row[0] == 'ellipse':
            return np.pi*row[1]*row[2]/4
        elif row[0] == 'rectangle':
            return row[1]*row[2]

    def select_chip(self, wafer, chip):
        self.c.execute('''
            SELECT shape.shape, shape.dim1, shape.dim2, 
            josephson.ic_p, josephson.ic_ap, josephson.r_p, josephson.r_ap
            FROM shape JOIN josephson 
            ON shape.wafer=josephson.wafer AND shape.chip=josephson.chip
                AND shape.device=josephson.device''')
        self.chipdata = self.c.fetchall()

        self.areas = []
        self.ic_p = []
        self.ic_ap = []
        self.r_p = []
        for row in self.chipdata:
            self.areas += [self.get_area(row)]
            self.ic_p += [row[3]]
            self.ic_ap += [row[4]]
            self.r_p += [row[5]]

    def print_chip(self):
        print(self.chipdata)

    def plot_chip(self):
        fig = plt.figure(0, (12,6))
        
        # plot Ic's
        ax1 = fig.add_subplot(121)
        ax1.plot(self.areas, self.ic_p, 's')
        ax1.plot(self.areas, self.ic_ap, 'o')
        
        # plot R's
        ax2 = fig.add_subplot(122)
        ax2.plot(self.areas, 1/np.array(self.r_p), 's')
        print(self.ic_p)
        
        plt.show()

# main shell interface (run SVJJDBInteract class)
def app(argv):
    """Execute in system shell
    """
    if len(argv) < 2:
        print("Usage: python %s <command> <table>\n" 
              "       <command>: print, insert, delete, or edit\n"
              "       <table>: barrier, shape, or josephson\n" % argv[0])
        sys.exit(0)

    db = SVJJDBInteract()
    methodname = argv[1]
    print(argv[2:])
    getattr(db, methodname)(*argv[2:])
    db.close()
    print('Bye!')

def test(argv):
    lf = LinFitSVJJ()
    lf.select_chip('B150323a', '56')
    lf.print_chip()
    lf.plot_chip()
    
if __name__ == '__main__':
    import sys
    print(sys.version)
    test(sys.argv)
    print('Bye!')
