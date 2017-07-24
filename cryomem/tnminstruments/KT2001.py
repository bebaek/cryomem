from .base import Interface
from time import sleep

class KT2001(Interface):
    """Keithley 2001 multimeter"""
    def read_voltage(self):
        """Return voltage on the display"""
        self.write(':FETC?')
        msg = self.read()
        #print ('dmm msg = ', msg)
        v = msg.split(',')[0].rstrip('NVDC').strip()
        if v[-1] == 'R':
            return float(v[:-1])
        else:
            return float(v)

    def fetch(self):
        """Same as read_voltage. Keep for backward compatibility."""
        return read_voltage()

    def read_R4W(self):
        """Return 4-wire resistance on the display."""
        self.write(':FETC?')
        sleep(0.1)
        msg = self.read()
        #print ('read_R4W msg:', msg)
        v = msg.split(',')[0].rstrip('NOHM4W').strip()
        if v[-1] == 'R':
            return float(v[:-1])
        else:
            return float(v)
