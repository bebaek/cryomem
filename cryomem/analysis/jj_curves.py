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

def V_RSJ_asym(i, ic_pos, ic_neg, rn, io, vo):
    """Return voltage with asymmetric Ic's in RSJ model"""
    if ic_pos < 0 or ic_neg > 0 or rn < 0:
        #or abs(ic_neg/ic_pos) > 1.2 or abs(ic_pos/ic_neg) > 1.2 :
        # set boundaries for fitting
        #pass
        v = 1e10
    else:
        v = np.zeros(len(i))
        n = i>io+ic_pos; v[n] = rn*np.sqrt((i[n]-io)**2-ic_pos**2)+vo
        n = i<io+ic_neg; v[n] = -rn*np.sqrt((i[n]-io)**2-ic_neg**2)+vo
        n = np.logical_and(i>=io+ic_neg, i<=io+ic_pos); v[n]=vo
    return v
