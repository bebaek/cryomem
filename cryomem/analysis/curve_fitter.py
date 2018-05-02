"""Generic curve fitting tool"""
import numpy as np
from scipy.optimize import curve_fit
from ..common.datacondition import deglitch

class CurveFitter1D:
    """1-dim curve fitting tool class. Unnecessary abstraction. To be deprecated."""
    def __init__(self, x=[0], y=[0], func=lambda x: 0):
        """Load data and fit function.

        func: f(x, *param) form
        """
        #k = deglitch(y, factor=1e6)      # remove glitch by orders of mag
        #self.x, self.y = x[k], y[k]
        self.x, self.y = x, y
        self.func = func

    def fit(self, guess):
        self.popt, self.pcov = curve_fit(self.func, self.x, self.y, guess)
        return self.popt, self.pcov

    def build_curve(self, **kwargs):
        """Build fit data arrays.

        Keyword arguments:
            num, minfac, maxfac
            xmin, xmax: overides the limits given by data
        """
        num     = kwargs.get("num", 100)
        minfac  = kwargs.get("minfac", 1)
        maxfac  = kwargs.get("maxfac", 1)
        xmin = kwargs.get("xmin", np.amin(self.x))
        xmax = kwargs.get("xmax", np.amax(self.x))

        self.xfit = np.array(np.linspace((xmin + xmax)/2 +
                    (xmin - xmax)/2*minfac,
                    (xmin + xmax)/2 - (xmin - xmax)/2*maxfac, num))
        self.yfit = self.func(self.xfit, *self.popt)
        return self.xfit, self.yfit

    def get_popt(self):
        return self.popt

    def get_pcov(self):
        return self.pcov

    def set_popt(self, popt):
        """Set fit parameters manually for reasons other than fitting."""
        self.popt = popt
