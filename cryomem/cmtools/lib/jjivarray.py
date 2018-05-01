# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Analyze JJ IV curve array (core).

BB, 2014
"""

import numpy as np
from .jjiv import JJIV
import sys

# multiple IV curves with a control param
# called by JJIVs([ctl1, ctl2, ...], i, v)
class JJIVArray(JJIV):
    def __init__(self, c, iarr, varr):
        self.c, self.iarr, self.varr = c, iarr, varr
        self.cdim = np.shape(c)[1]
        self.ndata2 = len(self.iarr)    # 2 means 2nd lowest dimension
        
        # initialize fitting params        
        self.icarr, self.rnarr, self.ioarr, self.voarr =\
          [np.zeros(self.ndata2) for n in range(4)]
        self.tnarr = np.ones(self.ndata2)*37    # reasonable noise temperature
        self.ic_err_arr, self.rn_err_arr, self.io_err_arr, self.vo_err_arr,\
          self.tn_err_arr = [np.zeros(self.ndata2) for n in range(5)] # std dev
    
    def fit2rsj_array(self, guess=[1e-5, 1, 0, 0], method=0): # fit to RSJ model
        if type(guess)==list:
            guess = np.array(guess)
        previc = guess[0]; prevrn = guess[1]
        for n in range(self.ndata2):
        #~ for n in range(5):
            #sys.stdout.write('%8.4f '%data.i1[n])
            self.set_iv(self.iarr[n], self.varr[n])
            try:
                done = False; nrep = 0
                while not done:
                    if method == 0:
                        self.fit2rsj(guess)        # simple RSJ fit
                    elif method == 1:
                        self.fit2rsj_2step(guess)   # 2-step RSJ fit
                    self.icarr[n], self.rnarr[n], self.ioarr[n], self.voarr[n] \
                      = [self.ic, self.rn, self.io, self.vo]
                    self.ic_err_arr[n], self.rn_err_arr[n], self.io_err_arr[n],\
                      self.vo_err_arr[n]\
                      = [self.ic_err, self.rn_err, self.io_err, self.vo_err]
                    previc = self.ic; prevrn = self.rn
                    #if n < 5:
                    #    guess = [self.ic, self.rn, self.io, self.vo]
                    if n > -1:	# update initial guess
                        #guess = .9*guess + \
                        #  .1*np.array([self.ic, self.rn, self.io, self.vo])
                        guess = np.array([\
                                .95*guess[0] + .05*self.ic,\
                                .98*guess[1] + .02*self.rn,\
                                .95*guess[2] + .05*self.io,\
                                .9*guess[3] + .1*self.vo ])
                    
                    # check if the fit is good
                    nrep += 1
                    #~ if n<4:
                        #~ print(self.rn_err)
                    if (self.rn_err/self.rn < 1e2) or (nrep > 5):
                        done = True
                    else:
                        print('Fit not good. Index: %d\tTrial: %d'%(n, nrep))
                        
            except RuntimeError:
                print ('Can\'t fit %f!'%self.c[n][0])
                self.icarr[n] = previc; self.rnarr[n] = prevrn
        
    # fit to Ambegaokar model. Take guess matrix (e.g. from RSJ fit results).
    # guess_arr = [ic_arr, rn_arr, io_arr, vo_arr, tn_arr]
    # f: external function used to deal with intermediate results
    def fit2ah_ic_rn_tn_array(self, guess_arr, f_report):
        #ic0arr, rn0arr, ioarr, voarr, tn0arr = [guess_arr[n] for n in range(5)]
        #print rsj[1:2]; exit(1)
        prev = [0,0,guess_arr[0,4]]
        for n in range(self.ndata2):
            #sys.stdout.write('%8.4f '%data.i1[n])
            self.set_iv(self.iarr[n], self.varr[n])
            try:
                self.fit2ah_ic_rn_tn(guess_arr[n])
                self.icarr[n], self.rnarr[n], self.tnarr[n]\
                  = self.ic, self.rn, self.tn
                self.ic_err_arr[n], self.rn_err_arr[n], self.tn_err_arr[n] =\
                  [self.ic_err, self.rn_err, self.tn_err]
                prev = [self.icarr[n], self.rnarr[n], self.tnarr[n]]
            except RuntimeError:
                print ('Can\'t fit %f!'%self.c[n][0])
                self.icarr[n], self.rnarr[n], self.tnarr[n] = prev
                self.ic_err_arr[n], self.rn_err_arr[n], self.tn_err_arr[n]\
                  = [0, 0, 0]
#            results = [self.ic_arr, self.rn_arr, self.io_arr, self.vo_arr,\
#              self.tn_arr, self.ic_err_arr, self.rn_err_arr, self.io_err_arr,\
#              self.vo_err_arr, self.tn_arr][:][:(n+1)]
            f_report(n)  # send out (intermediate) processed results

    # fit to Ambegaokar model; fixed tn
    def fit2ah_ic_rn_array(self, guess_arr, func_report):
        prev = [0,0]
        for n in range(self.ndata2):
            self.set_iv(self.iarr[n], self.varr[n])
            try:
                self.fit2ah_ic_rn(guess_arr[n])
                self.icarr[n], self.rnarr[n] = self.ic, self.rn
                self.ic_err_arr[n], self.rn_err_arr[n] =\
                  [self.ic_err, self.rn_err]
                prev = [self.icarr[n], self.rnarr[n]]
            except RuntimeError:
                print ('Can\'t fit %f!'%self.c[n][0])
                self.icarr[n], self.rnarr[n] = prev
#            results = [self.ic_arr, self.rn_arr, self.io_arr, self.vo_arr,\
#              self.tn_arr, self.ic_err_arr, self.rn_err_arr, self.io_err_arr,\
#              self.vo_err_arr, self.tn_arr][:][:(n+1)]
            func_report(n)  # send out (intermediate) processed results
    
#    def fit2ah_ic_rn_array_old(self, fn_rsj, tn):
#        rsj = np.transpose(np.loadtxt(fn_rsj, skiprows=1)[self.idx])
#        ic0, rn0, io, vo = [rsj[n] for n in range(1+self.cdim,5+self.cdim)]
#        #print rsj[1:2]; exit(1)
#        prev = [0,0,tn]
#        for n in range(self.ndata2):
#            #sys.stdout.write('%8.4f '%data.i1[n])
#            jj = JJIV(self.i[n], self.v[n])
#            try:
#                jj.fit2ah_ic_rn([ic0[n], rn0[n], io[n], vo[n], tn])
#                self.ic[n], self.rn[n], self.io[n], self.vo[n], self.tn[n] = \
#                    [jj.ic, jj.rn, io[n], vo[n], tn]
#                self.ic_err[n], self.rn_err[n] = [jj.ic_err, jj.rn_err]
##                self.ic[n], self.rn[n], self.io[n], self.vo[n], self.tn[n] = \
##                    [1, 1, 1, 1, 1]
##                self.ic_err[n], self.rn_err[n] = [1, 1]
#                sys.stdout.write('[%5d] %f %e %f,\t'%(n, self.c[n][0],\
#                    self.ic[n], self.rn[n]))
#                prev = [self.ic[n], self.rn[n], self.tn[n]]
#            except RuntimeError:
#                print ('Can\'t fit %f!'%self.c[n][0])
#                self.ic[n], self.rn[n], self.t[n] = prev
#            sys.stdout.write('Progress: %d/%d.\n'%(n+1, self.ndata2))
#            self.save_ah(idx=range(n+1))  # save intermediate results
#        
#        return self.ic, self.rn, self.io, self.vo, self.tn

    def fit2fraunhofer(self):
        pass
    
    def fit2airy(self):
        pass


if __name__ == '__main__':
    
    print(sys.version)
