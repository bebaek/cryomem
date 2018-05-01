# -*- coding: utf-8 -*-
"""
JJ I-V data manipulation

BB, 2014
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import quad, dblquad
from time import time
from multiprocessing import Pool

# RSJ function for fit. i: array.
def vrsj(i, ic, rn, io, vo):
    if ic < 0 or rn < 0:
        v = 1e10
    else:
        v = np.zeros(len(i))
        n = i>io+ic; v[n] = rn*np.sqrt((i[n]-io)**2-ic**2)+vo
        n = i<io-ic; v[n] = -rn*np.sqrt((i[n]-io)**2-ic**2)+vo
        n = np.logical_and(i>=io-ic, i<=io+ic); v[n]=vo
    return v

def v_rsj_asym(i, ic_pos, ic_neg, rn, io, vo):
    """Return voltage with asymmetric Ic's in RSJ model"""
    if ic_pos < 0 or ic_neg > 0 or rn < 0:      # set boundaries for fitting
        v = 1e10
    else:
        v = np.zeros(len(i))
        n = i>io+ic_pos; v[n] = rn*np.sqrt((i[n]-io)**2-ic_pos**2)+vo
        n = i<io-ic_neg; v[n] = -rn*np.sqrt((i[n]-io)**2-ic_neg**2)+vo
        n = np.logical_and(i>=io-ic_pos, i<=io+ic_neg); v[n]=vo
    return v

# AH model
def v_ah(i, ic, rn, io, vo, t):
    e = 1.60217657e-19
    hbar = 1.05457173e-34
    k = 1.3806488e-23
    
    v = np.zeros(len(i))
    if t>0 and t<100 and ic>=0 and rn>=0:
        r = hbar*ic/(e*k*t)
        x = (i-io)/ic
        #print('Ic, rn, t, gamma = %e, %f, %f, %f'%(ic, rn, t, r))
        
        n = 0
        for xx in x:
            if xx == 0:
                v[n] = 0
            elif xx > 0:
                f = lambda theta: np.exp(.5*r*(xx*theta + np.cos(theta)))
                finv = lambda theta: 1/f(theta)
                a1 = 1/(np.exp(np.pi*r*xx) - 1)*quad(f, 0, 2*np.pi)[0]*quad(finv, 0, 2*np.pi)[0]
                
                f2 = lambda theta2, theta1: f(theta1)/f(theta2)
                a2 = dblquad(f2, 0, 2*np.pi, lambda theta: theta, lambda theta: 2*np.pi)[0]
                
                v[n] = vo + ic*rn*4*np.pi/r/(a1 + a2)
            
            else:   # negative current (somehow glitchy otherwise)
                xx = -xx
                f = lambda theta: np.exp(.5*r*(xx*theta + np.cos(theta)))
                finv = lambda theta: 1/f(theta)
                a1 = 1/(np.exp(np.pi*r*xx) - 1)*quad(f, 0, 2*np.pi)[0]*quad(finv, 0, 2*np.pi)[0]
                
                f2 = lambda theta2, theta1: f(theta1)/f(theta2)
                a2 = dblquad(f2, 0, 2*np.pi, lambda theta: theta, lambda theta: 2*np.pi)[0]
                
                v[n] = vo - ic*rn*4*np.pi/r/(a1 + a2)
            #stdout.write('%d\t'%n)
            n += 1
    return v
    
def v_ah_caller(arg): return v_ah(*arg)

# multiprocessing version of v_ah()
def v_ah_mp(i, ic, rn, io, vo, t):
    
    nproc = 3
    n = len(i)
    args = []
    v = np.zeros(n)
    print('Ic = %e, Rn = %f, Tn = %f'%(ic, rn, t))
    print(i, io, vo)
    for m in range(nproc):
        args += [(i[m:n:nproc],ic,rn,io,vo,t)]
    #print (args)
    
    # run processes    
    pool = Pool(processes=nproc)
    results = pool.map(v_ah_caller, args)
    pool.close(); pool.join()   # clean up processes
    #print(results, pl.shape(results))
    
    #v = pl.ravel(pl.transpose(pl.vstack(results)))
    for m in range(nproc):
        v[m:n:nproc] = results[m]
    #print (v, pl.shape(v))
    return v

class JJIV:
    def __init__(self, i, v):
        self.set_iv(i, v)

    def set_iv(self, i, v):
        self.i, self.v = [i, v]
        self.ndata1 = len(i)
