# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
MCC DAQ

bb
"""

import ctypes
from time import sleep

# D/A range codes (gain)
bip10volts = 1              # -10 to +10 Volts

daqdll = ctypes.windll.LoadLibrary('cbw64')

class MCCDAQ:
    def __init__(self, **kwargs):
        self.setparams(**kwargs)
    
    def setparams(self, **kwargs):
        self.boardnum = kwargs.get('boardnum', 0)
        self.ch_arr = kwargs.get('ch_arr',[0])
        self.gain_arr = kwargs.get('gain_arr',[bip10volts])
        
    def vout(self, ch, v):
        gain = self.gain_arr[self.ch_arr == ch]
        v = ctypes.c_float(v)
        options = 0
        errcode = daqdll.cbVOut(self.boardnum, ch, gain, v, options)
        if errcode != 0:
            print('DAC errcode = ', errcode)
        
    # waveform out; under development
    def vout_scan(self, ch_arr, ch_type_arr, gain_arr, ch_cnt, rate,\
      count, da_data, options):
        bufsize = 4
        rate = ctypes.create_string_buffer(bufsize)
        errcode = daqdll.cbAOutScan(self.boardnum, ch_arr, ch_type_arr, \
          gain_arr, ch_cnt, rate, count, da_data, options)
        
if __name__ == '__main__':
    dev = MCCDAQ()

    # single output
    #v = 0
    #print('Setting V = ', v)
    #dev.vout(0, v)
    
    # array out (one by one)
    import numpy as np
    for v in np.arange(1, -0.001, -0.001):
        print(v)
        dev.vout(0, v)
        sleep(0.01)
    
    print('done.')
    sleep(1)
