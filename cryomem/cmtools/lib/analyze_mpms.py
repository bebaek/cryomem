# -*- coding: utf-8 -*-
"""
Analyze MPMS (SQUID) data. (high level)

BB, 2015
"""

import pylab as pl
from jjivarray import JJIVArray
#from config import IVArrayTDS, AnalysisCfg
import analysis_params
import datafile
import sys
import plothyst

# MPMS datafile access
class MPMSDataFile:
    


# process IV array data (base class)
class ProcIVArray(JJIVArray):
    def __init__(self, **kwargs):
        self.datafilename = kwargs.get('datafilename', 'test')
        self.step = kwargs.get('step', 1)
        
        # dummy defaults. normally reassigned by read_datafile()
        c = [pl.array([n]) for n in range(5)]
        iarr = pl.array([pl.linspace(-.1, .1, 10) for n in range(5)])
        varr = pl.array([pl.linspace(-.01, .01, 10) for n in range(5)])
        self.idx = list(range(self.step-1, len(iarr), self.step))
        JJIVArray.__init__(self, c, iarr, varr)
        if 'datafilename' in kwargs:
            self.cdim = self.cdim_from_filename(self.datafilename)
            
        # filename/directory settings
        #cfg = AnalysisCfg()
        cfg = analysis_params.AnalysisParams()
        self.path = cfg.datapath
        self.tag = cfg.tag
        self.fn_rsjparams = 'fit2RSJ' + self.tag + '_' + self.datafilename + '.txt'
        self.fn_ahparams = 'fit2AH' + self.tag + '_' + self.datafilename + '.txt'

        # plot settings
        self.fignum_params = 1
        self.fignum_iv = 2
        
    def get_fullpath(self, fn):
        return self.path + '/' + fn
        
    # extract number of control params from filename
    def cdim_from_filename(self, filename):
        if ('_VItrace-H_' in filename) or ('_VItrace-Hpulse_' in filename)\
          or ('_VIH_' in filename):
            cdim = 1
        elif ('_VItrace-IH_' in filename) or ('_VItrace-HI_' in filename):
            cdim = 2
        elif ('_VItrace-HIpulse_' in filename):
            cdim = 3
        else:
            print('Not a valid data file.'); sys.exit(1)
        print('%d scalars.'%cdim)
        return cdim

    def datafit2rsj(self, guess):
        self.fit2rsj_array(guess)
        self.save_rsj_params()
    
    def reportprog(self, n):
        print('[%5d/%d] Ctl1 = %9f, Ic = %9e, Rn = %9f, Tn = %9f'%
          (n+1, self.ndata2, self.c[n,0], self.icarr[n], self.rnarr[n],\
          self.tnarr[n]))
        self.save_ah_params(n)
        
    def datafit2ah_ic_rn_tn(self, tn):
        self.read_rsj_params(step=self.step)
        self.tnarr = pl.ones(self.ndata2)*tn
        guess_arr = pl.transpose(pl.array(
          [self.icarr, self.rnarr, self.ioarr, self.voarr, self.tnarr]))
        self.fit2ah_ic_rn_tn_array(guess_arr, self.reportprog)
    
    def datafit2ah_ic_rn(self, tn):
        self.read_rsj_params(step=self.step)
        self.tnarr = pl.ones(self.ndata2)*tn
        guess_arr = pl.transpose(pl.array(
          [self.icarr, self.rnarr, self.ioarr, self.voarr, self.tnarr]))
        self.fit2ah_ic_rn_array(guess_arr, self.reportprog)

    def plot_raw(self):
        self.fig = pl.figure(figsize=(8,6))
        self.fig.clf()
        
        xv, yv = pl.meshgrid(pl.array(self.idx) + 1, self.iarr[0])
        self.ax = self.fig.add_subplot(211)
        #self.ax.hold(True)
        im = self.ax.pcolormesh(xv, pl.transpose(self.iarr),\
          pl.transpose(self.varr))
        self.fig.colorbar(im)
        self.ax.set_ylabel('I (A)')
        self.ax.set_xlabel('Index')
        
        self.ax2 = self.fig.add_subplot(212)
        #self.ax2.hold(True)
        self.ax2.plot(pl.array(self.idx) + 1, self.c[:,0])
        self.ax2.set_ylabel('Control 1')
        self.ax2.set_xlabel('Index')
        self.ax2.grid(True)
        
        pl.show()
    
    # plot I-V: raw, RSJ fit (need param file), AH fit (need param file).
    def plot_iv(self, idx, **kwargs):
        showrsj = kwargs.get('showrsj', False)
        showah = kwargs.get('showah', False)
        #idx -= 1        
        
        self.fig = pl.figure(self.fignum_iv, figsize=(8,4))
        self.fig.clf()
        
        # measured data        
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.iarr[idx], self.varr[idx], '.')
        
        # fit curves
        if showrsj:
            self.read_rsj_params()
            self.ic = self.icarr[idx]
            self.rn = self.rnarr[idx]
            self.io = self.ioarr[idx]
            self.vo = self.voarr[idx]
            self.set_iv(self.iarr[idx], self.varr[idx])
            self.build_iv_rsj()            
            self.ax.plot(self.i_rsj, self.v_rsj, '-')
        if showah:
            self.read_ah_params()
            if idx == -1:
                newidx = idx
            else:
                newidx = abs(self.idx_ah_params - idx) < .1
            self.ic = self.icarr[newidx]
            self.rn = self.rnarr[newidx]
            self.io = self.ioarr[newidx]
            self.vo = self.voarr[newidx]
            self.tn = self.tnarr[newidx]
            self.set_iv(self.iarr[idx], self.varr[idx])
            self.build_iv_ah()            
            self.ax.plot(self.i_ah, self.v_ah, '-')
        self.ax.set_xlabel('I (A)')
        self.ax.set_ylabel('V (V)')
        self.ax.grid(True)
        self.fig.suptitle(self.datafilename)
        pl.show()
    
    def export_iv(self, idx):
        pass
    
    def save_rsj_params(self):
        mat = pl.vstack((pl.array(self.idx), pl.transpose(self.c),\
          self.icarr, self.rnarr, self.ioarr, self.voarr,\
          self.ic_err_arr, self.rn_err_arr, self.io_err_arr, self.vo_err_arr))
        
        header_c = ''
        for n in range(self.cdim):
            header_c = header_c + 'Control%d '%(n+1)
        header_ = 'Index ' + header_c + \
          'Ic Rn Io Vo Ic_err Rn_err Io_err Vo_err'
        pl.savetxt(self.get_fullpath(self.fn_rsjparams), pl.transpose(mat),\
          header=header_)

    def save_ah_params(self, n):
        n += 1
        mat = pl.vstack((pl.array(self.idx)[:n], pl.transpose(self.c[:n]),\
          self.icarr[:n], self.rnarr[:n], self.ioarr[:n], self.voarr[:n],\
          self.tnarr[:n],\
          self.ic_err_arr[:n], self.rn_err_arr[:n], self.io_err_arr[:n],\
          self.vo_err_arr[:n], self.tn_err_arr[:n]))
        n -= 1
        
        header_c = ''
        for m in range(self.cdim):
            header_c = header_c + 'Control%d '%(m+1)
        header_ = 'Index ' + header_c + \
          'Ic Rn Io Vo Tn Ic_err Rn_err Io_err Vo_err Tn_err'

        pl.savetxt(self.get_fullpath(self.fn_ahparams), pl.transpose(mat),\
          header=header_)

    def read_rsj_params(self, **kwargs):
        filename = kwargs.get('filename', self.fn_rsjparams)        
        step = kwargs.get('step', 1)
        params = pl.loadtxt(self.get_fullpath(filename), skiprows=1)\
          [(step-1)::step]
        self.idx_rsj_params = pl.array(list(map(int, params[:,0])))
        self.c = params[:,1:(1+self.cdim)]
        self.icarr, self.rnarr, self.ioarr, self.voarr, self.ic_err_arr,\
          self.rn_err_arr, self.io_err_arr, self.vo_err_arr\
          = [params[:,(1+self.cdim):][:,n] for n in range(8)]
        
    def read_ah_params(self, **kwargs):
        filename = kwargs.get('filename', self.fn_ahparams)        
        step = kwargs.get('step', 1)
        params = pl.loadtxt(self.get_fullpath(filename), skiprows=1)\
          [(step-1)::step]
        self.idx_ah_params = pl.array(list(map(round, params[:,0])))
        self.c = params[:,1:(1+self.cdim)]
        self.icarr, self.rnarr, self.ioarr, self.voarr, self.tnarr,\
          self.ic_err_arr, self.rn_err_arr, self.io_err_arr, self.vo_err_arr,\
          self.tn_err_arr\
          = [params[:,(1+self.cdim):][:,n] for n in range(10)]

    def plot_rsj_params(self, cind=1, filename=None):
        if filename is None:
            filename = self.fn_rsjparams
        data = pl.loadtxt(self.get_fullpath(filename), skiprows=1)
        cdim = self.cdim_from_filename(filename)
        fig = pl.figure(self.fignum_params,(8,4))
        
        pl.rcParams['font.size'] = 8
        subpos = [221, 223, 222, 224]    
        ax = [fig.add_subplot(idx) for idx in subpos]
        if cind==1:
            xlabels = ['H (Oe)', 'H (Oe)', 'H (Oe)', 'H (Oe)']
            ylabels = ['Ic (A)', 'Rn (Ohm)', 'Io (A)', 'Vo (V)']
        elif cind==2:
            xlabels = ['Ipls (A)', 'Ipls (A)', 'Ipls (A)', 'Ipls (A)']
            ylabels = ['Ic (A)', 'Rn (Ohm)', 'Io (A)', 'Vpls (V)']
        else:
            xlabels = ['Control %d'%cind, 'Control %d'%cind, 'Control %d'%cind,\
          'Control %d'%cind]
        
        for n in range(4):
            #ax[n].plot(data[:,1], data[:,(n+1+cdim)])
            if n==3 and cind==2:
                plothyst.plothystcolor(ax[n], data[:,cind], data[:,(cind+1)])
            else:
                plothyst.plothystcolor(ax[n], data[:,cind], data[:,(n+1+cdim)])
            ax[n].grid(1)
            ax[n].set_xlabel(xlabels[n])
            ax[n].set_ylabel(ylabels[n])
        fig.suptitle(filename)
        pl.show()
    
    def plot_ah_params(self, filename=None):
        if filename is None:
            filename = self.fn_ahparams
        ah = pl.loadtxt(self.get_fullpath(filename), skiprows=1)
        cdim = self.cdim_from_filename(filename)
        fig = pl.figure(self.fignum_params,(8,4))
        
        subpos = [221, 223, 222, 224]    
        ax = [fig.add_subplot(idx) for idx in subpos]
        xlabels = ['Control', 'Control', 'Control', 'Control']
        ylabels = ['Ic (A)', 'Rn (Ohm)', 'Io (A)', 'Tn (K)']
        
        for n in range(3):
            #ax[n].plot(ah[:,1], ah[:,(n+1+cdim)])
            plothyst.plothystcolor(ax[n], ah[:,1], ah[:,(n+1+cdim)])
            ax[n].grid(True)
            ax[n].set_xlabel(xlabels[n])
            ax[n].set_ylabel(ylabels[n])
            
        ax[3].plot(ah[:,1], ah[:,(5+cdim)])
        ax[3].grid(True)
        ax[3].set_xlabel(xlabels[3])
        ax[3].set_ylabel(ylabels[3])
        fig.suptitle(filename)
        pl.show()