#        self.io, self.vo, self.ic, self.rn, self.tn = [0,0,0,0,37]
#        
#        # fit std dev        
#        self.io_err, self.vo_err, self.ic_err, self.rn_err = [0,0,0,0]
#        self.tn_err = 0

    # 2-step RSJ fitter (bb, Aug 2015). Results are not strictly RSJ.
    def fit2rsj_2step(self, guess = [10, 1, 0, 0]):
        # 1st fit
        popt, pcov = curve_fit(vrsj, self.i, self.v, guess)
        self.ic, self.rn, self.io, self.vo = popt
        if np.shape(pcov)==(4,4):
            self.ic_err, self.rn_err, self.io_err, self.vo_err =\
              np.sqrt(np.diag(pcov))       # std deviations of param estimates
        else:
            self.ic_err, self.rn_err, self.io_err, self.vo_err =\
              (np.inf, np.inf, np.inf, np.inf)
        #print('popt: ', popt)
        #print('pcov: ', pcov)
        
        # 2nd fit; narrower range
        k = abs(self.i) < max([self.ic*1.5, 0.3*max(self.i)]) # narrower range
        if sum(l == True for l in k) > 50:
            i2, v2 = (self.i[k], self.v[k])
            guess2 = popt
            popt2, pcov2 = curve_fit(vrsj, i2, v2, guess2)
            self.ic2, self.rn2, self.io2, self.vo2 = popt2
            if np.shape(pcov2)==(4,4):
                self.ic_err2, self.rn_err2, self.io_err2, self.vo_err2 =\
                  np.sqrt(np.diag(pcov2))    # std deviations of param estimates
            else:
                self.ic_err2, self.rn_err2, self.io_err2, self.vo_err2 =\
                  (np.inf, np.inf, np.inf, np.inf)

            self.ic = self.ic2      # replace 1st fitted Ic with 2nd
            self.ic_err = self.ic_err2

     # best working fitter (RSJ). give good initial guess=[ic, rn, io, vo]
    def fit2rsj(self, guess = [10, 1, 0, 0]):
        #print(guess)
        #import pylab; pylab.plot(self.i, self.v); pylab.show()
        popt, pcov = curve_fit(vrsj, self.i, self.v, guess)
        self.ic, self.rn, self.io, self.vo = popt
        #print(np.shape(pcov))
        if np.shape(pcov)==(4,4):
            self.ic_err, self.rn_err, self.io_err, self.vo_err =\
              np.sqrt(np.diag(pcov))       # std deviations of param estimates
        else:
            self.ic_err, self.rn_err, self.io_err, self.vo_err =\
              (np.inf, np.inf, np.inf, np.inf)

    # full fit with AH theory. give good initial guess=[Ic, Rn, Io, Vo, T]
    def fit2ah_full(self, guess = [10, 1, 0, 0, 10]):
        popt, pcov = curve_fit(v_ah_mp, self.i, self.v, guess)
        self.ic, self.rn, self.io, self.vo, self.tn = popt
        self.ic_err, self.rn_err, self.io_err, self.vo_err, self.tn_err =\
          np.sqrt(np.diag(pcov))       # std deviations of param estimates

    # quick fit for Ic, Rn, T only.
    def fit2ah_ic_rn_tn(self, guess):
        fitfunc = lambda i, ic, rn, t: v_ah_mp(i, ic, rn, guess[2], guess[3], t)
        guess2 = np.array([guess[0], guess[1], guess[4]])
        popt, pcov = curve_fit(fitfunc, self.i, self.v, guess2, maxfev=0)
        self.ic, self.rn, self.tn = popt
        self.ic_err, self.rn_err, self.tn_err = np.sqrt(np.diag(pcov)) # stdev

    # quicker fit for Ic, Rn only.
    def fit2ah_ic_rn(self, guess):
        def fitfunc_ic_rn(i, ic, rn):
            return v_ah_mp(i, ic, rn, guess[2], guess[3], guess[4])
            
        #fitfunc_ic_rn = lambda i, ic, rn: v_ah_mp(i, ic, rn, guess[2], guess[3], guess[4])
        guess2 = np.array([guess[0], guess[1]])
        popt, pcov = curve_fit(fitfunc_ic_rn, self.i, self.v, guess2)
        self.ic, self.rn = popt
        self.tn = guess[4]
        self.ic_err, self.rn_err = np.sqrt(np.diag(pcov)) # stdev

    # quicker fit for Ic only.
    def fit2ah_ic(self, guess):
        fitfunc = lambda i, ic: v_ah_mp(i, ic, guess[1], guess[2], guess[3], guess[4])
        newguess = np.array([guess[0]])
        popt, pcov = curve_fit(fitfunc, self.i, self.v, newguess)
        self.ic = popt
        self.tn = guess[4]
        self.ic_err, = np.sqrt(np.diag(pcov)) # stdev
        
    # linear fit for a resistor
    def getRfit(self):
        self.rn = np.polyfit(self.i, self.v, 1)[0]
        self.ic = 0; self.io = 0; self.vo =0;
        
    def getRn(self):
        i=self.i; v=self.v; ic=self.ic
        pts = 10
        if (ic>0):
            # in case of not enough I range
            iref = np.amin([ 2.5*ic,np.amax(i)*0.9 ])
        else:
            iref = np.amax(i)*0.9
        i1 = i[i>iref]
        i2 = i[i<-iref]
        v1 = v[i>iref]
        v2 = v[i<-iref]
        rn = (np.mean(v1[:pts])-np.mean(v2[:pts])) \
    		/(np.mean(i1[:pts])-np.mean(i2[:pts]))	# little averaging
        #rn = np.polyfit()
    #    np.figure(2)
    #    np.hold(1)
    #    np.plot(self.i,self.v)
    #    np.plot(i1[:4],v1[:4],'s')
    #    np.plot(i2[:4],v2[:4],'s')
    #    pl.hold(0)
    #    pl.show()
    #    time.sleep(3)
        self.rn = rn
        return(rn)

    # build RSJ IV array
    def build_iv_rsj(self, num=200):
        imax = np.amax(self.i)
        imin = np.amin(self.i)
        i = np.array(np.linspace(imin,imax,num))
        v = np.zeros(num)
        n = i>self.io+self.ic; v[n] = self.rn*np.sqrt((i[n]-self.io)**2-self.ic**2)+self.vo
        n = i<self.io-self.ic; v[n] = -self.rn*np.sqrt((i[n]-self.io)**2-self.ic**2)+self.vo
        n = np.logical_and(i>=self.io-self.ic, i<=self.io+self.ic); v[n]=self.vo
        self.i_rsj = i; self.v_rsj = v
        return i,v

    # build AH IV array
    def build_iv_ah(self, num=50):
        imax = np.amax(self.i)
        imin = np.amin(self.i)
        i = np.array(np.linspace(imin,imax,num))
        v = v_ah(i, self.ic, self.rn, self.io, self.vo, self.tn)
        self.i_ah = i; self.v_ah = v
        return i,v

