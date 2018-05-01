"""
User interface for data management for magnetic JJ research
    Raw data processing (I-V fit) and plot
    High level data management (dev parameter database) and plot

Minimize codes here and delegate details to libcmtools modules.

BB, 2015
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, rc
import os
from time import sleep

#from libcmtools.plothyst import plothyst
from . import plothyst, plotparams, jjivarray, analyze_jjivarray, datafile, \
  sql_svjj, convargs, quickplot, plot_mpms, sql_mpms
from . import jjivarray2
from . import jjiv2 as jjiv
import os.path

# helper functions

def cdim_from_filename(filename):
    """Return N of control parameters"""
    if ('_VItrace-H_' in filename) or ('_VItrace-Hpulse_' in filename)\
      or ('_VIH_' in filename):
        cdim = 1
    elif ('_VItrace-IH_' in filename) or ('_VItrace-HI_' in filename):
        cdim = 2
    elif ('_VItrace-HIpulse_' in filename):
        cdim = 3
    else:
        print('Not a valid data file.'); sys.exit(1)
    return cdim

def load_data(fname, ftype='tdsbin'):
    if ftype == 'tdsbin':                          # Raw trace file
        cdim = cdim_from_filename(fname)
        data = datafile.IVArrayBin8b(fname)
        data.readcfgfile()
        data.readdatafile(cdim=cdim)
        data.convert2iv()
    elif ftype == 'icarr':               # RSJ fit file
        data = datafile.CMData_H_Ic_Rn(fname)
    return data

def newfilename_fit2rsj(origname):
    path, fname1 = os.path.split(origname)
    root1, ext1 = os.path.splitext(fname1)
    return path + 'fit2RSJ_' + root1 + '.txt' 

# user commands ##########

def fit(**kwargs):
    """Generate a file with jjiv fit array results and return that filename."""
    fi = kwargs['fi']
    model = kwargs.get('model', 'rsj_asym')
    fitype = kwargs.get('fitype', 'tdsbin')

    if model == 'rsj' or model == 'rsj_asym':
        kwargs2 = {}
        kwargs2['model'] = model
        kwargs2['io'] = io = kwargs.get('io', 0)
        if 'guess' in kwargs:
            kwargs2['guess'] = kwargs['guess']
        if 'updateguess' in kwargs:
            kwargs2['updateguess'] = kwargs['updateguess']
        else:
            kwargs2['updateguess'] = 0.8
            print('Default updateguess =', kwargs2['updateguess'])

        # read and fit data
        din = load_data(os.path.splitext(fi)[0], ftype='tdsbin')
        iarr, varr = din.i, din.v
        popt_arr, pcov_arr = jjivarray2.fit2rsj_arr(iarr, varr, **kwargs2)

        # build save data object
        n = len(popt_arr)
        npopt = len(popt_arr[0])
        dout = datafile.CMData_IcArr()
        dout.idx = np.arange(1, n+1)
        dout.happ, dout.iapp = din.c[:,0], din.c[:,1]
        dout.ic_pos, dout.ic_neg, dout.rn, dout.vo = [popt_arr[:,k] for k in range(npopt)]

        # pick only diagonals of covariances
        ic_pos_err, ic_neg_err, rn_err, vo_err = [np.zeros(n) for k in range(npopt)]
        for k in range(n):
            ic_pos_err[k], ic_neg_err[k], rn_err[k], vo_err[k] = list(np.sqrt(np.diag(pcov_arr[k]))) if np.shape(pcov_arr[k]) == (4,4) else [np.inf for l in range(npopt)]
            dout.ic_pos_err, dout.ic_neg_err, dout.rn_err, dout.vo_err = ic_pos_err, ic_neg_err, rn_err, vo_err 

        # fixed parameter 
        dout.io = np.ones(n)*io
        dout.io_err = np.zeros(n)
        
        # tweak filename and save
        fo = newfilename_fit2rsj(fi)
        dout.save(fo)
        return fo
    else:
        print(model,': not implemented yet')
        return

def plot(**kwargs):
    """Plot depending on passed datafile type"""
    filenames0 = kwargs['fi']
    if type(filenames0) == str:
        issingleplot = True
        filenames0 = [filenames0]
    else:
        issingleplot = False
    path, filename = os.path.split(filenames0[0])
    #fileext = filename.split('.')[-1]
    fileext = os.path.splitext(filename)[1]

    if 'fit2RSJ_' in filename:
        fitype = 'icarr'
    elif '_V_dVdI_vs_' in filename: 
        fitype = 'v_dvdi_h_i'
    elif (fileext == '.dat') and ('_VItrace-HI_' in filename):
        fitype = 'h_i_iarray_varray_bin'
    else:
        fitype = 'unknown'
        xcol = int(kwargs.get('xcol', 0))
        ycol = int(kwargs.get('ycol', 1))
        xl = kwargs.get('xlabel', 'Column '+str(xcol))
        yl = kwargs.get('ylabel', 'Column '+str(ycol))
        xparam = kwargs.get('x', '')
        yparam = kwargs.get('y', '')
    #if 'fitype' in kwargs:
    #    fitype = kwargs['type']
    #elif fileext == 'txt':
    #    fitype = 'fit_h_i_ic_rn'
    save = kwargs['save'] if 'save' in kwargs else False
     
    plotparams.setplotparams()
    fig = plt.figure(1, figsize=(12,6))
    col = ['b','g','r','c','m','y','k']

    # datafile type dependent
    if fitype == 'h_i_iarray_varray_bin':   
        # Plot binary, IV trace data
        unit_i = 1e-6
        unit_v = 1e-6
        idxs = kwargs.get('idx',[0])
        if type(idxs) != list :    # array-fy
            idxs = [idxs]
        idxs = list(map(int, idxs))
        showrsj = kwargs.get('showrsj', False)
        for k in range(len(filenames0)):
            filename0, idx = filenames0[k], idxs[k]

            # read from file
            din = load_data(os.path.splitext(filename0)[0], ftype='tdsbin')
            iarr, varr = din.i, din.v

            # plot data
            fig.add_subplot(111)
            x, y = iarr[idx]/unit_i, varr[idx]/unit_v
            plt.plot(x, y, 'o')
            
            # plot fit
            if showrsj:
                # open fit file
                fitfilename = newfilename_fit2rsj(filename0)
                p = datafile.CMData_IcArr(fitfilename)
                i2 = np.linspace(1.1*min(iarr[idx]), 1.1*max(iarr[idx]), 1000)
                v2 = jjiv.v_rsj_asym(i2, p.ic_pos[idx], p.ic_neg[idx], \
                    p.rn[idx], p.io[idx], p.vo[idx])

                # plot
                plt.plot(i2/unit_i, v2/unit_v, '-')

            plt.xlabel('I ($\mu$A)')
            plt.ylabel('V ($\mu$V)')
            plt.grid(1)

    elif fitype == 'icarr':
        # plot Ic-H or Ic-I
        unit_h = 10
        unit_i = 1e-6
        unit_v = 1e-6
        unit_r = 1e-3
        def plotfunc(issingle, ax, x, y, **kwargs):
            kwargs['sglcolor'] = False if issingle else True
            plothyst.plothyst(ax, x, y, **kwargs)

        # plot
        for k,filename0 in enumerate(filenames0):
            data = datafile.CMData_IcArr(filename0)
            path, filename = os.path.split(filename0)
            filename2, ext = os.path.splitext(filename)
            ax = []

            # subplot 1
            gca = fig.add_subplot(121)
            ax += [gca]
            x = data.happ/unit_h
            y = data.ic_pos/unit_i          # Ic_pos
            plotfunc(issingleplot, gca, x, y, color=col[k], mec=col[k], label=filename2)
            y = data.ic_neg/unit_i          # Ic_neg
            plotfunc(issingleplot, gca, x, y, color=col[k], mec=col[k], label=filename2)
            gca.set_xlabel('$\mu_0$H (mT)')
            gca.set_ylabel('Ic ($\mu$A)')

            # subplot 2
            gca = fig.add_subplot(222)
            ax += [gca]
            y = data.rn/unit_r              # Rn 
            plotfunc(issingleplot, gca, x, y, color=col[k], mec=col[k], label=filename2)
            gca.set_ylabel('Rn (m$\Omega$)')

            # subplot 3
            gca = fig.add_subplot(224)
            ax += [gca] 
            y = data.vo/unit_v              # Rn 
            plotfunc(issingleplot, gca, x, y, color=col[k], mec=col[k], label=filename2)
            gca.set_ylabel('Vo ($\mu$V)')
            gca.set_xlabel('$\mu_0$H (mT)')

        # rest of formatting
        for a in ax:
            a.grid(1)
        ax[2].legend(loc=2, fontsize=9)
    elif fitype == 'v_dvdi_h_i':         # Plot dV/dI-I
        unit_h = 10
        unit_i = 1e-6
        unit_v = 1e-6
        unit_r = 1

        # plot file by file
        for k,filename0 in enumerate(filenames0):
            data = datafile.CMData_H_I_V_dVdI()
            data.read(filename0)
            path, filename = os.path.split(filename0)

            # choose x, y cols
            for param in ['happ','iapp']:
                x0 = getattr(data, param)
                if max(x0) != min(x0):
                    x = x0
            #xparam = kwargs.get('x', 'iapp')
            yparam = kwargs.get('y', 'dvdi')
            #pos = [221, 222, 223, 224]
            #x = getattr(data, xparam)
            y = getattr(data, yparam)
            #xl = ['$\mu_0$H (mT)', '$\mu_0$H (mT)', '$\mu_0$H (mT)', 
            #  '$\mu_0$H (mT)']
            #yl = ['Ic ($\mu$A)', 'Rn (Ohm)', 'Io ($\mu$A)', 'Vo ($\mu$V)']
            
            ax = fig.add_subplot(111)
            if len(filenames0) > 1:     # multiple datafiles
                plothyst(ax, x, y, c=col[k], mec=col[k],
                        label=filename[:-4])
            else:                       # single datafile
                plothyst(ax, x, y, sglcolor=False, c=col[k],
                  mec=col[k], label=filename[:-4])
            #ax.set_xlabel(xl); ax.set_ylabel(yl)
            ax.grid(1)
            ax.legend(loc=2, fontsize=9)

    elif fitype == 'unknown':
        for k,filename0 in enumerate(filenames0):
            data = np.loadtxt(filename0)
            path, filename = os.path.split(filename0)

            x = data[:,xcol]
            y = data[:,ycol]

            ax = fig.add_subplot(111)
            if len(filenames0) > 1:     # multiple datafiles
                plothyst(ax, x, y, c=col[k], mec=col[k],
                        label=filename[:-4])
            else:                       # single datafile
                plothyst(ax, x, y, sglcolor=False, c=col[k],
                  mec=col[k], label=filename[:-4])
            ax.set_xlabel(xl); ax.set_ylabel(yl)
            ax.grid(1)
            ax.legend(loc=2, fontsize=9)

    plt.tight_layout()
    if save:
        path, filename = os.path.split(filenames0[-1])
        print(path, filename)
        plt.savefig(path + filename[:-4] + '.png')
    plt.show()

def update_fit_plot(**kwargs):
    """Update plot periodically. Works from shell not notebook.
    """
    unit_h = 10
    unit_i = 1e-6
    unit_v = 1e-6
    unit_r = 1e-3

    # setup plot
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'o-', animated=True)

    # initial plot function
    def init():
        line.set_data([], [])
        return (line,)

    # animation function
    def animate(k):
        filename = fit(**kwargs)
        #filename = 'fit2RSJ_{}_VItrace-HI.txt'.format(str(k%2))
        #print(filename)
        data = datafile.CMData_IcArr(filename)
        x = data.happ/unit_h
        y = data.ic_pos/unit_i          # Ic_pos
        line.set_data(x, y)
        plt.xlim(min(x), max(x))
        plt.ylim(min(y), max(y))
        return (line,)

    # update/animate
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=1000,
                                   interval=10000, blit=True)
    #rc('animation', html='html5')
    #print('anim start')
    #anim
    #print('anim done')
    plt.show()

class cmtools:
    """(old) Main cryomem analysis class.
    To retire analyze_jjivarray.py gradually.
    """

    def fit_ivarr(self, **kwargs):
        """Transitional RSJ fit method"""
        fi = kwargs['fi']   # include extension .dat
        model = kwargs.get('model', 'rsj')
        if model == 'rsj' or model == 'rsj2':
            guess = kwargs.get('guess', [50e-6, 1e-3, 0, 0])
        elif model == 'ah':
            step = int(kwargs.get('step', 1))
            if 'tn ' in kwargs:
                tn = kwargs['tn']
                fitmode = 1
            else:
                tnguess = kwargs.get('tnguess', 27)
                fitmode = 0

        # call old fitting function
        #fi_noext = fi[:-4]
        if model == 'rsj':                                  # RSJ fit
            analyze_jjivarray.fit2rsj_ivarraytds(fi, guess, method=0) 
            fo = 'fit2RSJ_'+fi[:-4]+'.txt'          # output filename
        elif model == 'rsj2':                                  # RSJ fit
            analyze_jjivarray.fit2rsj_ivarraytds(fi, guess, method=1) 
            fo = 'fit2RSJ_'+fi[:-4]+'.txt'          # output filename
        elif model == 'ah':                                 # AH fit
            if fitmode == 0:
                analyze_jjivarray.fit2ah_ivarraytds_1(fi, tnguess, step=step)  
            elif fitmode == 1:
                analyze_jjivarray.fit2ah_ivarraytds_2(fi, tn, step=step)  
            fo = 'fit2AH_'+fi[:-4]+'.txt'

        return fo

    def get_iv(self, **kwargs):
        """Return I, V 1-d data."""
        idx = kwargs.get('idx', 0)
        fi = kwargs['fi']
        i,v = analyze_jjivarray.get_iv(fi, idx=idx)
        return i,v

    # plot I-V from main IV array datafiles
    def plot_ivarr(self, **kwargs):
        idx = int(kwargs.get('idx', 0))
        fi = kwargs['fi']
        if 'idx' in kwargs: del kwargs['idx']
        if 'fi' in kwargs: del kwargs['fi']
        #showrsj = kwargs.get('showrsj', False)
        analyze_jjivarray.plot_iv(idx, fi, **kwargs)
        return 0

    def fit_new(self, **kwargs):
        '''Usage: cmfit(fi=filename, model=modelname, guess=guesslist,
        io=ioffset, of=outfilename)
            modelname: 'rsjsym' (single Ic) or 'rsjasym' (pos/neg Ic'; default).
            guesslist: [ic, rn, io, vo] (rsjsym) or 
              [icpos, icneg, rn, io, vo] (rsjasym)
            ioffset: current offset in A. Default 0.
            outfilename: Default fitRSJ_<input filename wo ext>.txt
        '''
        # arguments
        fi = kwargs['fi']
        model = kwargs.get('model', 'rsjsym')
        guess = kwargs.get('guess', [50e-6, -50e-6, 1, 0, 0])
        io = kwargs.get('io', 0)
        if 'fo' in kwargs:
            fo = kwargs['fo']
        else:
            path, filename = ntpath.split(fi)
            filename_core = filename.split('.')[0]
            fo = path + filename_core + '.txt'

        # read and process data
        #data = ProcIVArrayTDS(datafilename=filename, step=1)
        #data.read_datafile()
        #data.datafit2rsj(guess)
        #data.plot_iv(idx, **kwargs)

        rawdata = datafile.CMData8b_H_I_Iarr_Varr(fi=fi)  # read datafile
        data = jjivarray.JJIVArray(rawdata.ivarr)        # fit
        data.fitrsj(model=model, guess=guess, io=io)
        odata = datafile.CMData_H_I_Ic_Rn()     # save
        odata.save(fo)
        return fo

    def plot_ic_h(self, **kwargs):
        '''Examples:
            cmplot(fi=filename, index=0, showrsj=True): raw IV trace (.dat)
            cmplot(fi=filename): detect file type with extention and plot
            cmplot(fi=filename, type=fit_h_i_ic_rn): designate file type
        '''
        # inspect filename and decide on datafile type
        filenames0 = kwargs['fi']
        if type(filenames0) is str:
            filenames0 = [filenames0]
        path, filename = os.path.split(filenames0[0])
        fileext = filename.split('.')[-1]
        if 'fitype' in kwargs:
            fitype = kwargs['type']
        elif fileext == 'dat':
            fitype = 'bin_h_i_iarray_varray'
        elif fileext == 'txt':
            if '_VItrace-HI_' in filename:
                fitype = 'fit_h_i_ic_rn'
            elif '_VItrace-HIpulse_' in filename:
                fitype = 'fit_h_i_ic_rn_pulse'
        save = kwargs['save'] if 'save' in kwargs else False

        plotparams.setplotparams()
        fig = plt.figure(1, figsize=(12,6))
        col = ['b','g','r','c','m','y','k']
        
        if fitype == 'bin_h_i_iarray_varray':   # Plot binary, IV trace data
            pass
        # plot txt data
        elif fitype == 'fit_h_i_ic_rn' or fitype == 'fit_h_i_ic_rn_pulse':
            unit_h = 10
            unit_i = 1e-6
            unit_ib = 1e-3
            unit_v = 1e-6
            unit_r = 1
            for k,filename0 in enumerate(filenames0):
                if fitype == 'fit_h_i_ic_rn':
                    data = datafile.CMData_H_I_Ic_Rn()
                elif fitype == 'fit_h_i_ic_rn_pulse':
                    data = datafile.CMData_H_I_Ic_Rn_pulse()
                data.read(filename0)
                path, filename = os.path.split(filename0)
                filename2 = filename.split('.')[-2]

                # choose x between H and I 
                for param in ['happ','iapp']:
                    x0 = getattr(data, param)
                    if max(x0) != min(x0):
                        x = x0
                        xparam = param
                        if param is 'happ':
                            xunit = unit_h
                        elif param is 'iapp':
                            xunit = unit_ib

                pos = [221, 222, 223, 224]
                if fitype == 'fit_h_i_ic_rn':
                    xs = [x/xunit, x/xunit, x/xunit, x/xunit]
                    ys = [data.ic/unit_i, data.rn/unit_r, data.io/unit_i, 
                      data.vo/unit_v]
                    if xparam is 'happ':
                        xl = ['$\mu_0$H (mT)', '$\mu_0$H (mT)', '$\mu_0$H (mT)'
                                , '$\mu_0$H (mT)']
                    elif xparam is 'iapp':
                        xl = ['I (mA)', 'I (mA)', 'I (mA)', 'I (mA)']
                    yl = ['Ic ($\mu$A)','Rn (Ohm)','Io ($\mu$A)','Vo ($\mu$V)']
                elif fitype == 'fit_h_i_ic_rn_pulse':
                    xs = [x/xunit, x/xunit, x/xunit, x/xunit]
                    ys = [data.ic/unit_i, data.rn/unit_r, data.io/unit_i, 
                      data.vapp]
                    if xparam is 'happ':
                        xl = ['$\mu_0$H (mT)', '$\mu_0$H (mT)', '$\mu_0$H (mT)'
                                , '$\mu_0$H (mT)']
                    elif xparam is 'iapp':
                        xl = ['I (mA)', 'I (mA)', 'I (mA)', 'I (mA)']
                    yl = ['Ic ($\mu$A)','Rn (Ohm)','Io ($\mu$A)','Vcoil (V)'] 
                ax = []
                for l in range(4):
                    ax += [fig.add_subplot(pos[l])]
                    if len(filenames0) > 1:     # multiple datafiles
                        plothyst.plothyst(ax[l], xs[l], ys[l], c=col[k], 
                                mec=col[k], label=filename2)
                    else:                       # single datafile
                        plothyst.plothyst(ax[l], xs[l], ys[l], sglcolor=False,
                                c=col[k], mec=col[k], label=filename2)
                    ax[l].set_xlabel(xl[l]); ax[l].set_ylabel(yl[l])
                    ax[l].grid(1)
                ax[2].legend(loc=2, fontsize=9)
                    
        plt.tight_layout()
        if save:
            path, filename = os.path.split(filenames0[-1])
            print(path, filename)
            plt.savefig(path + filename[:-4] + '.png')
        plt.show()
        return filenames0

    def plot_ic_i(self, **kwargs):
        '''Examples:
            cmplot(fi=filename, index=0, showrsj=True): raw IV trace (.dat)
            cmplot(fi=filename): detect file type with extention and plot
            cmplot(fi=filename, type=fit_h_i_ic_rn): designate file type
        '''
        # inspect filename and decide on datafile type
        filenames0 = kwargs['fi']
        if type(filenames0) is str:
            filenames0 = [filenames0]
        path, filename = os.path.split(filenames0[0])
        fileext = filename.split('.')[-1]
        if 'fitype' in kwargs:
            fitype = kwargs['type']
        elif fileext == 'dat':
            fitype = 'bin_h_i_iarray_varray'
        elif fileext == 'txt':
            fitype = 'fit_h_i_ic_rn'
         
        plotparams.setplotparams()
        fig = plt.figure(1, figsize=(12,6))
        col = ['b','g','r','c','m','y','k']
        
        if fitype == 'bin_h_i_iarray_varray':   # Plot binary, IV trace data
            pass

        elif fitype == 'fit_h_i_ic_rn':         # Plot Ic-H.
            unit_h = 10
            unit_i = 1e-3
            unit_v = 1e-6
            unit_r = 1
            for k,filename0 in enumerate(filenames0):
                data = datafile.CMData_H_I_Ic_Rn()
                data.read(filename0)
                path, filename = os.path.split(filename0)
                filename2 = filename.split('.')[-2]

                pos = [221, 222, 223, 224]
                x = [data.iapp/unit_i, data.iapp/unit_i, data.iapp/unit_i, 
                  data.iapp/unit_i]
                y = [data.ic/unit_i, data.rn/unit_r, data.io/unit_i, 
                  data.vo/unit_v]
                xl = ['I (mA)', 'I (mA)', 'I (mA)', 'I (mA)']
                yl = ['Ic ($\mu$A)', 'Rn (Ohm)', 'Io ($\mu$A)', 'Vo ($\mu$V)']
                
                ax = []
                for l in range(4):
                    ax += [fig.add_subplot(pos[l])]
                    if len(filenames0) > 1:     # multiple datafiles
                        plothyst.plothyst(ax[l], x[l], y[l], c=col[k], mec=col[k],
                          label=filename2)
                    else:                       # single datafile
                        plothyst.plothyst(ax[l], x[l], y[l], sglcolor=False, c=col[k],
                          mec=col[k], label=filename2)
                    ax[l].set_xlabel(xl[l]); ax[l].set_ylabel(yl[l])
                    ax[l].grid(1)
                ax[2].legend(loc=2, fontsize=9)
                    
        plt.tight_layout()
        plt.show()
        return filenames0

    # fit and plot JJ params of I-V data
    def fit_plot_ivarr(self, **kwargs):
        fo1 = self.fit_ivarr(**kwargs)
        kwargs['fi'] = fo1
        self.plot_ic_h(**kwargs)

    # Search SVJJ device DB
    def search_josephson(self, **kwargs):
        '''**kwargs: searchcol, searchval
            examples: 
            searchcol=['structure', 'fm2_thickness'], searchval=['Fe/Cu/Ni/Cu',
              2.4e-9 
            return: ['wafer', 'chip', 'device', 'fm1_thickness', 'ic_p', 
              'ic_ap', 'rn']
        '''
        db = sql_svjj.SVJJDB('../data/svjj.db')
        data = db.search_josephson(**kwargs)

        for row in data:
            print(row)
        return data

    # test sql
    def simplesearchdb1_svjj(self, **kwargs):
        barrierstr = kwargs['barrierstr']
        fm2_thickness = kwargs['fm2_thickness']
        db = sql_svjj.SVJJDB('../data/svjj.db')
        data = db.simplesearchdb1(barrierstr, fm2_thickness)
        return data

    # internal method: return column as list in tuple list
    def colfromtuples(self, l, ind):
        return [l[k][ind] for k,tmp in enumerate(l)]

    # Plot IcRn vs FM thickness from db
    def plot_vc_d(self, **kwargs):
        data = self.search_josephson(**kwargs)
        xl, yl = 'FM thickness (nm)', 'Vc (uV)'
        unit_v = 1e-6
        unit_d = 1e-9

        ic_p = np.array(self.colfromtuples(data, 6))
        ic_ap = np.array(self.colfromtuples(data, 7))
        rn = np.array(self.colfromtuples(data, 8))
        d = np.array(self.colfromtuples(data, 4))
        vc_p = ic_p*rn
        vc_ap = ic_ap*rn
        
        self.plot(d/unit_d, vc_p/unit_v, 'b^', xl=xl, yl=yl, ms=12)
        self.plot(d/unit_d, vc_ap/unit_v, 'ro', xl=xl, yl=yl, ms=12)
        
        plt.show()
        return d
        
    # internal method
    def plot(self, x, y, *args, **kwargs):
        
        # custom labels
        xl = kwargs.get('xl', 'x')
        yl = kwargs.get('yl', 'y')
        if 'xl' in kwargs: del kwargs['xl']
        if 'yl' in kwargs: del kwargs['yl']

        # plot with custom plot parameters
        plotparams.setplotparams()
        fig = plt.figure(1, figsize=(12,8))
        ax = fig.add_subplot(111)
        ax.plot(x, y, *args, **kwargs)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_xlim([0, ax.get_xlim()[1]]) 
        ax.set_ylim([0, ax.get_ylim()[1]]) 
        plt.tight_layout()

    # plot from common datafiles
    def quickplot(self, **kwargs):
        p = quickplot.quickplot()
        p.plot_xy(**kwargs)
        return 0

    # MPMS plot
    def plot_mpms(self, **kwargs):
        plot_mpms.plot_mpms(**kwargs)
        return 0

    # Search MPMS DB for M-H in-plane data
    def search_mhip(self, **kwargs):
        '''**kwargs: searchcol, searchval
            examples: 
            searchcol=['structure'], 
            searchval=['Ta/Cu/Co/Cu/Ta']
        '''
        db = sql_mpms.MPMSDB('../data/mpms.db')
        data = db.search_mhip(**kwargs)

        for row in data:
            print(row)
        return data

    # Plot moment (per area) vs FM thickness from db
    def plot_m_d(self, **kwargs):
        data = self.search_josephson(**kwargs)
        xl, yl = 'FM thickness (nm)', 'Moment/Area (mA)'
        unit_m = 1e-3
        unit_d = 1e-9

        m = np.array(self.colfromtuples(data, 6))
        d = np.array(self.colfromtuples(data, 7))
        rn = np.array(self.colfromtuples(data, 8))
        d = np.array(self.colfromtuples(data, 4))
        vc_p = ic_p*rn
        vc_ap = ic_ap*rn
        
        self.plot(d/unit_d, vc_p/unit_v, 'bs', xl=xl, yl=yl)
        self.plot(d/unit_d, vc_ap/unit_v, 'go', xl=xl, yl=yl)
        
        plt.show()
        return d
 
   # indirect method call (from CLI)
    def call(self, cmd, **kwargs):
        getattr(self, cmd)(**kwargs) 

# Handle command line run. Convert shell args to kw args
def main(args0):    
    if len(args0) < 2:
        print(
"""Usage: cmdata <command> [--option1 value1 value2 ...]
Examples:
     cmdata fit --fi data.dat [--updateguess 0.9] [--guess 50e-6 -50e-6 1e-3 0] [--io 1e-6]
            Fits positive and negative Ic\'s. --guess: Ic+ Ic- Rn Voff
     cmdata plot --fi fit.txt [fit2.txt ...] [--save]
            New general plot function. Compatible with fit.
     cmdata update_fit_plot --fi data.dat [--updateguess 0.9] [--guess 50e-6 -50e-6 1e-3 0] [--io 1e-6]
            Run fit and plot repeatedly to monitor progress (iv tracer).

Old examples:
     cmdata fit_ivarr --fi data.dat --guess 50e-6 1e-3 0 0
     cmdata fit_ivarr --fi data.dat --guess 50e-6 1e-3 0 0 --model rsj2
     cmdata fit_plot_ivarr --fi data.dat --guess ... --save
     cmdata plot_ivarr --fi data.dat --idx 0 --showrsj --saveraw --saversj
     cmdata plot_mpms --fi data.dat --datatype mt --norm
     cmdata quickplot --fi loop1.dat loop2.dat --save
     cmdata plot_ic_h --fi fit1.txt fit2.txt --save
"""
        )
        sys.exit(0)
    cmd = args0[1]
    kwargs = convargs.convargs(args0[2:])   # make args kwargs
    print(kwargs)
    if cmd in ('fit', 'plot', 'update_fit_plot'):       # new, simpler way
        globals()[cmd](**kwargs)
    else:                                   # deprecated
        tools = cmtools()
        tools.call(cmd, **kwargs)

if __name__ == '__main__':
    #print(sys.version)
    main(sys.argv)
    #print('Bye!')
