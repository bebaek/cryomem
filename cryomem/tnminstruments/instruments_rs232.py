"""
Created on Thu Jan 31 10:59:49 2013

@author: BB
"""

from time import sleep
import numpy as np
import struct
try:
    import serial
except:
    print('pyserial is not installed. RS232 won\'t work.')

porttds2000 = 4   # 5 -> COM4

class TDS2000:
    def __init__(self, **kwargs):
        port = kwargs.get('port', porttds2000)
        to = kwargs.get('timeout', 20)
        self.verbose = kwargs.get('verbose', False)
        self.port = port
        self.ndata = 2500
        self.ser = serial.Serial(self.port, 19200, bytesize=8, timeout=to)
        self.write('*CLS')
        self.write('*ESR?')
        #print (self.ser.readline())
        print(self.read())
        self.write('ALLEV?')
        #print (self.ser.readline())
        print(self.read())
        #vscale_div = {.002: 1000, .005:400, .01:200, .02:100, .05:40,\
        #        .1:20, .2:10, .5:100, 1:50, 2:25, 5:10}

    def write(self, msg):
        msg2 = (msg+'\n').encode('utf-8')
        if self.verbose:
            print(msg2)
        self.ser.write(msg2)
        sleep(0.1)

    def read(self):
        return self.ser.readline().decode('utf-8')
        
    def acquiresingle(self):
        self.write('ACQ:STOPA SEQ')
        self.write('ACQ:STATE ON')
        self.write('*OPC?')
        sleep(.1)
        msg = self.read()
        if msg != '1\n':
            msg = 'timeout'
            print ('Scope trigger time out!')
        return msg

    def run(self):
        self.write('ACQ:STOPA RUST')
        self.write('ACQ:STATE RUN')

    def stop(self):
        self.write('ACQ:STOPA RUST')
        self.write('ACQ:STATE STOP')

    def setdatafmtascii(self):
        self.write('DAT:ENC ASCII')

    def setdatafmtbin(self):
        self.write('DAT:ENC RIB')
        #self.write('DAT:ENC ASCII')
        #self.ser.write('DAT:STAR 1\n')
        #self.ser.write('DAT:STOP 2500\n')

    def getwfmparam(self, ch):
        self.write('DAT:SOU CH%d'%ch)
        self.write('WFMPRE?')
        msg = self.read()
        return msg

    def gettraceascii(self, ch):
        self.write('DAT:SOU CH%d'%ch)
        self.write('CURV?')
        msg = self.read()
        return msg

    def gettracebin(self, ch):
        self.write('DAT:SOU CH%d'%ch)
        self.write('CURVE?')
        msg = self.ser.read(self.ndata+7)
        return msg[6:-1]

    def wfm2array(self, wfm, yoff, ymult):
        arr = (np.array(struct.unpack('%db'%len(wfm), wfm)) - yoff)*ymult
        return arr

    def get_yoff(self, ch):
        self.write('DAT:SOU {}'.format(ch))
        self.write('WFMP:YOF?')
        msg = self.read()
        return float(msg)

    def get_ymult(self, ch):
        self.write('DAT:SOU {}'.format(ch))
        self.write('WFMP:YMU?')
        msg = self.read()
        return float(msg)

    def set_vscale(self, ch, scale):
        """Set vertical scale of CH1, ... to 100E-3, ..."""
        if type(ch) == str:
            self.write('{}:SCA {}'.format(ch, scale))
        else:
            self.write('CH{}:SCA {}'.format(ch, scale))

    def get_vscale(self, ch):
        if type(ch) == str:
            self.write('{}:SCA?'.format(ch))
        else:
            self.write('CH%d:SCA?'%ch)
        msg = self.read()
        return float(msg)

    def set_vpos(self, ch, div):
        self.write('CH%d:POS %.2f'%(ch, round(div,2)))

    #def set_wfm(self, ch, stat):
    #    """turn on/off CH1, REFA, ..."""
    #    self.write('SEL:{} {}'.format(ch, 'ON' if stat == True else 'OFF'))

    #def set_coupling(self, ch, coupling):
    #    """Set coupling of CH1, etc to DC, ..."""
    #    self.write('{}:COUP {}'.format(ch, coupling))

    def close(self):
        self.ser.close()
        print ('COM%d closed.'%(self.port+1))

if __name__ == '__main__':
    import sys
    if len(sys.argv)<3:
        print ('Usage 1: python serialinstruments.py')
        print ('Usage 2: python serialinstruments.py <filename (no ext)> <channel>')
        dev = TDS2000()
        print (dev.getwfmparam(1))
        dev.close()
        print ('Exiting...')
        sys.exit(0)

    fn = sys.argv[1]+'.dat'
    ch = int(sys.argv[2])
    dev = TDS2000()
    dev.setdatafmtascii()
    param = dev.getwfmparam(ch)
    print (param)
    wfm = dev.gettraceascii(ch)
    print (wfm[:40], '...')
    f = open(fn,'w')
    f.write(param)
    f.write(wfm)
    f.close()
    dev.close()
    print ('Read and saved waveform channel %d.'%ch)
