# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Run analyze_data.py

BB, 2014
"""

#import analyze_jjivarray as an
#from IPython.lib import deepreload; deepreload.reload(an)
#from imp import reload; reload(an)
import numpy as np
import matplotlib.pyplot as plt
from plothyst import plothyst

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
