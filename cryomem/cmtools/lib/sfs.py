# -*- coding: utf-8 -*-
"""
SFS JJ data fitting etc.

@author: burm
"""

#import pylab as pl
import numpy as np
from scipy.optimize import curve_fit, root
from scipy.special import sici
from scipy.integrate import quad

e = 1.60217657e-19
hbar = 1.05457173e-34
kb = 1.3806488e-23
    
def vc_SFS_sinc(d, prefac, xi, d0, phi0):
    """Return simple clean limit characteristic voltage in sinc function
    """
    #print(prefac, xi, d0, phi0)
    vc = prefac * abs( np.sin( (d-d0)/xi+phi0 ) / ((d-d0)/xi) )
    return vc

def vc_SFS_sinc2(d, prefac, xi, phi1, phi2):
    """Return phenomenological fit Vc; theoretically not justified
    """
    #print(prefac, xi, d0, phi0)
    vc = prefac * abs( np.sin( d/xi+phi1 ) / (d/xi+phi2) )
    return vc

def psi_SFS_simple3d(d, prefac, xi, d0):
    """Return simple clean limit pair wavefunction from Demler
    """
    a = (d - d0)/xi
    (si,ci) = sici(a)
    vc = abs(prefac*(-np.pi/2*(a) + a*sici(a)[0] + np.cos(a)))
    return vc

def vc_SFS_sinc_old(d, **kwargs):
    """Return simple clean limit characteristic voltage in sinc function
    
    Keyword arguments:
    d_o -- thickness offset
    xi_f -- characteristic length
    phi_o -- phase offset
    prefac -- prefactor
    """
    xi_f,d_o,phi_o,prefac = (kwargs[key] for key in 
            ('xi_f','d_o','phi_o','prefac'))
    print(d_o, xi_f, phi_o, prefac)
    vc = prefac * abs( np.sin( (d+d_o)/xi_f+phi_o ) / (d+d_o/xi_f) ) # wrong
    return vc

def vc_SFS_B82_nearTc(d, prefac, xi_f, doff):
    """clean limit vc-d by Buzdin (1982)
    Transparent interface.
    """
    a = (d - doff)/xi_f
    (si,ci) = sici(a)
    vc = prefac * abs( -1/2*(a**2*ci - a*np.sin(a) + np.cos(a)) )
    return vc

def _IsRn_SFS_B82(phi, d, xi, delta, t, **kwargs):
    """clean limit supercurrent-phase relationship in Buzdin-1982
    xi = vf*hbar/2Ex
    kwargs for numpy.quad
    """
    a = d/xi; t=kb*t; delta = e*delta
    prefac = np.pi*delta*a**2/2/e
    f = lambda y: \
        prefac*y**(-3) \
        *(np.sin((phi-y)/2)*np.tanh(delta*np.cos((phi-y)/2)/(2*t)) \
          + np.sin((phi+y)/2)*np.tanh(delta*np.cos((phi+y)/2)/(2*t)))
    res = quad(f, a, np.inf, **kwargs)
    return res[0]

# Vectorized caller of _IsRn_SFS_B82
IsRn_SFS_B82 = np.vectorize(_IsRn_SFS_B82)

def Vc_SFS_B82(d, xi, delta, t, **kwargs):
    """clean limit supercurrent-phase relationship in Buzdin-1982
    kwargs for numpy.quad
    """
    t2 = kb*t; delta2 = e*delta
    def f(d):       # per thickness
        phi = np.linspace(0, np.pi, 100)
        IsRn = IsRn_SFS_B82(phi, d, xi, delta, t, **kwargs)
        imax = np.argmax(abs(IsRn))
        Vc, phi_max = abs(IsRn[imax]), phi[imax]
        return Vc, phi_max

    return np.vectorize(f)(d)