# use this for TDS scope array data
class ProcIVArrayTDS(ProcIVArray):
    def read_datafile(self):
        cdim = self.cdim_from_filename(self.datafilename)
        #data = IVArrayTDS(self.get_fullpath(self.datafilename))
        data = datafile.IVArrayBin8b(self.get_fullpath(self.datafilename))
        data.readcfgfile()
        data.readdatafile(cdim=cdim)
        data.convert2iv()
        
        # pick partial data        
        self.idx = list(range(self.step-1, len(data.i), self.step))
#        self.c, self.iarr, self.varr = \
#          [data.c[:][self.idx], data.i[self.idx], data.v[self.idx]]
        
        # re-initialize variables   
        JJIVArray.__init__(\
          self, data.c[self.idx,:], data.i[self.idx], data.v[self.idx])
    
# functions for routinely data analysis
def plot_raw_ivarraytds(filename):
    data = ProcIVArrayTDS(datafilename=filename, step=1)
    data.read_datafile()
    data.plot_raw()

def fit2rsj_ivarraytds(filename, guess):
    data = ProcIVArrayTDS(datafilename=filename, step=1)
    data.read_datafile()
    data.datafit2rsj(guess)
    #data.plot_rsj_params()
    
def fit2ah_ivarraytds_1(filename, tnguess, step=1):
    data = ProcIVArrayTDS(datafilename=filename, step=step)
    data.read_datafile()
    data.datafit2ah_ic_rn_tn(tnguess)
