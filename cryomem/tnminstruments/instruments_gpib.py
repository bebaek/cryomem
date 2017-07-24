# -*- coding: utf-8 -*-
"""
GPIB instruments

bb
"""

from __future__ import division
#from ctypes import windll, create_string_buffer
import ctypes
from time import sleep
#from string import strip
#from math import copysign

# GPIB addresses. Change as needed.
addrag34420a = 23   #voltlab
addrsr830 = 9   # maglab
addrls330 = 15   # maglab
addrkt2001 = 11  # maglab
addrds345 = 8   # maglab
addrxdl = 12  # maglab

try:
    #gpibdll = windll.LoadLibrary('gpib-32') # old way
    gpibdll = ctypes.windll.LoadLibrary('ni4882')
except:
    print('Cannot load ni4882.dll. GPIB will not work.', flush=True)

class GPIB:
    def __init__(self, addr):
        timeout = 10
        self.addr = addr
        self.ud = gpibdll.ibdev(ctypes.c_int(0),ctypes.c_int(self.addr),\
          ctypes.c_int(0),ctypes.c_int(timeout),ctypes.c_int(1),ctypes.c_int(0))
        #print(self.ud)
        #print('ibdev=',getattr(gpibdll, 'ibdev'))
        gpibdll.ibclr(self.ud)
        self.write('*IDN?')
        sleep(0.1)
        msg = self.read()
        print(msg, flush=True)

    def write(self, cmd):
        msg = gpibdll.ibwrt(self.ud, (cmd+'n').encode('utf-8'), len(cmd))
        sleep(0.1)
        return msg

    def read(self, bufsize=100):
        buf = ctypes.create_string_buffer(bufsize)
        msg = gpibdll.ibrd(self.ud, buf, bufsize)
        #return repr(buf.value)
        return buf.value.decode('utf-8')

    def close(self):
        # return control
        gpibdll.ibonl(self.ud, 0)
        print ('GPIB #%d offline.'%self.addr, flush=True)

class HP34420A(GPIB):
    # voltmeter with analog out
    def __init__(self):
        GPIB.__init__(self, addrag34420a)

    def dacout(self, voltage):
        #print ('%6.3f'%voltage)
        self.write('OUTP:REF:VAL %6.3f'%voltage)    # ~1 mV resolution
        self.write('OUTP:STAT ON')

    def dacoff(self):
        self.write('OUTP:REF:VAL 0')
        self.write('OUTP:STAT OFF')

class SR830(GPIB):
    # SRS lock-in
    def __init__(self):
        GPIB.__init__(self, addrsr830)
        self.vsens = [2e-9, 5e-9, 10e-9, 2e-8, 5e-8, 10e-8, 2e-7, 5e-7, 10e-7,\
            2e-6, 5e-6, 10e-6, 2e-5, 5e-5, 10e-5, 2e-4, 5e-4, 10e-4,\
            2e-3, 5e-3, 10e-3, 2e-2, 5e-2, 10e-2, 2e-1, 5e-1, 10e-1]


    # r = sqrt(x2+y2) in V
    def get_r(self):
        self.write('OUTP? 3')
        return float(self.read())

    # needed in offset subtracted measurements
    def get_offset(self):
        self.write('SENS?')             # get range
        msg = self.read()
        print(msg, flush=True)
        idx = int(msg)
        sens = self.vsens[idx]

        self.write('OEXP? 3')             # get R offset (%)
        off, exp = tuple(map(float, self.read().split(',')))

        return sens*off/100

    # use get_r instead
    def getdisp(self, ch):
        self.write('OUTR? %d'%ch)
        msg = self.read()
        return float(msg)

    # get r = sqrt(x**2 + y**2) calculated with offset and expand
    def get_r_(self, ch):
        disp = self.getdisp(ch)     # get display
        self.write('OEXP? 3')       # get offset/expand
        off, exp = tuple(map(float, self.read().split(',')))
        return disp

    def dacout(self, ch, voltage):
        self.write('AUXV %d,%7.3f'%(ch,voltage))    # 1 mV resolution
        print ('AUXV %d,%7.3f'%(ch,voltage), flush=True)

    def get_auxvout(self, ch):
        self.write('AUXV? %d'%ch)
        msg = self.read()
        return float(msg)
        
    def dacoff(self, ch):
        self.write('AUXV %d,%7.3f'%(ch,0))    # 1 mV resolution

    def sinelvl(self, v):
        if v < 0.004:
            v = 0.004
            print('Setting to lower limit, %5.3f'%v, flush=True)
        msg = 'SLVL %7.3f'%v
        self.write(msg)
        print (msg, flush=True)
        
    def freq(self, v):
        msg = 'FREQ %9.4f'%v
        self.write(msg)
        print (msg, flush=True)
        
class LS330(GPIB):
    # Lakeshore temperature controller
    def __init__(self):
        GPIB.__init__(self, addrls330)

    def getsampledata(self):
        self.write('SDAT?')
        msg = self.read()
        return float(msg)

class KT2001(GPIB):
    # Keithley 2001 voltmeter
    def __init__(self):
        GPIB.__init__(self, addrkt2001)

    def fetch(self):
        self.write(':FETC?')
        msg = self.read()
##         print 'dmm msg = ', msg
        v = msg.split(',')[0].rstrip('NVDC')
        if v[-1] == 'R':
            return float(v[:-1])
        else:
            return float(v)

class DS345(GPIB):
    """Stanford DS345 function generator"""
    waveform = {'sine':'0', 'square':'1', 'triangle':'2', 'ramp':'3', 'noise':'4'}
    def __init__(self):
        GPIB.__init__(self, addrds345)

    def set_waveform(self, s):
        """Set waveform"""
        self.write('FUNC {}'.format(self.waveform[s]))

    def set_freq(self, f):
        self.write('FREQ {:d}'.format(f))

    def set_ampl(self, v):
        msg = ('AMPL {:f}'.format(v)).rstrip('0')+' VP'
        self.write(msg)

    def setampl(self, v):
        msg = ('AMPL %f'%v).rstrip('0')+' VP'
        print (msg, flush=True)
        self.write(msg)

    def getampl(self):
        msg = 'AMPL?'
        self.write(msg)
        #print('Msg:', msg)
        msg = self.read()
        #print('DS345:',msg)
        v = float(msg.split('VP')[0])
        return v

class XDL(GPIB):
    # Sorensen XDL dc power
    def __init__(self):
        GPIB.__init__(self, addrxdl)
        

    def set_v(self, ch, v):
        msg = 'V{:d} {:f}'.format(ch, v)
        self.write(msg)

    def set_i(self, ch, i):
        msg = 'I{:d} {:f}'.format(ch, i)
        print(msg, flush=True)
        self.write(msg)

    def set_output(self, ch, val):
        # ch=1 or 2; val=0 for off 1 for on
        msg = 'OP{:d} {:d}'.format(ch, val)
        print(msg, flush=True)
        self.write(msg)

if __name__ == '__main__':
    #dev = DS345()
    #dev.setampl(1); sleep(1); dev.setampl(0)
    #print (dev.getampl())
    
    #~ dev = SR830()
    #~ dev.dacout(1, 0.1)
    #~ print(dev.get_auxvout(1))
    #~ sleep(1)
    #~ dev.dacout(1, 0)
    #~ print(dev.get_auxvout(1))

    dev = SR830()
    print(dev.get_offset())

    
    #dev = XDL()
    #dev.set_v(1,0.12)
    #dev.set_output(1, 1)
    #sleep(1)
    #dev.set_output(1, 0)

