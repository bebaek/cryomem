# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Measurement system interfaces.
Mostly for DAQ. Scope interface for analysis as well.

BB 2014
"""

import struct
import instruments_gpib
import instruments_mccdaq
import instruments_rs232
import datafile
from time import sleep, time
import numpy as np
import sys  # for debugging

# DAQ interface
class DAQDipstick:
    def __init__(self, **kwargs):
        self.load_daqparams(**kwargs)
        self.ready_mccdaq = False
        self.ready_sr830 = False
        self.ready_dccurrent = False
        #self.ready_field = False
        self.ready_heat = False
        self.ready_sweepvolt = False
        self.ready_voltmeter = False
        self.ready_scope = False
        self.ready_scopedata = False
        self.ready_lockin = False

    def load_daqparams(self, **kwargs):
        self.daqparams = datafile.DAQParamsDipstick(**kwargs)
        
    # Read primary config file and add/modify params
    def save_daqparams(self, **kwargs):
        #~ for i in range(1, len(args)-1, 2):
            #~ newparams[args[i]] = args[i+1]
        newparams = kwargs
        self.daqparams.params.update(newparams)
        self.daqparams.saveconf_master()

    def set_vout(self, dev, ch, v):
        # Helper function for DAC out.
        
        if dev == 'mccdaq':
            if not self.ready_mccdaq:
                print('First use of MCCDAQ...')
                self.instr_mccdaq = instruments_mccdaq.MCCDAQ()
                self.ready_mccdaq = True
            self.instr_mccdaq.vout(ch, v)
            #print(v)
        else:
            if not self.ready_SR830:
                print('First use of SR830...')
                self.instr_sr830 = instruments_gpib.SR830()
                self.ready_sr830 = True
            self.instr_sr830.dacout(ch, v)

    def ramp_vout(self, dev, ch, **kwargs):
        # Helper function for DAC ramp out.
        
        step = kwargs.get('step', 0.001)

        # setup dependent on DAC
        if dev == 'mccdaq':
            if not self.ready_mccdaq:
                print('First use of MCCDAQ...')
                self.instr_mccdaq = instruments_mccdaq.MCCDAQ()
                self.ready_mccdaq = True
            v1 = kwargs['v1']
            v2 = kwargs['v2']
            delay_dac = 0.01
            #self.instr_mccdaq.vout(ch, v)
        else:
            if not self.ready_SR830:
                print('First use of SR830...')
                self.instr_sr830 = instruments_gpib.SR830()
                self.ready_sr830 = True
            v1 = self.instr_sr830.get_auxvout(self.daqparams.dacch_field)
            v2 = kwargs['v']
            delay_dac = 0.1
            #self.instr_sr830.dacout(ch, v)

        # common codes independent of DAC
        if v1 == v2:
            varray = [v1]
        else:
            step = np.sign(v2-v1)*abs(step)
            varray = np.arange(v1, v2, step)
        t0 = time()
        for v in varray[1:]:
            t = time()
            if t-t0 > 1:
                print('%10.4f'%v, end="", flush=True)
                t0 = t
            self.set_vout(dev, ch, v)
            sleep(delay_dac)
        print('%10.4f'%v2, end="\n", flush=True)
        self.set_vout(dev, ch, v2)

    #
    # basic user functions
    #

    def set_dccurrent(self, **kwargs):
        # if first time, initialize instrument
        if not self.ready_dccurrent:
            print('Connecting to dc current source...')
            self.instr_dccurrent = instruments_gpib.SR830()
            self.ready_dccurrent = True

        i = kwargs.get('i', 0)
        dbl_bias = kwargs.get('dbl_bias', False)
        if dbl_bias:            # 20 mA range
            v = float(i)/self.daqparams.i_per_v_dcbias/2
            if abs(v) > 10:
                v = 10 if v>10 else -10
                print ('Exceeded max V. Setting V = %f' % (v))
            self.instr_dccurrent.dacout(self.daqparams.dacch_bias, v)
            self.instr_dccurrent.dacout(self.daqparams.dacch_bias2, v)
            if 't' in kwargs:         # if pulse
                sleep(kwargs['t'])
                self.instr_dccurrent.dacout(self.daqparams.dacch_bias, 0)
                self.instr_dccurrent.dacout(self.daqparams.dacch_bias2, 0)
        else:                   # 10 mA range
            v = float(i)/self.daqparams.i_per_v_dcbias
            if abs(v) > 10:
                v = 10 if v>10 else -10
                print ('Exceeded max V. Setting V = %f' % (v))
            self.instr_dccurrent.dacout(self.daqparams.dacch_bias, v)
        if 't' in kwargs:         # if pulse
            sleep(kwargs['t'])
            self.instr_dccurrent.dacout(self.daqparams.dacch_bias, 0)
            if dbl_bias:
                self.instr_dccurrent.dacout(self.daqparams.dacch_bias2, 0)
    
    def set_field(self, **kwargs):
        if ('ramp' in kwargs and kwargs['ramp'] == True) or\
                ('h1' in kwargs and 'h2' in kwargs):
            ramp = True
        else:
            ramp = False
        vmax = self.daqparams.i_coil_max/self.daqparams.i_per_v_coil
        if not ramp:    # simple set
            h = kwargs.get('h', 0)
            v = h/self.daqparams.h_per_i/self.daqparams.i_per_v_coil
            if abs(v) > vmax:
                v = vmax if v>vmax else -vmax
                print ('Max V is %f. Setting V = %f'%(vmax, v))
    
            print('Field: ', self.daqparams.dac_field, ', Ch',\
                    self.daqparams.dacch_field, ', %6.4f V'%v)
            self.set_vout(self.daqparams.dac_field, self.daqparams.dacch_field,
              v)
    
            # if pulse, delay and reset.
            if 't' in kwargs: 
                sleep(kwargs['t'])
                self.set_vout(self.daqparams.dac_field,\
                        self.daqparams.dacch_field, 0)

        else:           # ramp
            step = kwargs.get('step', 5)
            if self.daqparams.dac_field == 'mccdaq':
                h1 = kwargs['h1']
                h2 = kwargs['h2']
                delay_dac = 0.01
            elif 'h' in kwargs: # SR830 with only final field given
                h2 = h
                if not self.ready_sr830:
                    print('First use of SR830...')
                    self.instr_sr830 = instruments_gpib.SR830()
                    self.ready_sr830 = True
                h1 = self.instr_sr830.get_auxvout(self.daqparams.dacch_field)
            else:               # SR830 with two fields given
                h1 = kwargs['h1']
                h2 = kwargs['h2']
                delay_dac = 0.1

            # voltage out
            v1 = h1/self.daqparams.h_per_i/self.daqparams.i_per_v_coil
            v2 = h2/self.daqparams.h_per_i/self.daqparams.i_per_v_coil
            vstep = step/self.daqparams.h_per_i/self.daqparams.i_per_v_coil
            if abs(v1) > vmax:
                v1 = vmax if v1>vmax else -vmax
                print ('Max V is %f. Setting V = %f'%(vmax, v1))
            if abs(v2) > vmax:
                v2 = vmax if v2>vmax else -vmax
                print ('Max V is %f. Setting V = %f'%(vmax, v2))
            self.ramp_vout(self.daqparams.dac_field,\
                    self.daqparams.dacch_field, v1=v1, v2=v2, step=vstep)

            # if pulse, delay and reset.
            if 't' in kwargs: 
                sleep(kwargs['t'])
                self.ramp_vout(self.daqparams.dac_field,\
                        self.daqparams.dacch_field, v1=v2, v2=0, step=vstep)
                        
    def set_heat(self, **kwargs):
        # if first time, initialize instrument
        if not self.ready_heat:
            print('Connecting to heat source...')
            self.instr_heat = instruments_gpib.SR830()
            self.ready_heat = True

        i = kwargs.get('i', .09)
        if abs(i) > .1:
            i = .1 if i > .1 else -.1
            print ('Exceeded max I. Setting I = %f' % (i))
        v = i/self.daqparams.i_per_v_heat
        self.instr_heat.dacout(self.daqparams.dacch_heat, v)
        if 't' in kwargs:         # if pulse
            sleep(kwargs['t'])
            self.instr_heat.dacout(self.daqparams.dacch_heat, 0)

    def sqwave_field(self, **kwargs):
        # if first time, initialize instrument
        if not self.ready_field:
            print('Connecting to field source...')
            self.instr_field = instruments_gpib.SR830()
            self.ready_field = True

        h = kwargs.get('h', 0)
        v = h/self.daqparams.h_per_i/self.daqparams.i_per_v_coil
        if abs(v) > 2:
            v = 2 if v>2 else -2
            print ('Exceeded max V. Setting V = %f' % (v))
        while 1:
            self.instr_field.dacout(self.daqparams.dacch_field, v)
            h1 = self.instr_field.get_auxvout(self.daqparams.dacch_field)\
              *self.daqparams.h_per_i*self.daqparams.i_per_v_coil
            self.instr_field.dacout(self.daqparams.dacch_field, 0)
            h1 = self.instr_field.get_auxvout(self.daqparams.dacch_field)\
              *self.daqparams.h_per_i*self.daqparams.i_per_v_coil
        if 't' in kwargs:         # if pulse
            sleep(kwargs['t'])
            self.instr_field.dacout(self.daqparams.dacch_field, 0)
    
    def set_sweepvolt(self, v):
        # if first time, initialize instrument
        if not self.ready_sweepvolt:
            print('Connecting to voltage sweeper...')
            self.instr_sweepvolt = instruments_gpib.DS345()
            self.ready_sweepvolt = True

        if abs(v) > 10:
            v = 10 if v > 10 else -10
            print ('Exceeded max sweep V amplitude. Setting to %f...' % (v))
        self.instr_sweepvolt.setampl(v)

    def get_sweepvolt(self):
        # if first time, initialize instrument
        if not self.ready_sweepvolt:
            print('Connecting to voltage sweeper...')
            self.instr_sweepvolt = instruments_gpib.DS345()
            self.ready_sweepvolt = True

        return self.instr_sweepvolt.getampl()

    def get_volt(self):
        # if first time, initialize instrument
        if not self.ready_voltmeter:
            print('Connecting to voltmeter...')
            self.instr_voltmeter = instruments_gpib.KT2001()
            self.ready_voltmeter = True

        return self.instr_voltmeter.fetch()/self.daqparams.gain

    # set lock-in sine out (amplitude and/or frequency)
    def set_accurrent(self, **kwargs):
        # if first time, initialize instrument
        if not self.ready_lockin:
            print('Connecting to lockin...')
            self.instr_lockin = instruments_gpib.SR830()
            self.ready_lockin = True
        
        if 'ampl' in kwargs:
            ampl = kwargs['ampl']/self.daqparams.i_per_v_acbias
            self.instr_lockin.sinelvl(ampl)
        if 'freq' in kwargs:
            self.instr_lockin.freq(kwargs['freq'])
    
    # get lock-in out
    def get_dvdi(self, ch=1):
        # if first time, initialize instrument
        if not self.ready_lockin:
            print('Connecting to lockin...')
            self.instr_lockin = instruments_gpib.SR830()
            self.ready_lockin = True

        #return self.instr_lockin.getdisp(ch)/self.daqparams.gain/ \
        #  (self.daqparams.ampl_lockin*self.daqparams.i_per_v_acbias)
        return self.instr_lockin.getdisp(ch)/self.daqparams.gain/ \
          self.daqparams.ampl_lockin

    def set_scopedatafmt(self, fmt):
        # if first time, initialize instrument
        if not self.ready_scope:
            print('Connecting to scope...')
            self.instr_scope = instruments_rs232.TDS2000()
            self.ready_scope = True

        if fmt == 'bin':
            self.instr_scope.setdatafmtbin()
        else:
            pass

    def save_scopeconf(self):
        # if first time, initialize instrument
        if not self.ready_scope:
            print('Connecting to scope...')
            self.instr_scope = instruments_rs232.TDS2000()
            self.ready_scope = True
        if not self.ready_scopedata:
            self.scopedata = datafile.IVArrayBin8b(self.daqparams.datafilename)
            self.ready_scopedata = True

        def savewfmdata(f, ch):
            msg = self.instr_scope.getwfmparam(ch)       # get waveform parameters
            self.scopedata.savewfmdata(f, msg)
            #print(msg)
            #f.write(msg)                # save params in separate file

        f = open(self.daqparams.datapath + '\\' + \
          self.daqparams.datafilename+'.osccfg', 'w')
        savewfmdata(f, 1)
        savewfmdata(f, 2)
        f.close()

    def trig_scope(self):
        # if first time, initialize instrument
        if not self.ready_scope:
            print('Connecting to scope...')
            self.instr_scope = instruments_rs232.TDS2000()
            self.ready_scope = True

        print('Scope: measuring...')
        self.instr_scope.acquiresingle()
    
    def get_iv(self):
        # if first time, initialize instrument
        if not self.ready_scope:
            print('Connecting to scope...')
            self.instr_scope = instruments_rs232.TDS2000()
            self.ready_scope = True

        print('Scope: downloading trace2 (I)...')
        i = self.instr_scope.gettracebin(2)
        print('Scope: downloading trace1 (V)...')
        v = self.instr_scope.gettracebin(1)
        return i, v
    
    def save_scalars_txt(self, f, sarr):
        # save typical scalar results sarr=[s1, s2, ...] in a text file
        
        msg = '\t'.join(map(str, sarr))
        f.write(msg+'\n')
        f.flush()

    def save_ivarray_2scalars(self, f, s1, s2, v1, v2):
        # two scalars (s1, s2) and two vectors (v1, v2) in binary array format

        # if first time, initialize instrument
        if not self.ready_scopedata:
            self.scopedata = datafile.IVArrayBin8b(self.daqparams.datafilename)
            self.ready_scopedata = True
        
        # (ih: 1x 4 byte float) + (i: 2500x 1 byte int) + (v: 2500x 1 byte int)
        outdata = struct.pack('f', s1) + struct.pack('f', s2) + v1 + v2
        f.write(outdata)
        f.flush()

    def save_ivarray_3scalars(self, f, s1, s2, s3, v1, v2):
        # two scalars (s1, s2) and two vectors (v1, v2) in binary array format

        # if first time, initialize instrument
        if not self.ready_scopedata:
            self.scopedata = datafile.IVArrayBin8b(self.daqparams.datafilename)
            self.ready_scopedata = True
        
        # (ih: 1x 4 byte float) + (i: 2500x 1 byte int) + (v: 2500x 1 byte int)
        outdata = struct.pack('f', s1) + struct.pack('f', s2) \
          + struct.pack('f', s3) + v1 + v2
        f.write(outdata)
        f.flush()

    def center_y(self, ch, v):
        yoff = self.instr_scope.get_yoff(ch)
        ymult = self.instr_scope.get_ymult(ch)
        yscale = self.instr_scope.get_vscale(ch)
        y = self.instr_scope.wfm2array(v, yoff, ymult)
        ymid = (max(y) + min(y))/2
        div = round(-ymid/yscale, 2)
        print('Setting vertical position with %.2f...'%div)
        self.instr_scope.set_vpos(ch, div)

# helper functions

def build_sweepseq(swpparams):
    # swpparams = [a0, astep0, a1, astep1, a2, ...] or just [a0]
    
    carray = np.array([])
    nseg = int((len(swpparams)-1)/2)
    print("nseg =", nseg)
    if nseg == 0:
        carray = np.array([swpparams[0]])
    else:
        for k in range(nseg):
            swpstart = swpparams[k*2]
            swpstep  = swpparams[k*2+1]
            swpend   = swpparams[k*2+2]
            
            # bypass floating point anomaly in arange
            if (swpstep < 100):
                #print -np.log10(swpstep/100)
                m = 10**np.ceil(-np.log10(abs(swpstep)/100))
                #print("m =", m)
                swpstart = round(m*swpstart)
                swpstep  = round(m*swpstep)
                swpend   = round(m*swpend)
            else:
                m = 1
            #print(swpstart, swpstep, swpend)
            carray = np.hstack((carray, np.arange(swpstart, swpend, swpstep)/m))
        carray = np.hstack((carray, np.array([swpend/m])))
    print(carray)
    return carray

# shell interfaces 

def save_daqparams(**kwargs):
    DAQDipstick().save_daqparams(**kwargs)
    sleep(1)

def set_dccurrent(**kwargs):
    DAQDipstick().set_dccurrent(**kwargs)
    sleep(1)
    
def set_field(**kwargs):
    DAQDipstick().set_field(**kwargs)
    sleep(1)

def set_heat(**kwargs):
    DAQDipstick().set_heat(**kwargs)
    sleep(1)

def sqwave_field(**kwargs):
    DAQDipstick().sqwave_field(**kwargs)
    sleep(1)

def set_sweepvolt(v):
    DAQDipstick().set_sweepvolt(v)
    sleep(1)

def get_sweepvolt():
    print(DAQDipstick().get_sweepvolt())
    sleep(1)

def set_accurrent(**kwargs):
    DAQDipstick().set_accurrent(**kwargs)
    sleep(1)

def get_dvdi():
    print(DAQDipstick().get_dvdi())
    sleep(1)

def reset_allsrc():
    meas = DAQDipstick()
    meas.set_dccurrent(i=0, dbl_bias=True)
    meas.set_field(h=0)
    meas.set_heat(i=0)
    meas.set_sweepvolt(0)
    meas.set_accurrent(ampl=0)
    sleep(1)

# measure V and dV/dI with swept I (continuous or pulsed).
def get_v_dvdi_vs_h_i(**kwargs):
    # swpparams: a=[a0, astep0, a1, astep1, a2, ...] or just [a0]
    # a can be h (field) and/or i (current)
    
    swpparams1 = kwargs.get('h', [0])
    swpparams2 = kwargs.get('i', [0])
    pulse = kwargs.get('pulse', False)
    dbl_bias = kwargs.get('dbl_bias', False)
    meastype = 'V_dVdI_vs_Ipulse' if pulse else 'V_dVdI_vs_I'
    
    # main interface    
    meas = DAQDipstick(meastype = meastype)

    # build sweep sequence
    c1 = build_sweepseq(swpparams1)        # control 1 (field)
    c2 = build_sweepseq(swpparams2)        # control 2 (current)
    
    # save configuration
    meas.daqparams.saveconf()
    
    # main loop
    outpath = meas.daqparams.datapath + '/' + meas.daqparams.datafilename + '.dat'
    fout = open(outpath, 'w')
    print('Data file: %s'%outpath)
    print('Setting initial state...')
    if pulse:
        meas.set_dccurrent(i=0, dbl_bias=dbl_bias)      # initial state
        meas.set_field(h=0)
        meas.set_accurrent(freq=meas.daqparams.f_lockin)
        # caution: ampl_lockin is now current, not voltage
        meas.set_accurrent(ampl=0)
    else:
        meas.set_dccurrent(i=c2[0], dbl_bias=dbl_bias)      # initial state
        meas.set_field(h=c1[0])
        meas.set_accurrent(freq=meas.daqparams.f_lockin)
        # caution: ampl_lockin is now current, not voltage
        meas.set_accurrent(ampl=meas.daqparams.ampl_lockin)
    print("Initial delay 10s...\n"); sleep(10)
    for n1 in range(len(c1)):
        for n2 in range(len(c2)):
            h = c1[n1]; i = c2[n2]
            
            # Apply bias(es)
            if pulse:
                meas.ramp_field(0, h); sleep(1)             # field on
                meas.set_dccurrent(i=i, dbl_bias=dbl_bias)  # I pulse on
                print('Delay for %.1f s...'%meas.daqparams.tsettle2)
                sleep(meas.daqparams.tsettle2)
                v2 = meas.get_volt()                     # read V
                meas.set_dccurrent(i=0, dbl_bias=dbl_bias); sleep(1)
                meas.ramp_field(h, 0)  # pulses off
                meas.set_heat(i=.09, t=5); sleep(2)         # heat pls
                print('Ac bias sweep on...');         
                meas.set_accurrent(ampl=meas.daqparams.ampl_lockin)
                print('Stabilizing for %.1f s...'%meas.daqparams.tsettle1)
                sleep(meas.daqparams.tsettle1)
            else:
                meas.set_field(h=c1[n1])
                meas.set_dccurrent(i=c2[n2], dbl_bias=dbl_bias)
                print('Stabilizing for %.1f s...'%meas.daqparams.tsettle1)
                sleep(meas.daqparams.tsettle1)
            
            # Read signals
            v = meas.get_volt()
            dvdi = meas.get_dvdi()
            if pulse:
                #print('Bias current off...'); meas.set_sweepvolt(0)
                pass

            # Save data
            if pulse:
                print([h, i, v, dvdi, v2])
                meas.save_scalars_txt(fout, [h, i, v, dvdi, v2])
                #meas.save_ivarray_3scalars(fout, h, i, v2, vout, iout)
            else:
                print([h, i, v, dvdi])
                meas.save_scalars_txt(fout, [h, i, v, dvdi])
    
    fout.close()

    # finish up
    print('Data file: %s'%outpath)
    print('Done!')
    sleep(1)

# measure IV with swept field and/or current (continuous or pulsed).
def get_vitrace_vs_h_i(**kwargs):
    # swpparams: a=[a0, astep0, a1, astep1, a2, ...] or just [a0]
    # a can be h (field) or i (current)
    
    swpparams1 = kwargs.get('h', [0])
    swpparams2 = kwargs.get('i', [0])
    pulse = kwargs.get('pulse', False)
    dbl_bias = kwargs.get('dbl_bias', False)
    meastype = 'VItrace-HIpulse' if pulse else 'VItrace-HI'
    
    # main interface    
    meas = DAQDipstick(meastype = meastype)

    # build sweep sequence
    c1 = build_sweepseq(swpparams1)        # control 1 (field)
    c2 = build_sweepseq(swpparams2)        # control 2 (current)
    
    # read V bias and save configuration
    vswpbias0 = meas.get_sweepvolt()
    addedparams = { 'sweep voltage amplitude':str(vswpbias0) }
    meas.daqparams.saveconf2(addedparams)
    
    # setup scope
    print('Setting up oscilloscope...')
    meas.set_scopedatafmt('bin')
    meas.save_scopeconf()
    
    #~ # helper function for biasing
    #~ def set_idcbias(i):
        #~ if dbl_bias:        
            #~ meas.set_dccurrent(i=i, dbl_bias=True)
        #~ else:
            #~ meas.set_dccurrent(i=i)
        
    # main loop
    outpath = meas.daqparams.datapath + '/' + meas.daqparams.datafilename + '.dat'
    fout = open(outpath, 'wb')
    print('Data file: %s'%outpath)
    print('Setting initial state...')
    if pulse:
        meas.set_dccurrent(i=0, dbl_bias=dbl_bias)      # initial state
        meas.set_field(h=0)
        meas.set_sweepvolt(0)
    else:
        meas.set_dccurrent(i=c2[0], dbl_bias=dbl_bias)      # initial state
        meas.set_field(h=c1[0])
    print("Initial delay 10s...\n"); sleep(10)
    for n1 in range(len(c1)):
        for n2 in range(len(c2)):
            h = c1[n1]; i = c2[n2]
            
            # Apply bias(es)
            if pulse:
                meas.set_field(h1=0, h2=h, step=5); sleep(1)    # field on
                meas.set_dccurrent(i=i, dbl_bias=dbl_bias)      # I pulse on
                print('Delay for %.1f s...'%meas.daqparams.tsettle2)
                sleep(meas.daqparams.tsettle2)
                v2 = meas.get_volt()                        # read V
                meas.set_dccurrent(i=0, dbl_bias=dbl_bias); sleep(1)
                meas.set_field(h1=h, h2=0, step=5)          # pulses off
                meas.set_heat(i=.09, t=5); sleep(2)         # heat pls
                print('Bias sweep on...'); meas.set_sweepvolt(vswpbias0)
                print('Stabilizing for %.1f s...'%meas.daqparams.tsettle1)
                sleep(meas.daqparams.tsettle1)
            else:
                meas.set_field(h=c1[n1])
                meas.set_dccurrent(i=c2[n2], dbl_bias=dbl_bias)
                print('Stabilizing for %.1f s...'%meas.daqparams.tsettle1)
                sleep(meas.daqparams.tsettle1)
            
            # center y curve based on previous curve
            if n1 > 0 or n2 >0:
                meas.center_y(1, vout)

            # Trigger scope
            meas.trig_scope(); sleep(0.1)
            if pulse:
                print('Bias sweep off...'); meas.set_sweepvolt(0)

            # Download and save data
            iout, vout = meas.get_iv()
            if pulse:
                print(h, i, v2, len(vout), len(iout))
                print('Saving to a file...\n')
                meas.save_ivarray_3scalars(fout, h, i, v2, vout, iout)
            else:
                print(h, i, len(vout), len(iout))
                print('Saving to a file...\n')
                meas.save_ivarray_2scalars(fout, h, i, vout, iout)
    
    fout.close()

    # finish up
    if pulse:
        print('Bias sweep on...'); meas.set_sweepvolt(vswpbias0)
    #meas.set_dccurrent(i=0, dbl_bias=dbl_bias)  # dc bias off
    print('Data file: %s'%outpath)
    print('Done!')
    sleep(1)

# call DAQ user functions from shell command line
def runfromshell(args):
    def str2bool(s):
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            raise ValueError
            
    if len(args) < 2:
        print('')
        print('Usage: python daq_dipstick.py <command> [<arguments>]\n')
        print('Examples:')
        print('python daq_dipstick.py reset_allsrc')
        print('python daq_dipstick.py set_dccurrent i=1e-4')
        print('python daq_dipstick.py set_dccurrent i=1e-4 t=3')
        print('python daq_dipstick.py set_field h=80')
        print('python daq_dipstick.py set_field h1=0 h2=1000 t=5')
        print('python daq_dipstick.py set_heat t=3')
        print('python daq_dipstick.py sqwave_field h=150')
        print('python daq_dipstick.py set_sweepvolt .7')
        print('python daq_dipstick.py get_sweepvolt')
        print('python daq_dipstick.py set_accurrent ampl=1e-6 freq=190')
        print('python daq_dipstick.py get_dvdi')
        print('python daq_dipstick.py get_vitrace_vs_h_i h=0,20,100,-20,0 '
          'pulse=True')
        print('python daq_dipstick.py get_vitrace_vs_h_i h=100 '
          'i=0,.001,.02,-.001,-.02,.001,.02 dbl_bias=True')
        print('python daq_dipstick.py get_v_dvdi_vs_h_i h=100 '
          'i=0,.001,.02,-.001,-.02,.001,.02 dbl_bias=True')
        print('python daq_dipstick.py save_daqparams "datafile tag = jj0_CIMS"')
        sys.exit(0)
    func = args[1]
    #print(args[2])
    posargs = []
    kwargs = {}
    if func in ['set_dccurrent', 'set_field', 'set_heat', 'reset_allsrc',\
      'set_sweepvolt', 'get_sweepvolt', 'sqwave_field', 'save_params',\
      'save_daqparams', 'set_accurrent', 'get_dvdi']:
        # easy ones: no list argument
        for arg in args[2:]:
            try:
                posargs.append(float(arg))
            except ValueError:
                pass
            try:
                tmp = arg.split('=')
                kw = tmp[0].strip()
                val = tmp[1].strip()
                if val:
                    try:
                        kwargs[kw] = float(val)
                    except ValueError:
                        try:
                            kwargs[kw] = str2bool(val)
                        except ValueError:
                            kwargs[kw] = val
                    print(kw, kwargs)
            except (ValueError, IndexError):
                pass
    elif func in ['get_vitrace_vs_h_i', 'get_v_dvdi_vs_h_i']:
        # less easy ones: list arguments as main
        for arg in args[2:]:
            try:
                newposarg = list(map(float, arg.split(',')))
                posargs.append(newposarg)
            except ValueError:
                pass
            try:
                kw, val = arg.split('=')
                if val:
                    #~ try:
                        #~ kwargs[kw] = float(val)
                    #~ except ValueError:
                    try:
                        kwargs[kw] = list(map(float, val.split(',')))
                    except ValueError:
                        kwargs[kw] = str2bool(val)
            except ValueError:
                pass
    print(posargs)
    print(kwargs)
    globals()[func](*posargs, **kwargs)
            
if __name__=='__main__':
    
    import sys    
    print(sys.version)
#    meas = MeasSysDipstick()
#    meas.instr_heat.set_i(t=1)
#    set_dccurrent(i=1e-5, t=1)
    #reset_allsrc()
    #get_vitrace_vs_h_i([0,50,100,-50,0], [0], pulse=True)
    runfromshell(sys.argv)
    
