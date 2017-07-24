"""
Base classes for GPIB interface. Only used by other modules
"""

import ctypes
from time import sleep

# Load DLL
#gpibdll = windll.LoadLibrary('gpib-32') # old way
gpibdll = ctypes.windll.LoadLibrary('ni4882')

class GPIB:
    """GPIB inteface class"""
    def __init__(self, unit, addr):
        timeout = 10
        self.unit = unit
        self.addr = addr
        self.ud = gpibdll.ibdev(ctypes.c_int(self.unit),ctypes.c_int(self.addr),\
          ctypes.c_int(0),ctypes.c_int(timeout),ctypes.c_int(1),ctypes.c_int(0))
        #print(self.ud)
        #print('ibdev=',getattr(gpibdll, 'ibdev'))
        gpibdll.ibclr(self.ud)
        self.write('*IDN?')
        msg = self.read()
        print("GPIB unit {}, address {}".format(self.unit, self.addr))
        print(msg, flush=True)

    def write(self, cmd):
        msg = gpibdll.ibwrt(self.ud, (cmd+'\n').encode('utf-8'), len(cmd))
        #print("GPIB write; address: {}, msg: {}".format(self.addr, cmd))
        sleep(0.2)
        return msg

    def read(self, bufsize=256):
        buf = ctypes.create_string_buffer(bufsize)
        msg = gpibdll.ibrd(self.ud, buf, bufsize)
        #return repr(buf.value)
        #print("GPIB read; address: {}, msg: {}".format(self.addr, msg))
        return buf.value.decode('utf-8')

    def close(self):
        # return control
        gpibdll.ibonl(self.ud, 0)
        print ('GPIB #%d offline.'%self.addr, flush=True)
