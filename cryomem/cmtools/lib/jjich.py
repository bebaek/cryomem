# -*- coding: utf-8 -*-
"""
JJ Ic-H measurement data manipulation

@author: burm
"""

from __future__ import division
import sys
#sys.path.insert(0,r'..')
import numpy as np
import matplotlib as plt
from scipy.optimize import curve_fit
from scipy.special import jn

#phi0 = 2.0679e-7 # CGS, use this for some ncomm plots
phi0 = 2.0679e-15 # MKS

class jjich:
    def __init__(self, h=[], ic=[], ho=0, func='airy'):
        self.h = h
        self.ic = ic
        self.ho = ho
        if func == 'airy':
            self.func = self.airypat
        elif func == 'fraunhofer':
            self.func = self.fraunhoferpat
        # need to preset prefactor, area, ho?
        #self.icfit = np.zeros(300)

    # Airy pattern: circular/elliptic junction
    def airypat(self, h, ic0, area, ho):
        ic = ic0*abs(jn(1, np.pi*area*(h-ho)/phi0)/(0.5*np.pi*area*(h-ho)/phi0))
        return ic

    # Fraunhofer pattern: rectangular junction
    def fraunhoferpat(self, h, ic0, area, ho):
        ic = ic0*abs(np.sin(np.pi*area*(h-ho)/phi0)/(np.pi*area*(h-ho)/phi0))
        return ic

    # curve fitter
    def fitich(self, guess = [1, 1e-13, 0]):
        popt, pcov = curve_fit(self.func, self.h, self.ic, guess)
        self.pref, self.area, self.ho = popt
        return popt, pcov

    # fitter with fixed H offset
    def fitich_fixho(self,  guess = [1, 1e-13]):
        f = lambda x, pref, area: self.func(x, pref, area, self.ho)
        popt, pcov = curve_fit(f, self.h, self.ic, guess)
        self.pref, self.area = popt

   # build fit curve
    def buildfitich(self, num=100, minfac=1, maxfac=1):
        hmax = np.amax(self.h)
        hmin = np.amin(self.h)
        print('hmax = ', hmax, 'hmin = ', hmin)
        h = np.array(np.linspace((hmin+hmax)/2+(hmin-hmax)/2*minfac, \
        (hmin+hmax)/2-(hmin-hmax)/2*maxfac, num))
        #ic = np.zeros(num)
        self.hfit = h
        self.icfit = self.func(h, self.pref, self.area, self.ho)
        return self.hfit, self.icfit

if __name__=='__main__':

    path = r'..\..\20130606_NiFeNb-Ni\\'
    data = np.loadtxt(path+'IcH_035_VIH_B130603_chip52_0.9v0.8_detrap-flux after 15A.txt')
    #data = np.loadtxt(path+'IcH_037_VIH_B130603_chip52_1.4v1.0_detrap flux after 15A.txt')
    h = data[:,0]  # in Oe
    ic = data[:,1]  # in mA
    hdispfactor = 1   # in Oe
    plt.plot(h*hdispfactor, ic, 'o')

    #i1 = int(len(h)*4.3/8)
    #i2 = int(len(h)*6.3/8)
    i1 = int(len(h)*5.2/8)
    i2 = int(len(h)*6.5/8)
    print(i1, i2)
    myich = jjich(h[i1:i2], ic[i1:i2])
    initguess = [0.6, 2e-9, 5]
    #initguess = [3, 5e-13, 2.5e-4]
    myich.fitich_fixho(initguess)
    myich.buildfitich(minfac=1, maxfac=1)
    print('parameters = ', myich.pref, myich.area, myich.ho)
    plt.plot(myich.hfit*hdispfactor, myich.icfit, '-')

    i1 = int(len(h)*0.3/8)
    i2 = int(len(h)*2.3/8)
    print(i1, i2)
    myich = jjich(h[i1:i2], ic[i1:i2])
    initguess = [0.6, 2e-9, -5]
    #initguess = [3, 5e-13, 2.5e-4]
    myich.geticfit(initguess)
    myich.buildfitich(minfac=2, maxfac=1.5)
    print('parameters = ', myich.pref, myich.area, myich.ho)
    plt.plot(myich.hfit*hdispfactor, myich.icfit, '-')

    plt.show()
    print('Done.')
