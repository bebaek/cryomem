# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Define datafile structures.
Used for both DAQ and Data Manipulation.

BB 2014
"""

from shutil import copy
from glob import glob
#from os.path import exists
import os.path, configparser
from os import mkdir
from collections import OrderedDict
import struct
import numpy as np

# Config file used by DAQ
class DAQParamsDipstick:
    def __init__(self, filename='cfg_daq_dipstick.txt', meastype='Hpulse_IVscope'):
        self.loadparams(filename, meastype)
        
    def loadparams(self, filename='cfg_daq_dipstick.txt', meastype='Hpulse_IVscope'):
        self.configfilename = filename
        f = open(filename, 'r')
        self.params = OrderedDict([])
        for line in f:
            l = line.split('=')
            if len(l) > 1:
                self.params[l[0].strip()] = l[1].strip()
        f.close()
        self.meastype = meastype
        self.lab = self.params.get('lab','x')
        self.gain = float(self.params.get('preamp gain',0))
        self.gain2 = float(self.params.get('preamp 2 gain',0))
        self.dac_field = self.params.get('field dac','mccdaq')
        self.dac_bias = self.params.get('bias dac','sr830')
        self.dac_bias2 = self.params.get('bias2 dac','sr830')
        self.dac_heat = self.params.get('heater dac','sr830')
        self.dacch_field = int(self.params.get('field dac channel',0))
        self.dacch_bias = int(self.params.get('bias dac channel',0))
        self.dacch_bias2 = int(self.params.get('bias dac channel 2',0))
        self.dacch_heat = int(self.params.get('heater dac channel',0))
        self.volt_amped = False if self.params.get('voltmeter amplified','no')\
            else True
        self.i_per_v_swpbias = float(self.params.get('sweep bias current per voltage',0))
        self.i_per_v_dcbias = float(self.params.get('dc bias current per voltage',0))
        self.ioffset_dcbias = float(self.params.get('dc bias current offset',0))
        self.i_per_v_acbias = float(self.params.get('ac bias current per voltage',0))
        self.i_per_v_coil = float(self.params.get('coil current per voltage',0))
        self.i_coil_max = float(self.params.get('max coil current',18))
        self.i_per_v_heat = float(self.params.get('heater current per voltage',0))
        self.i_heat = float(self.params.get('heater current',0))
        self.h_per_i = float(self.params.get('field per current',0))
        self.h_ramp_delay = float(self.params.get('field ramp delay',0))
        self.h_ramp_step = float(self.params.get('field ramp step',0))
        self.tsettle1 = float(self.params.get('settling time 1',0))
        self.tsettle2 = float(self.params.get('settling time 2',0))
        self.f_lockin = float(self.params.get('lock-in frequency',0))
        self.ampl_lockin = float(self.params.get('lock-in amplitude',0))
        self.time_lockin = float(self.params.get('lock-in time constant',0))
        self.flt_lockin = self.params.get('lock-in filter oct','x')
        self.datapath = self.params.get('data path root','.') + '/' \
                    + self.params.get('data folder','')
        self.tag = self.params.get('datafile tag','x')

        # look for the last number of datafiles and increase it.
        fnlist = glob(self.datapath+'\\*.dat')
        if len(fnlist)==0:
            n=1
            print ('1st data!')
        else:
            n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1
        self.datafilename = '%03d_%s_%s'%(n, self.meastype, self.tag)

    def getlastfilename(self):
        fnlist = glob(self.datapath+'\\*.dat')
        if len(fnlist)==0:
            print ('No data!')
            return(1)
        else:
            n = np.argmax([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])
            fn = fnlist[n]
            return(fn)

    def saveconf(self):
        # look for the last number of datafiles and increase it.
        fnlist = glob(self.datapath+'\\*.dat')
        if len(fnlist)==0:
            n=1
            print ('1st data!')
        else:
            n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1
        self.datafilename = '%03d_%s_%s'%(n, self.meastype, self.tag)

        src = self.configfilename
        dst = self.datapath+'\\'+self.datafilename+'.txt'
        if os.path.exists(self.datapath)==False:
            mkdir(self.datapath)
            print ('Created new folder: %s'%self.datapath)
        copy(src, dst)
        print ('Created config file: %s' % (dst))

    def saveconf2(self, addedparams):
        # look for the last number of datafiles and increase it.
        fnlist = glob(self.datapath+'\\*.dat')
        if len(fnlist)==0:
            n=1
            print ('1st data!')
        else:
            n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1
        self.datafilename = '%03d_%s_%s'%(n, self.meastype, self.tag)

        src = self.configfilename
        dst = self.datapath+'\\'+self.datafilename+'.txt'
        if os.path.exists(self.datapath)==False:
            mkdir(self.datapath)
            print ('Created new folder: %s'%self.datapath)
        copy(src, dst)

        # more parameters
        f = open(dst, 'a')
        f.write('\n')
        for key in addedparams.keys():
            f.write(key + ' = ' + str(addedparams[key]))
        f.close()

    # Use this.
    # save all the params (from dict)
    def saveconf3(self):
        # check the directory
        print (os.path.exists(self.datapath))
        if os.path.exists(self.datapath)==False:
            mkdir(self.datapath)
            print ('Created new folder: %s'%self.datapath)

        # look for the last number of datafiles and increase it.
        fnlist = glob(self.datapath+'\\*.dat')
        if len(fnlist)==0:
            n=1
            print ('1st data!')
        else:
            n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1
        self.datafilename = '%03d_%s_%s'%(n, self.meastype, self.tag)
        dst = self.datapath+'\\'+self.datafilename+'.txt'
        
        # save parameters
        f = open(dst, 'w')
        for key in self.params.keys():
            f.write(key + ' = ' + str(self.params[key]) + '\n')
        f.close()

    # save params to master config file
    def saveconf_master(self):
        f = open('./'+self.configfilename, 'w')
        for key in self.params.keys():
            f.write(key + ' = ' + str(self.params[key]) + '\n')
        f.close()

    def appendconf(self, addedparams):
        dst = self.datapath+'\\'+self.datafilename+'.txt'
        f = open(dst, 'a')
        for key in addedparams.keys():
            f.write('\n' + key + ' = ' + str(addedparams[key]))
        f.close()

    def printconf(self):
        pass
    
class HIIarrVarr:
    """Raw IV array with control parameters H and I
    H, I: double (64 bit)
    Iarr, Varr: short (16; picoscope) or char (8; tektronics)
    Given metadata (config) with 'scope actual' section
    """
    def set_md(self, md):
        self.md = md

    def set_data(self, h, i, iarr, varr):
        self.h, self.i, self.iarr, self.varr = h, i, iarr, varr

    def _get_mdfilename(self, filename):
        """Return metadata filename from data filename"""
        return os.path.basename(filename) + '.md'

    def write_md(self, filename):
        with open(self._get_mdfilename(filename)) as mdfile:
            md.write(mdfile)

    def write(self, filename, **kwargs):
        """Write metadata and data to file
        Keyword arguments:
        bit -- 8 (TDS2000), 16 (picoscope) for Iarr and Varr raw format
        """
        self.write_md(filename)
        
        # (h,i: 8,8 bytes) + (i: Nx 1 or 2 bytes) + (v: Nx 1 or 2 bytes)
        outdata = struct.pack('f', val1) + struct.pack('f', val2) + arr1 + arr2
        outfile.write(outdata)
        outfile.flush()

    def read(self, filename):
        pass

    def set_md(self, **kwargs):
        for key in kwargs:
            self.md['scope actual'][key] = kwargs[key]
        
    def read_md(self, filename):
        self.md = configparser.ConfigParser()
        self.config.read(self._get_mdfilename(filename))
    def get_iv(self):
        pass

# an array of 2 float scalars and 2 8-bit binary arrays (TDS scope)
class IVArrayBin8b:
    def __init__(self, filename):
        self.fncfg = filename+'.osccfg'         # scope-specific params
        self.fndat = filename+'.dat'            # data
        self.fnsetup = filename + '.txt'        # measurement setup file
        #self.hmult = 1                          # I to H conversion factor
        
    def savewfmdata(self, f, msg):
        #msg = self.getwfmparam(ch)       # get waveform parameters
        print(msg)
        f.write(msg)                # save params in separate file
    
    def savedata(self, outfile, val1, val2, arr1, arr2):
        # (ih: 1x 4 byte float) + (i: 2500x 1 byte int) + (v: 2500x 1 byte int)
        outdata = struct.pack('f', val1) + struct.pack('f', val2) + arr1 + arr2
        outfile.write(outdata)
        outfile.flush()

    def readcfgfile(self):
        f = open(self.fncfg, 'r')

        # channel 1
        params = f.readline().split(';')
        self.pts    = int(params[5])
        self.xincr  = float(params[8])
        self.ymult  = [float(params[12])]
        self.yoff   = [float(params[14])]

        # channel 2
        params = f.readline().split(';')
        self.ymult.append( float(params[12]) )
        self.yoff.append( float(params[14]) )

        #print self.pts, self.xincr, self.ymult, self.yoff
        f.close()

    # reads datafile with variable number of control params (scalar)
    def readdatafile(self, cdim=1, ltrim=0, rtrim=0):
        f = open(self.fndat, 'rb')
        raw = f.read()
        f.close()
        dn = 4*cdim + 2*self.pts  # byte count: cdim*(float) + 2*(byte array)
        n = int(len(raw)/dn) - ltrim - rtrim
        #self.c = [np.zeros(n)]*cdim
        self.c = np.zeros((n, cdim))
        self.v = np.zeros((n, self.pts))
        self.i = np.zeros((n, self.pts))
        pp = 0
        for m in range(ltrim, n-rtrim, 1):
            # control params
            for k in range(cdim):
                self.c[m][k] = struct.unpack('f', raw[pp:(pp+4)])[0]; pp+=4

            # IV      
            self.v[m] = struct.unpack('%db'%self.pts, raw[pp:(pp+self.pts)]); pp+=self.pts
            self.i[m] = struct.unpack('%db'%self.pts, raw[pp:(pp+self.pts)]); pp+=self.pts
        self.v = (self.v-self.yoff[0])*self.ymult[0]
        self.i = (self.i-self.yoff[1])*self.ymult[1]
       
    def convert2iv(self):
        """convert IV based on custom measurement setup
        """
        cfg = DAQParamsDipstick(self.fnsetup)
        self.v /= cfg.gain            # apply v amp gain
        self.i *= cfg.i_per_v_swpbias # apply i/v factor

    def get_minmax_wfm(self, data):
        pass

# Datafile: (V, dV/dI) vs (H, I).
class CMData_H_I_V_dVdI:
    def read(self, filename):
        data = np.loadtxt(filename, skiprows=0)
        #self.index = data[:,0]
        self.happ = data[:,0]
        self.iapp = data[:,1]
        self.v = data[:,2]
        self.dvdi = data[:,3]

class CMData_IcArr:
    """Datafile handler for fitted JJ parameters 2016/BB"""
    def __init__(self, filename=None):
        if filename != None:
            self.read(filename)
        self.header = 'Index Control1 Control2 Ic_pos Ic_neg Rn Io Vo Ic_err Rn_err Io_err Vo_err'

    def read(self, filename):
        data = np.loadtxt(filename, skiprows=1)
        self.index, self.happ, self.iapp, self.ic_pos, self.ic_neg, self.rn, self.io, self.vo, self.ic_pos_err, self.ic_neg_err, self.rn_err, self.io_err, self.vo_err = [data[:,k] for k in range(13)]

    def save(self, filename):
        data = np.transpose(np.vstack((self.idx, self.happ, self.iapp, self.ic_pos, self.ic_neg, self.rn, self.io, self.vo, self.ic_pos_err, self.ic_neg_err, self.rn_err, self.io_err, self.vo_err)))
        np.savetxt(filename, data, header=self.header)

class CMData_H_I_Ic_Rn:
    """Datafile handler for fitted JJ parameters (old)"""
    def __init__(self, filename=None):
        if filename != None:
            self.read(filename)
        self.header = 'Index Control1 Control2 Ic Rn Io Vo Ic_err Rn_err Io_err Vo_err'

    def read(self, filename):
        data = np.loadtxt(filename, skiprows=1)
        self.index = data[:,0]
        self.happ = data[:,1]
        self.iapp = data[:,2]
        self.ic = data[:,3]
        self.rn = data[:,4]
        self.io = data[:,5]
        self.vo = data[:,6]

    def save(self, filename):
        data = np.transpose(np.vstack((self.idx, self.happ, self.iapp, self.ic, self.rn, self.io, self.vo)))
        np.savetxt(filename, data, header=self.header)
    
class CMData_H_I_Ic_Rn_pulse:
    """Datafile handler for fitted JJ parameters (pulsed meas)"""
    def __init__(self, filename=None):
        if filename != None:
            self.read(filename)
        self.header = 'Index Control1 Control2 V_ctl Ic Rn Io Vo Ic_err Rn_err Io_err Vo_err'

    def read(self, filename):
        data = np.loadtxt(filename, skiprows=1)
        self.idx = data[:,0]
        self.happ = data[:,1]
        self.iapp = data[:,2]
        self.vapp = data[:,3]
        self.ic = data[:,4]
        self.rn = data[:,5]
        self.io = data[:,6]
        self.vo = data[:,7]

    def save(self, filename):
        data = np.transpose(np.vstack((self.idx, self.happ, self.iapp, self.vapp, self.ic, self.rn, self.io, self.vo)))
        np.savetxt(filename, data, header=self.header)
    
# MPMS datafile access
class MPMSData:
    """ whole data in a file
    """
    def __init__(self, filename):
        self.header = open(filename, 'r').readlines()[:31]
        self.matrix = np.loadtxt(filename, skiprows=31, delimiter=',', \
            usecols=(0,2,3,4,8))
        self.len = len(self.matrix)
        self.units = self.get_units()
        self.itime = 0
        self.ifield = 1
        self.itemp = 2
        self.imoment = 3
        self.ilongerr = 4
        self.area = 36e-6	    # in m2
        #self.separate_seq()

    def get_units(self):
        units = {'Time':'s', 'Field':'Oe', 'Moment':'emu', 'Temperature':'K'}
        return units

    def separate_seq(self):
        eps_h = 0.2
        ictl = self.ifield
        d = self.matrix[1:,ictl] - self.matrix[:-1,ictl]
        iseq = P.nonzero(d > eps_h)[0]      # detect changing control param
        di = iseq[1:] - iseq[:-1]
        boundary = P.nonzero(di > 1)[0]        # detect different sequences
        print(d)
        print(iseq)
        print(di)
        print(boundary)
        self.ihseqstart = np.hstack((P.array(iseq[0]), boundary))
        self.ihseqend = np.hstack((boundary+1, P.array(iseq[-1])))

        print(self.ihseqstart, self.ihseqend)
        return self.ihseqstart, self.ihseqend

    def get_MH(self, wholedata=True, n=0):
        if wholedata==True:
            return self.matrix[:, [self.ifield, self.imoment]]
        else:
            return self.seq[n]   # tuple of MH array and average T?

    def get_M(self):
        return self.matrix[:, self.imoment]

    def get_H(self):
        return self.matrix[:, self.ifield]

    def get_T(self):
        return self.matrix[:, self.itemp]

    def get_long_err(self):
        return self.matrix[:, self.ilongerr]

#~ class MPMSData:
    #~ def __init__(self, filename):
        #~ f = open(filename, 'r')
        #~ for line0 in f:
            #~ line = line0.strip()
            #~ if line == '[Header]':          # check header section
                #~ content = 'header'
                #~ self.header = []
            #~ elif line == '[Data]':          # check data section
                #~ content = 'data'
                #~ self.data = np.array([])
                #~ firstdata = True
            #~ elif content == 'header':
                #~ self.header.append(line)
            #~ elif content == 'data':
                #~ if firstline == True:
                    #~ # read measurement labels
                    #~ self.labels = line.split(',')
                    #~ firstline == False
                #~ else:
                    #~ # read main data
                    
                
        
        #~ self.data = np.loadtxt(filename, skiprows=31, delimiter=',')
        #~ #time = data[:,0]
        #~ #field = data[:,1]
        #~ #temperature = data[:,2]
        #~ #moment = data[:,3]
        

if __name__=='__main__':
    
    filename = 'test'    
    data = DAQParamsDipstick(filename)
    data.readcfgfile()
    data.readdatafile()
    data.convert2iv()
    print(data.i, data.v)
    exit(0)
