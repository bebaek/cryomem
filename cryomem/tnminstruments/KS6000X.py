from sys import exit
from struct import unpack
import numpy as np
import matplotlib.pyplot as plt
from .base import Interface


class KS6000X(Interface):
    """Keysight 6000 X-series oscilloscope"""
    def __init__(self, interface='USB0::0x0957::0x1790::MY54130118::INSTR'):
        super().__init__(interface)
        self.timeout = 10000
        self.write('*CLS')                  # system clear?
        self.clear()                        # clear buffer?
        if int(self.query('*OPC?')) != 1:   # wait for op complete
            print('Init: OP complete check failed.')

    def config_wfm(self, **kwargs):
        """Config waveform acquisition.

        Keyword arguments:
            ch: List of integers. Channels to read.
            mode: String. 'average' or another.
            navg: Integer. Number of average.
        """
        mode = kwargs.get('mode', 'manual')
        self.ch = kwargs.get('ch', [1])
        self.npts = kwargs.get('npts', 2000)
        
        self.yref, self.yinc, self.yor = {}, {}, {}
        self.write(':STOP')  # continuous run mode needs be stopped
        if mode == 'average':
            self.write(':ACQ:TYPE AVER')
            self.write(':ACQ:COUN %d' % kwargs.get('navg', 32))
        for c in self.ch:
            self.write(':WAV:SOUR CHAN{}'.format(c))  # chan to config
            self.write(':WAV:POIN %d' % self.npts)         # n of points
            self.write(':WAV:FORM WORD')              # 16 bit binary

            s0 = int(self.query(':WAV:UNS?'))   # signed or unsigned?
            self.s = 'h' if s0 == 0 else 'H'
            bo = self.query(':WAV:BYT?')[:4]    # byte order?
            self.bo = '<' if bo == 'LSBF' else '>'

            # Read config
            if int(self.query('*OPC?')) == 1:   # wait for op complete
                cfg0 = self.query(':WAV:PRE?')
                print('ch%d preamble:' % c, cfg0)
                cfg1 = cfg0.split(',')
                #self.npts[c] = int(cfg1[2])
                self.yinc[c] = float(cfg1[7])
                self.yor[c] = float(cfg1[8])
                self.yref[c] = int(cfg1[9])                
            else:
                print('Operation complete check error.')
                exit(1)

    def acquiresingle(self):
        """Run single shot acquisition."""
        self.write(':DIG')
        #sleep(0.1)

    def get_wfm(self, **kwargs):
        """Get waveforms. Run config_wfm() once before.

        Keyword arguments:
            acquire: Bool. Default: False. Include running acquiresingle().
        """
        acq = kwargs.get('acquire', False)
        scale = kwargs.get('scale', [1])
        
        if acq:
            self.acquiresingle()
            while int(self.query('WAV:POIN?')) != self.npts:
                print('Bad number of points. Re-acquiring...')
                self.acquiresingle()
            
        wfms = []
        for k, c in enumerate(self.ch):
            self.write(':WAV:SOUR CHAN{}'.format(c))
            self.write(':WAV:DATA?')
            wfm0 = self.read_raw()
            print('Header:', wfm0[:10])
            wfm1 = unpack('%c%d%c' % (self.bo, self.npts, self.s),
                           wfm0[10:-1])
            wfms += [((np.array(wfm1) - self.yref[c])*self.yinc[c]
                      + self.yor[c])*scale[k]]
        return np.array(wfms).transpose()

    
def test():
    dev = KS6000X('USB0::0x0957::0x1790::MY54130118::INSTR')
    dev.config_wfm(ch=[1,2], mode='average')
    data = dev.get_wfm(acquire=True)
    print(data)
    for c in data:
        plt.plot(data[c])
    plt.show()

    
if __name__ == '__main__':
    test()
