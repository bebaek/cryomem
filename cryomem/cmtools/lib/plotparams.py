# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Common plot parameters

BB, 2015
"""

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

