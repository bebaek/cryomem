"""
Simple xy plot

BB, 2015
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from . import datafile, plotparams
from .plothyst import plothyst

# display units
_unit_i = 1e-6  # uA
_unit_v = 1e-6   # uV
_unit_r = 1      # Ohm
_unit_i1 = 1e-3  # mA; control I
_unit_v1 = 1e-3  # mV; control V
_unit_h = 10    # mT

class quickplot:
    def setplotparams(self):
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['legend.fontsize'] = 12
        plt.rcParams['legend.frameon'] = False

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

    # Typical xy plot with typical datafiles
    def plot_xy(self, **kwargs):

        # inspect the 1st datafile name and decide on datafile type
        filenames0 = kwargs['fi']
        if type(filenames0) is str:
            filenames0 = [filenames0]
        path, filename = os.path.split(filenames0[0])
        fileext = filename.split('.')[-1]
        if '_V_dVdI_vs_' in filename: 
            fitype = 'v_dvdi_h_i'
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
        #elif fileext == 'dat':
        #    fitype = 'bin_h_i_iarray_varray'
        #elif fileext == 'txt':
        #    fitype = 'fit_h_i_ic_rn'
        save = kwargs('save') if 'save' in kwargs else False
         
        plotparams.setplotparams()
        fig = plt.figure(1, figsize=(12,8))
        col = ['b','g','r','c','m','y','k']
        
        if fitype == 'bin_h_i_iarray_varray':   # Plot binary, IV trace data
            pass

        elif fitype == 'fit_h_i_ic_rn':         # Plot Ic-H.
            unit_h = 10
            unit_i = 1e-6
            unit_v = 1e-6
            unit_r = 1
            for k,filename0 in enumerate(filenames0):
                data = datafile.CMData_H_I_Ic_Rn()
                data.read(filename0)
                path, filename = os.path.split(filename0)
                filename2 = filename.split('.')[-2]

                pos = [221, 222, 223, 224]
                x = [data.happ/unit_h, data.happ/unit_h, data.happ/unit_h, 
                  data.happ/unit_h]
                y = [data.ic/unit_i, data.rn/unit_r, data.io/unit_i, 
                  data.vo/unit_v]
                xl = ['$\mu_0$H (mT)', '$\mu_0$H (mT)', '$\mu_0$H (mT)', 
                  '$\mu_0$H (mT)']
                yl = ['Ic ($\mu$A)', 'Rn (Ohm)', 'Io ($\mu$A)', 'Vo ($\mu$V)']
                
                ax = []
                for l in range(4):
                    ax += [fig.add_subplot(pos[l])]
                    if len(filenames0) > 1:     # multiple datafiles
                        plothyst(ax[l], x[l], y[l], color=col[k], mec=col[k],
                          label=filename2)
                    else:                       # single datafile
                        plothyst(ax[l], x[l], y[l], sglcolor=False, 
                                color=col[k], mec=col[k], label=filename2)
                    ax[l].set_xlabel(xl[l]); ax[l].set_ylabel(yl[l])
                    ax[l].grid(1)
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

        return filenames0

 
def app(args):    
    if len(args) < 2:
        print('')
        print('Usage: python plot_cryomem.py <filename> [<arguments>]\n')
        print('Examples:')
        print('python daq_dipstick.py sqwave_field h=150')
        print('python daq_dipstick.py set_sweepvolt .7')
        sys.exit(0)
    func = args[1]
    fn = args[2]
    if func == 'iv':
        pass
    elif func == 'hic':
        data = np.loadtxt(data, skiprows=1, usecols=(2,4))
        plothyst.plothyst(data[0], data[1])

    plt.show()


if __name__ == '__main__':
    import sys
    print(sys.version)
    app(sys.argv)