def Vc_SFS_B82_slow(d, xi, delta, t, guess, **kwargs):
    """clean limit supercurrent-phase relationship in Buzdin-1982
    kwargs for numpy.quad
    """
    t2 = kb*t; delta2 = e*delta
    def f(d):
        a = d/xi
        prefac = np.pi*delta2*a**2/2/e

        def f2(phi):    # derivative
            f2b = lambda y: y**(-3)*( \
                np.cos((phi-y)/2)*np.tanh(delta2*np.cos((phi-y)/2)/(2*t2))\
              + np.sin((phi-y)/2)\
                *np.cosh(delta2*np.cos((phi-y)/2)/(2*t2))**(-2)\
                *delta2*(-np.sin((phi-y)/2))/(2*t2)\
              + np.cos((phi+y)/2)*np.tanh(delta2*np.cos((phi+y)/2)/(2*t2))\
              + np.sin((phi+y)/2)\
                *np.cosh(delta2*np.cos((phi+y)/2)/(2*t2))**(-2)\
                *delta2*(-np.sin((phi+y)/2))/(2*t2))
            return quad(f2b, a, np.inf, **kwargs)[0]

        def f3(phi):    # search for solution only in 0 < phi < pi
            if phi >= 0 and phi < np.pi:
                return f2(phi)
            elif phi < 0:
                return f2(0)*(phi-np.pi)**2
            elif phi >= np.pi:
                return f2(np.pi)*phi**2

        vroot = np.vectorize(lambda g: root(f3, g))
        sol = vroot(guess)
        phis = [sol[k].x for k in range(len(guess))]
        IsRns = IsRn_SFS_B82(phis, d, xi, delta, t, **kwargs)
        imax = np.argmax(abs(IsRns))
        Vc, phi_max = abs(IsRns[imax]), phis[imax]
        return Vc, phi_max

    return np.vectorize(f)(d)

# Vectorized caller of _Vc_SFS_B82
#Vc_SFS_B82 = np.vectorize(_Vc_SFS_B82)

def vc_vs_d_SFS_clean(d, xi_f, doff, prefac):
    """clean limit vc-d by Buzdin (1982)
    Transparent interface. Deprecated
    """
    a = (d - doff)/xi_f
    (si,ci) = sici(a)
    vc = prefac * abs( -1/2*(a**2*ci - a*np.sin(a) + np.cos(a)) )
    return vc

def fit_vc_SFS(func, x, y, **kwargs):
    """Return fit params of Vc(d); 

    Arguments:
    func -- fit function; e.g., vc_SFS_sinc
    x, y -- list of measurement data

    Keyword arguments:
    d_o -- thickness offset
    xi_f -- characteristic length
    phi_o -- phase offset
    prefac -- prefactor
    """
    guess = (kwargs[key] for key in 
            ('xi_f','d_o','phi_o','prefac'))
    popt, pcov = curve_fit(func, x, y, guess)
    self.xi_f, self.doff, self.prefac = popt


class sfs_clean_sinc:
    def __init__(self):
        self.xi_f = 0
        self.doff = 0
        self.prefac = 0
        self.d_fitted = np.zeros(300)
        self.d_fitted = np.zeros(300)

    def setdata_d_vc(self, d, vc):
        self.d = d
        self.vc = vc

    def fit_vc_vs_d(self, guess = [1, 0, 1]):
        """fitter
        """
        popt, pcov = curve_fit(vc_vs_d_SFS_clean_GL, self.d, self.vc, guess)
        self.xi_f, self.doff, self.prefac = popt

    def build_d_vc_arr(self, **kwargs):
        """Return theoretical Vc array

        Keyword arguments:
        ds -- thickness array; overrides n
        n -- number of pts
        """
        if 'ds' in kwargs:
            ds = kwargs['ds']
        else:
            n = kwargs.get('n', 2000)
            ds = np.linspace(self.doff, np.amax(self.d), n)
        vcs = vc_vs_d_SFS_clean(ds, self.xi_f, self.doff, self.prefac)
        return ds, vcs

    def build_d_vc(self, n=1000):
        #dmax = np.amax(self.d)
        dmax = 20
        #dmin = np.amin(self.d)
        dmin = self.doff*1.25
        d = np.array(np.linspace(dmin,dmax,n))
        vc = vc_vs_d_SFS_clean(d, self.xi_f, self.doff, self.prefac)
        return d, vc

    def setparams(self, xi_f, doff, prefac):
        self.xi_f = xi_f
        self.doff = doff
        self.prefac = prefac

    def get_xi_f(self):
        return self.xi_f

    def getdoff(self):
        return self.doff

    def getprefac(self):
        return self.prefac

