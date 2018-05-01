#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Plot MPMS data

BB, 2015
"""

#import analyze_jjivarray as an
#from IPython.lib import deepreload; deepreload.reload(an)
#from imp import reload; reload(an)
import numpy as np
import matplotlib.pyplot as plt
from cmtools.lib.plothyst import plothyst
from cmtools.lib import plotparams
from cmtools.lib import datafile

def plot_mpms(**kwargs):
    plotparams.setplotparams()
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    col = ['b','g','r','c','m','y','k']

    datatype = kwargs.get('datatype', 'mh')
    if datatype == 'mh':
        getx = 'get_H'
        gety = 'get_M'
        
        # choose units
        if kwargs.get('unit', 'raw') == 'raw':
            unit_x, unit_y = 1, 1
            xlabel1 = 'Field (Oe)'
            ylabel1 = 'Moment (emu)'
        elif kwargs['unit'] == 'si':
            unit_x, unit_y = 0.1, 1000
            xlabel1 = 'Field (mT)'
            ylabel1 = 'Moment (Am$^2$)'

    elif datatype == 'mt':
        getx = 'get_T'
        gety = 'get_M'
        
        # choose units
        if kwargs.get('unit', 'raw') == 'raw':
            unit_x, unit_y = 1, 1
            xlabel1 = 'Temperature (K)'
            ylabel1 = 'Moment (emu)'
        elif kwargs['unit'] == 'si':
            unit_x, unit_y = 0.1, 1000
            xlabel1 = 'Temperature (K)'
            ylabel1 = 'Moment (Am$^2$)'

    filenames = kwargs['fi']
    if type(filenames) is str:
        filenames = [filenames]

    norm = kwargs.get('norm', False)    # option normalize to 0-1 range.
    if norm:
        ylabel1 = 'Normalized ' + ylabel1

    i = 0
    for fn in filenames:
        print(fn)
        data = datafile.MPMSData(fn)
        x = getattr(data, getx)()
        y = getattr(data, gety)()
        print(len(x))

        if not norm:
            plothyst(ax, x/unit_x, y/unit_y, c=col[i], mec=col[i], label=fn)
        else:
            ymin, ymax = min(y), max(y)
            plothyst(ax, x/unit_x, (y-ymin)/(ymax-ymin), c=col[i], mec=col[i], label=fn)

        i = (i+1)%len(col)

    ax.legend(loc=2)
    ax.grid(1)
    ax.set_xlabel(xlabel1)
    ax.set_ylabel(ylabel1)
    
    plt.tight_layout()
    plt.show()
    
# Adapt command line execution
def app(args):    
    if len(args) < 2:
        print('')
        print('Usage: python plot_mpms.py <plottype> <file1> [<file2> ...] [<options>]\n')
        print('Examples:')
        print('python plot_mpms.py mh data.dat')
        print('python plot_mpms.py mh data1.dat data2.dat')
        print('python plot_mpms.py mt data1.dat -i 3 -f 20 data2.dat -i 3')
        sys.exit(0)
    plottype = args[1]
    #datafiles = [args[2]]
    datafiles = []
    for k in range(2,len(args)):
        print(k, args[k])
        if args[k][0] != '-':
            datafiles += [args[k]]
        elif args[k] == '-i':
            pass
        elif args[k] == '-f':
            pass
    plot_mpms(datafiles, plottype=plottype)

if __name__ == '__main__':
    import sys
    print(sys.version)
    app(sys.argv)
