#!/usr/bin/python3
"""Fit and estimate wedge film rate distribution.

BB
"""
import numpy as np
import sys
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def f(coord, a0, a1, a2, a3, a4, a5, a6, a7, a8):
    """Evaluate 2-d function by: a0*x**2*y**2 + a1*x**2*y + ... + a8
    
    Parameters:
    coord: (x,y): (float, float)
    a0,...,a8: float
    """
    x, y = coord
    #return a*x**2 + b*x*y + c*y**2 + d
    return a0*x**2*y**2 + a1*x**2*y + a2*x**2 \
            + a3*x*y**2 + a4*x*y + a5*x \
            + a6*y**2 + a7*y + a8

def rotate(x, y, phi):
    """Return rotated x, y by angle phi (radian)"""
    x2 = x*np.cos(phi) - y*np.sin(phi)
    y2 = x*np.sin(phi) + y*np.cos(phi)
    return x2, y2

def save_fit(fname, params):
    """Save fit params (np.array)"""
    np.savetxt(fname, params)

def load_fit(fname):
    return np.loadtxt(fname)

def get_globxy(col, row, xlocal, ylocal):
    return (col*10000 - 35000 + xlocal, row*10000 - 35000 + ylocal)

def get_rate(p, x, y, scale):
    return f((x, y), *list(p))*scale

class wedge:
    def __init__(self,fname):
        self.p = load_fit(fname)

    def set_loc(self, **kwargs):
        pass

    def get_rate(self):
        pass

def main(argv):
    if len(argv) < 2:
        print('Usage:   wedge.py fname col row xlocal ylocal scale [angle]')
        print('Example: wedge.py Ni_wedge_B160224b.dat 3 3 0 3000 0.5333')
        print('')
        print('fname: fit parameter datafile')
        print('angle: misalignment angle')
        sys.exit(1)

    fname = argv[1]
    col, row, xlocal, ylocal, scale = map(float, argv[2:7])
    angle = float(argv[7]) if len(argv) > 7 else 0

    p = load_fit(fname)
    x0, y0 = get_globxy(col, row, xlocal, ylocal)
    x, y = rotate(x0, y0, angle*np.pi/180)
    return get_rate(p, x, y, scale)

#w = Wedge()
    #w.load_cal(material)
    #w.fit_cal()
    #x, y = w.get_globxy(col, row, xlocal, ylocal)
    #print('x, y, rate = ', x, y, w.get_rate(x, y))
    #print(w.get_rate(x, y, scale))
    #w.plot_cal()

if __name__ == '__main__':
    print(main(sys.argv))