class sfs_clean(sfs_clean_sinc):
    def fit_vc_vs_d(self, guess = [1, 0, 1]):
        """fitter
        """
        popt, pcov = curve_fit(vc_vs_d_SFS_clean, self.d, self.vc, guess)
        self.xi_f, self.doff, self.prefac = popt

    def build_d_vc_arr(self, **kwargs):
        """Return theoretical Vc array

        Keyword arguments:
        ds -- thickness array; overrides n
        n -- number of pts
        """
        if 'ds' in kwargs:
            ds = kwargs['ds']
        else:
            n = kwargs.get('n', 2000)
            ds = np.linspace(self.doff, np.amax(self.d), n)
        vcs = vc_vs_d_SFS_clean(ds, self.xi_f, self.doff, self.prefac)
        return ds, vcs

    def build_d_vc(self, n=1000):
        #dmax = np.amax(self.d)
        dmax = 20
        #dmin = np.amin(self.d)
        dmin = self.doff
        d = np.array(np.linspace(dmin,dmax,n))
        vc = vc_vs_d_SFS_clean(d, self.xi_f, self.doff, self.prefac)
        return d, vc

if __name__=='__main__':

    import matplotlib.pyplot as plt

    xi_f_all = 1.0
    d_dead = 0.75
    doff_P = d_dead - 0.2
    doff_AP = 0.5+doff_P
    prefac_all = 6

    path = r'..\..\20130531_NiFeNb-Ni\\'
    data = np.loadtxt(path+r'vc vs d_P.txt')
    d = data[:,0]
    vc = data[:,1]
    sfs = sfs_clean()
    sfs.setdata_d_vc(d[:-1], vc[:-1])
    sfs.fit_vc_vs_d(guess = [1, 0.1, 6])
    xi_f = sfs.get_xi_f(); doff = sfs.getdoff(); prefac = sfs.getprefac()
    print('xi_f = %f, doff = %f, prefactor = %f'%(xi_f, doff, prefac))
    sfs.setparams(xi_f_all, doff_P, prefac_all)
    d_fit, vc_fit = sfs.build_d_vc()
    plt.subplot(1,1,1)
    plt.plot(d, vc, 'bs', ms=10, label='P')
    plt.plot(d_fit, vc_fit, 'b-')
    #plt.semilogy(d, vc, 'o')
    #plt.semilogy(d_fit, vc_fit, '-')

    path = r'..\..\20130531_NiFeNb-Ni\\'
    data = np.loadtxt(path+r'vc vs d_AP.txt')
    d = data[:,0]
    vc = data[:,1]
    sfs = sfs_clean()
    sfs.setdata_d_vc(d[:-1], vc[:-1])
    sfs.fit_vc_vs_d(guess = [.8, 0, 6])
    #sfs.fit_vc_vs_d(guess = [.8, -0.5, 6])
    xi_f = sfs.get_xi_f(); doff = sfs.getdoff(); prefac = sfs.getprefac()
    print('xi_f = %f, doff = %f, prefactor = %f'%(xi_f, doff, prefac))
    sfs.setparams(xi_f_all, doff_AP, prefac_all)
    d_fit, vc_fit = sfs.build_d_vc()
    plt.subplot(1,1,1)
    plt.plot(d, vc, 'ro', ms=8, label='AP')
    plt.plot(d_fit, vc_fit, 'r-')
    #plt.semilogy(d, vc, 'o')
    #plt.semilogy(d_fit, vc_fit, '-')

    plt.xlim([0, 5])
    plt.legend(frameon=False, loc=1)
    plt.xlabel('Ni Thickness (nm)')
    plt.ylabel('IcRn (uV)')
    plt.show()
    print('Done.')