#    data.plot_ah_params()
    #data.plot_iv(-1, showrsj=True, showah=True)
    
def fit2ah_ivarraytds_2(filename, tn, step=1):
    data = ProcIVArrayTDS(datafilename=filename, step=step)
    data.read_datafile()
    data.datafit2ah_ic_rn(tn)
#    data.plot_ah_params()
    #data.plot_iv(-1, showrsj=True, showah=True)
    
def plot_rsj_params(cind, filename):
    data = ProcIVArrayTDS(step=1)
    data.plot_rsj_params(cind=cind, filename=filename)

def plot_ah_params(filename):
    data = ProcIVArrayTDS(step=1)
    data.plot_ah_params(filename)

def plot_iv(idx, filename, **kwargs):
    data = ProcIVArrayTDS(datafilename=filename, step=1)
    data.read_datafile()
    data.plot_iv(idx, **kwargs)

class ProcIV(JJIV):
    def __init__(self, **kwargs):
        self.datafilename = kwargs.get('datafilename', 'test')
        #self.step = kwargs.get('step', 1)
        
        # dummy defaults. normally reassigned by read_datafile()
        #~ c = [pl.array([n]) for n in range(5)]
        #~ iarr = pl.array([pl.linspace(-.1, .1, 10) for n in range(5)])
        #~ varr = pl.array([pl.linspace(-.01, .01, 10) for n in range(5)])
        #~ self.idx = list(range(self.step-1, len(iarr), self.step))
        #~ JJIVArray.__init__(self, c, iarr, varr)
        #~ if 'datafilename' in kwargs:
            #~ self.cdim = self.cdim_from_filename(self.datafilename)
            
        # filename/directory settings
        #cfg = AnalysisCfg()
        cfg = analysis_params.AnalysisParams()
        self.path = cfg.datapath
        self.tag = cfg.tag
        #~ self.fn_rsjparams = 'fit2RSJ' + self.tag + '_' + self.datafilename + '.txt'
        #~ self.fn_ahparams = 'fit2AH' + self.tag + '_' + self.datafilename + '.txt'

        # plot settings
        self.fignum_params = 1
        self.fignum_iv = 2
        
    def get_fullpath(self, fn):
        return self.path + '/' + fn
        
    def plotraw_iv(self):
        data = pl.loadtxt(self.get_fullpath(self.datafilename), skiprows=0)
        #cdim = self.cdim_from_filename(filename)
        cdim = 2
        fig = pl.figure(self.fignum_params,(8,6))
        
        pl.rcParams['font.size'] = 8
        subpos = [311, 312, 313]
        ax = [fig.add_subplot(idx) for idx in subpos]
        xlabels = ['I (A)', 'I (A)', 'V (V)']
        ylabels = ['V (V)', 'dV/dI (Ohm)', 'dV/dI (Ohm)']
        colx = [1, 1, 2]
        coly = [2, 3, 3]
        
        for n in range(len(subpos)):
            #ax[n].plot(data[:,1], data[:,(n+1+cdim)])
            #plothyst.plothystcolor(ax[n], data[:,colx], data[:,coly])
            ax[n].plot(data[:,colx[n]], data[:,coly[n]])
            ax[n].grid(1)
            ax[n].set_xlabel(xlabels[n])
            ax[n].set_ylabel(ylabels[n])
        fig.suptitle(filename)
        pl.show()
        
if __name__ == '__main__':
    print(sys.version)
    #plot_raw_ivarraytds('040_VItrace-Hpulse-recool_B140211_chip22_jj4')
    #plot_rsj_params('fit2RSJ_040_VItrace-Hpulse-recool_B140211_chip22_jj4.txt')
    #plot_ah_params('fit2AH_046_VItrace-H_B140211_chip22_jj4_Hset7 4000OeR.txt')
    filename = '009_V_dVdI_vs_I_150126_chip56_jj13_Hset 5000OeRP.dat'
    iv = ProcIV(datafilename = filename)
    iv.plotraw_iv()
