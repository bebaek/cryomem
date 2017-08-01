import visa

rm = visa.ResourceManager()
rm.list_resources()

class GPIB:
    """GPIB inteface class"""
    def __init__(self, unit, addr):
        self.unit = unit
        self.addr = addr
        self.inst = rm.open_resource('GPIB{}::{}::INSTR'.format(unit, addr))
        print(self.query("*IDN?"))

    def write(self, cmd):
        return self.inst.write(cmd)

    def read(self):
        return self.inst.read()

    def query(self, cmd):
        return self.inst.query(cmd)
