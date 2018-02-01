from .base import Interface

class SR830(Interface):
    """SRS lock-in"""
    def __init__(self, interface="gpib0"):
        super().__init__(interface)
        self.vsens = [2e-9, 5e-9, 10e-9, 2e-8, 5e-8, 10e-8, 2e-7, 5e-7, 10e-7,\
            2e-6, 5e-6, 10e-6, 2e-5, 5e-5, 10e-5, 2e-4, 5e-4, 10e-4,\
            2e-3, 5e-3, 10e-3, 2e-2, 5e-2, 10e-2, 2e-1, 5e-1, 10e-1]

    def get_x(self):
        self.write('OUTP? 1')
        return float(self.read())

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

    # conform with yaml configs
    def set_auxvout(self, voltage, channel=-1):
        v_actual = "%7.3f"%(voltage)
        msg = 'AUXV %d,%s'%(channel, v_actual)
        self.write(msg)
        print(msg)
        return v_actual

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
