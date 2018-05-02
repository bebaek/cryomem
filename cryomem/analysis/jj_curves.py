"""Fit curve definitions for JJs"""
import numpy as np
from scipy.special import jn

def airypat(x, *p):
    """Return Airy f(x) = p0*|J1(pi*p1(x - p2))/(pi*p1(x - p2))|."""
    #print(p)
    return p[0]*abs(2*jn(1, np.pi*p[1]*(x - p[2]))\
        /(abs(np.pi*p[1]*(x - p[2]) + 1e-20)))  # bypass divide by 0

def airypat_easy(x, *p):
    """Return Airy pattern defined by Ic, Hcen, Hnode.

    Arguments:
        x, Ic, Hcenter, Hnode: float
    """
    p1 = 3.81/np.pi/(np.abs(p[1] - p[2]))
    return airypat(x, p[0], p1, p[1])
