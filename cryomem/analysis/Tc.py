"""Superconducting transition temperature analysis"""
from numpy.polynomial.chebyshev import chebfit, chebroots
import numpy as np
from scipy.optimize import curve_fit, least_squares

def _slanted_step(x, u):
    """Slanted step function.

    Sectioned function:
        a1(u-b1) if u < (a1b1-a2b2)/(a1-a2)
        a3(u-b3) if u > (a3b3-a2b2)/(a3-a2)
        a2(u-b2) otherwise
    Conditions:
        b1 < b3
        a1, a3 < a2
        a2 < 1
    """
    a1, b1, a2, b2, a3, b3 = x

    # return sectioned line
    if hasattr(u, '__iter__'):
        u1 = (a1*b1 - a2*b2)/(a1 - a2)
        u3 = (a3*b3 - a2*b2)/(a3 - a2)

        idx = u < u1
        y1 = np.array(a1*(u[idx] - b1))

        idx = np.logical_and(u >= u1, u < u3)
        y2 = np.array(a2*(u[idx] - b2))

        idx = u >= u3
        y3 = np.array(a3*(u[idx] - b3))

        return np.hstack((y1, y2, y3))
    else:
        if u <= (a1*b1 - a2*b2)/(a1 - a2):
            return a1*(u - b1)
        elif u >= (a3*b3 - a2*b2)/(a3 - a2):
            return a3*(u - b3)
        else:
            return a2*(u - b2)

def _residual_step(x, u, y):
    """Residual function of _slanted_step for fitting"""
    return _slanted_step(x, u) - y

def _get_transxy(popt):
    """Get transition point x, y of _slanted_step"""
    a1, b1, a2, b2, a3, b3 = popt
    x1 = (a1*b1 - a2*b2)/(a1 - a2)
    x3 = (a3*b3 - a2*b2)/(a3 - a2)
    y1 = _slanted_step(popt, x1)
    y3 = _slanted_step(popt, x3)
    return (x1 + x3)/2, (y1 + y3)/2

def _rotate(x, y, angle):
    """Rotate x, y by angle in degree."""
    x2 = x*np.cos(angle*np.pi/180) - y*np.sin(angle*np.pi/180)
    y2 = x*np.sin(angle*np.pi/180) + y*np.cos(angle*np.pi/180)
    return x2, y2

class T_R_step:
    """superconducting R(T) data fitting: rotate by -45 deg and fit to slanted step"""
    def __init__(self, T, R):
        self.T, self.R = np.array(T), np.array(R)

    def fit(self, **kwargs):
        x2, y2 = _rotate(self.T, self.R, -45)
        guess = (-1, 0, 0.9, 14, -1, 1e-6)
        self.res = least_squares(_residual_step, guess, gtol=1e-14, xtol=1e-14,
                                 ftol=1e-14, args=(x2, y2))
        print(self.res)
        transx, transy = _get_transxy(self.res.x)
        xy = _rotate(transx, transy, 45)
        return xy 

    def testfunc(self):
        import matplotlib.pyplot as plt
        p = (-1, 0, 0.9, 14, -1, 1e-6)
        x = np.linspace(0, 10, 101)
        y = _slanted_step(x, *p)
        x2, y2 = _rotate(x, y, 45)
        print(x2)
        print(y2)
        plt.plot(x2, y2)
        plt.show()

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

# debug
if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt

    dfile = '118_T_Vac_B170726_chip23_A13_0.4uAac_asmade.dat'
    data = pd.read_table(dfile, sep='\s+', comment="#")
    
    Tc, Rc = T_R_midx(data['T'], data["Rac_device"]).fit(hsnip=0.2, vsnip=0.2)
    print("Midx results:", Tc, Rc)

    Tc, Rc = T_R_step(data['T'], data["Rac_device"]).fit()
    print("Step results:", Tc, Rc)