if __name__=='__main__':
    
    import pylab as pl    
    t_i = time()
    path = '../../Cryogenic Probe Station/20140714_nanopillar remeasure/'
    filename = 'VI_043_VItrace-H_B140211_chip22_jj4_Hset4 4000OeR_40.txt'  # low Ic
    #filename = 'VI_043_VItrace-H_B140211_chip22_jj4_Hset4 4000OeR_70.txt' # high Ic
    data = np.loadtxt(path + filename)
    i = data[:,0]; v = data[:, 1]
    np.plot(i, v, '-')
    jj = JJIV(i, v)
    units = np.array([1e-6, 1, 1e-6, 1e-6])
    initguess = np.array([10, 1, 0, 30])*units
    print (initguess)
    jj.geticfit2(initguess)
    print ('RSJ fit: ', jj.ic, jj.rn, jj.io, jj.vo)
    jj.build_ivrsj()
    pl.plot(jj.irsj, jj.vrsj); pl.draw()
    
    # uncomment to fit
    initguess = pl.array([jj.ic, jj.rn, jj.io, jj.vo, 27])   # add temperature
    jj.fit_ah_ic(initguess)
    print ('AH fit: ', jj.ic, jj.rn, jj.io, jj.vo, jj.t)
    
    # uncomment to just use RSJ fit params + T.
    #jj.ic *= 1.1; jj.rn *= 1.02
    #jj.t = 40
    
    jj.build_iv_ah()
    pl.plot(jj.i_ah, jj.v_ah)

    t_f = time(); print ('Duration = ', t_f - t_i)
    pl.show()
    print ('Done.')
