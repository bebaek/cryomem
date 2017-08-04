"""Superconducting transition temperature analysis"""
from numpy.polynomial.chebyshev import chebfit, chebroots
import numpy as np

class XCheb:
    """Chebyshev polynomial x range manipulator"""
    def __init__(self, y):
        self.y = y
        self.ymin, self.ymax = np.amin(y), np.amax(y)
        self.ymid = (self.ymax - self.ymin)/2

    def get_normalized(self, y):
        return (y - self.ymid)/(self.ymax - self.ymid)

    def get_unnormalized(self, x):
        return x*(self.ymax - self.ymid) + self.ymid

class T_R_midx:
    """Superconducting R(T) data fitting class"""
    def __init__(self, T, R):
        self.T, self.R = np.array(T), np.array(R)

    def fit(self, **kwargs):
        """Linear fit transition part of R(T)."""
        hsnip = kwargs.get("hsnip", 0.1)
        vsnip = kwargs.get("vsnip", 0.4)
        Tmin, Tmax = np.amin(self.T), np.amax(self.T)
        Trange = Tmax - Tmin
        Rmin = np.mean(self.R[self.T < Tmin + Trange*hsnip])
        Rmax = np.mean(self.R[self.T > Tmax - Trange*hsnip])
        Rrange, Rmid = Rmax - Rmin, (Rmin + Rmax)/2

        ifit = np.logical_and(self.R > Rmid - Rrange*vsnip/2, self.R < Rmid + Rrange*vsnip/2)
        npts = sum(i for i in ifit)
        while npts < 4:
            vsnip = (vsnip + 1)/2
            print(vsnip)
            ifit = np.logical_and(self.R > Rmid - Rrange*vsnip/2, self.R < Rmid + Rrange*vsnip/2)
            npts = sum(i for i in ifit)
            if vsnip > 0.95:
                return np.NaN, Rmid

        p = np.polyfit(self.R[ifit], self.T[ifit], 1)
        Tc = np.polyval(p, Rmid)
        if Tc < Tmin or Tc > Tmax:
            Tc = np.NaN
        return Tc, Rmid
        #Tcheb = XCheb(self.T[ifit])
        #c = chebfit(Tcheb.get_normalized(self.T[ifit]), self.R[ifit], 2)
        #root = chebroots((c[0]-Rmid, c[1], c[2]))
        #return Tcheb.get_unnormalized(root[1])

    def build_fitcurve(self, **kwargs):
        """Calculate and return (T, R) from fit parameters.
        
        Keyword arguments:
            scale_range, npoints
        """
        extrapol = kwargs.get("scale_range", 1)
        npoints = kwargs.get("npoints", 1000)

        Tmin, Tmax = np.amin(self.T), np.amax(self.T)
        T1 = (Tmax + Tmin)/2 - extrapol*(Tmax - Tmin)/2 
        T2 = (Tmax + Tmin)/2 + extrapol*(Tmax - Tmin)/2 
        T = np.linspace(T1, T2, npoints)
        R = genlogistic(T, *self.popt)
        return T, R
