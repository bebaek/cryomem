"""Superconducting transition temperature analysis"""
from scipy.optimize import curve_fit
import numpy as np

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
    """Superconducting R(T) data fitting class"""
    def __init__(self, T, R):
        self.T, self.R = T, R
        self.fitfunc = genlogistic

    def fit(self):
        """Fit R(T) with general logistic function and return Tc."""
        A = np.amin(self.R)
        K = np.amax(self.R)
        B = 5/(np.amax(self.T) - np.amin(self.T))
        M = np.mean(self.T)
        nu = 0.5

        guess = (A, K, B, M, nu)
        self.popt, self.pcov = curve_fit(self.fitfunc, self.T, self.R, guess)
        return self.popt[3]

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
