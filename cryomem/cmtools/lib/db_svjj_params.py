# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Manage database of SV JJ parameters
File format: HDF5.

BB, 2015
"""

import numpy as np
import tables as tb

class JJParams(tb.IsDescription):
    wafer   = tb.StringCol(16)
    chip    = tb.StringCol(16)
    device  = tb.StringCol(16)
    meastime = tb.StringCol(8)
    #meastime = tb.Time64()
    measequip = tb.StringCol(20)
    measmethod = tb.StringCol(50)
    shape   = tb.StringCol(8)
    dimx    = tb.Float64()
    dimy    = tb.Float64()
    temperature = tb.Float64()
    ic_p    = tb.Float64()
    ic_ap   = tb.Float64()
    rn_p   = tb.Float64()
    rn_ap   = tb.Float64()

class DB():
    def __init__(**kwargs):
        if 'filename' in kwargs:
            self.open_db(kwargs['filename'])

    def open_db():
        pass
    
    def close_db():
        pass
    
    def add_jj(**kwargs):
        pass

    def del_jj(**kwargs):
        pass

    def edit_jj(**kwargs):
        pass
    

def plot_svjj(filenames, **kwargs):
    whichplot = kwargs('whichplot', 'hic')
    if whichplot == 'hic':  # H vs Ic
        ix = 1; iy = 3
    for fn = in filenames:
        data = np.loadtxt(filename, 

def app(args):    
    if len(args) < 2:
        print('')
        print('Usage: python plot_cryomem.py <filename> [<arguments>]\n')
        print('Examples:')
        print('python daq_dipstick.py sqwave_field h=150')
        print('python daq_dipstick.py set_sweepvolt .7')
        sys.exit(0)
    func = args[1]
    fn = args[2]
    if func == 'iv':
        pass
    elif func == 'hic':
        data = np.loadtxt(data, skiprows=1, usecols=(2,4))
        plothyst.plothyst(data[0], data[1])

    plt.show()


if __name__ == '__main__':
    import sys
    print(sys.version)
    app(sys.argv)
