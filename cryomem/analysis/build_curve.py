import numpy as np

def build_curve(func, x, *param, **kwargs):
    """Build fit 1-d data arrays [y = f(x)].

    Keyword arguments:
        num, minfac, maxfac
        xmin, xmax: overides the limits given by data
    """
    num     = kwargs.get("num", 100)
    minfac  = kwargs.get("minfac", 1)
    maxfac  = kwargs.get("maxfac", 1)
    xmin = kwargs.get("xmin", np.amin(x))
    xmax = kwargs.get("xmax", np.amax(x))

    xfit = np.array(np.linspace((xmin + xmax)/2 +
                (xmin - xmax)/2*minfac,
                (xmin + xmax)/2 - (xmin - xmax)/2*maxfac, num))
    yfit = func(xfit, *param)
    return xfit, yfit
