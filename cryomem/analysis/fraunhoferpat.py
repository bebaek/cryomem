"""Fit Fraunhofer pattern data"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import jn
from ..common.datacondition import deglitch

class FraunhoferPat:
    """Fraunhofer pattern data fitter (single-valued)"""
    def __init__(self, x, y):
        # Load data
        k = deglitch(y, factor=10)
        self.x, self.y = x[k], y[k]

    def func(self, x, *p):
        """Return Fraunhofer f(x) = p0*|sinc(p1(x - p2))|"""
        return p[0]*abs(np.sinc(p[1]*(x - p[2])))

    def fit(self, guess = [1, 1, 0]):
        self.p, self.pcov = curve_fit(self.func, self.x, self.y, guess)
        return self.p, self.pcov

    def build_curve(self, **kwargs):
        """Build fit data arrays"""
        num     = kwargs.get("num", 100)
        minfac  = kwargs.get("minfac", 1)
        maxfac  = kwargs.get("maxfac", 1)
        xmax = np.amax(self.x)
        xmin = np.amin(self.x)
        x = np.array(np.linspace((xmin + xmax)/2 + (xmin - xmax)/2*minfac, \
            (xmin + xmax)/2 - (xmin - xmax)/2*maxfac, num))
        self.xfit = x
        self.yfit = self.func(x, *self.p)
        return self.xfit, self.yfit

    def get_max(self):
        return self.p[0]

    def get_offset(self):
        return self.p[2]

class AiryPat(FraunhoferPat):
    """Airy pattern data fitter"""
    def func(self, x, *p):
        """Return Airy f(x) = p0*|J1(pi*p1(x - p2))/(pi*p1(x - p2))|."""
        return p[0]*abs(2*jn(1, np.pi*p[1]*(x - p[2]))\
            /(abs(np.pi*p[1]*(x - p[2]) + 1e-20)))  # bypass divide by 0
