"""Superconducting transition temperature analysis"""
from scipy.optimize import curve_fit
import numpy as np
from random import uniform
import sys
from ..common.datacondition import deglitch

def genlogistic(x, A, K, B, M, nu):
    """Return generalized logistic function.
    
    Arguments:
        x, A, K, B, M, nu 
    Return:
        A + (K - A)/(1 + np.exp(-B*(x-M)))**(1/nu)
    """
    return A + (K - A)/(1 + np.exp(-B*(x-M)))**(1/nu)

def asym_tanh(x, a, b, c1, c2, d):
    """Return asymmetric tanh.

    Arguments:
        x, a, b, c1, c2, d
    Return:
        x >= d: a + b*tanh(c1(x-d))
        x < d:  a + b*tanh(c2(x-d))
    """
    if hasattr(x, '__iter__'):
        y1 = np.array(a + b*np.tanh(c1*(x[x >= d] - d)))
        y2 = np.array(a + b*np.tanh(c2*(x[x < d] - d)))
        return np.hstack((y1, y2))
    else:
        if x >= d:
            return a + b*np.tanh(c1*(x-d))
        else:
            return a + b*np.tanh(c2*(x-d))

class T_R_asym_tanh:
    """Superconducting R(T) data fitting class"""
    def __init__(self, T, R):
        self.T, self.R = T, R
        self.fitfunc = asym_tanh

    def fit(self):
        """Fit R(T) with general logistic function and return Tc."""
        a = np.mean(self.R)
        b = (np.amax(self.R) - np.amin(self.R))/2
        c1 = 10/(np.amax(self.T) - np.amin(self.T))
        c2 = 10/(np.amax(self.T) - np.amin(self.T))
        d = np.mean(self.T)

        guess = (a, b, c1, c2, d)
        self.popt, self.pcov = curve_fit(self.fitfunc, self.T, self.R, guess)
        return self.popt[4]

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

class T_R_genlogistic:
    """Superconducting R(T) data fitting class with general logistic function"""
    def __init__(self, T, R):
        idx = deglitch(T, factor=20)
        self.T, self.R = T[idx], R[idx]
        self.fitfunc = genlogistic

    def fit(self, **fitparams):
        """Fit R(T) with general logistic function and return Tc.
        
        fitparams: 
            lb_Tc, ub_Tc -- float
            others passed to curve_fit()"""
        Tmin, Tmax = np.amin(self.T), np.amax(self.T)
        Rmin = np.mean(self.R[self.T < Tmin + (Tmax - Tmin)*.1])
        Rmax = np.mean(self.R[self.T > Tmax - (Tmax - Tmin)*.1])
        A = np.amin(self.R)
        K = np.amax(self.R)
        B = 400/(Tmax - Tmin)
        #M = (Tmax + Tmin)/2
        M = np.amin(self.T[self.R > (Rmax + Rmin)/2])
        nu = 1
        guess = (A, K, B, M, nu)

        # bounds: not really helping
        lb_A, ub_A = Rmin*.8, Rmin*1.2
        lb_K, ub_K = Rmax*.8, Rmax*1.2
        lb_M = fitparams.pop("lb_Tc", Tmin*.3)
        ub_M = fitparams.pop("ub_Tc", Tmax*1.3)
        #bounds = ([lb_A, lb_K, -np.inf, lb_M, -np.inf], 
        #          [ub_A, ub_K, np.inf, ub_M, np.inf])
        bounds = ([-np.inf, -np.inf, -np.inf, -np.inf, -np.inf], 
                  [np.inf, np.inf, np.inf, np.inf, np.inf])
        #print("Bounds:", bounds)

        # Fit
        #fitkwargs = dict(method="trf", bounds=bounds, **fitparams)
        #fitkwargs = dict(method="lm", **fitparams)
        try:
            fitparams['method'] = fitparams.get('method', 'lm')
            self.popt, self.pcov = curve_fit(self.fitfunc, self.T, self.R,
                                             guess, **fitparams)
        except RuntimeError:  # Try different fit method
            fitparams['method'] = 'trf' if fitparams['method'] == 'lm' else 'lm'
            self.popt, self.pcov = curve_fit(self.fitfunc, self.T, self.R,
                                             guess, **fitparams)
            
        A, K, B, M, nu = self.popt
        Tc = (B*M - np.log(2**nu - 1))/B    # halfway pt
        Rc = self.fitfunc(Tc, *self.popt)
        perr = np.sqrt(np.diag(self.pcov))
        return Tc, Rc, perr

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

def test1():
    """Test plot"""
    import matplotlib.pyplot as plt

    x = np.linspace(5, 8, 100)
    A, K, B, M, nu = 0.1, 1, 10, 7, 0.1
    y = genlogistic(x, A, K, B, M, nu)
    plt.plot(x, y, "o")
    plt.pause(5)

def test2():
    """Test fit"""
    import matplotlib.pyplot as plt

    x = np.linspace(5, 8, 100)
    A, K, B, M, nu = 0.1e-5, 1e-5, 10, 7, 1
    y = genlogistic(x, A, K, B, M, nu)
    y *= np.array([uniform(.9, 1.1) for xx in x])
    plt.plot(x, y, "o")

    fitter = T_R_genlogistic(x, y)
    Tc, Rc = fitter.fit()
    print("Tc, Rc fit =", Tc, Rc)
    print("Fit parameters =", fitter.popt)
    xfit, yfit = fitter.build_fitcurve()
    plt.plot(xfit, yfit, "-")
    plt.plot(Tc, Rc, "s")
    plt.pause(5)

def test3():
    """Test fit with real datafile."""
    import matplotlib.pyplot as plt
    import pandas as pd
    import glob

    if len(sys.argv) > 5:
        guess = tuple(map(float, sys.argv[1:]))
    else:
        guess = None

    dfiles = glob.glob("*.dat")
    for dfile in dfiles:
        data = pd.read_table(dfile, sep='\s+', comment="#")
        x, y = (data['T'], data["Vac_device"])
        plt.plot(x, y, "o", label=dfile)
        plt.legend(loc=2)

        if len(sys.argv) > 5:
            y2 = genlogistic(x, *guess)
            plt.plot(x, y2, "-")
        plt.pause(5)

        fitter = T_R_genlogistic(x, y)
        Tc, Rc, perr = fitter.fit()
        print("Tc, Rc, error =", Tc, Rc, perr)
        print("Fit parameters =", fitter.popt)
        xfit, yfit = fitter.build_fitcurve()
        plt.plot(xfit, yfit, "-")
        #plt.plot(Tc, Rc, "s")
        plt.pause(5)
        plt.cla()
    #plt.pause(10)

if __name__ == "__main__":
    test3()
