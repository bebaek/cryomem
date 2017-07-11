import numpy as np
from importlib import import_module
import tnminstruments

class DeviceProp:
    """Class for a device measurement property"""
    def __init__(self, **kwargs):
        self.param = kwargs

        # Raw property from instrument
        if "instrument" in self.param:
            instr_name = self.param["instrument"].uppercase()
            mod = import_module("tnminstruments." + instr_name)
            self.instr = getattr(mod, instr_name)(self.param["interface"])

            # Assign access methods
            if "read_method" in self.param:
                self.read = getattr(self.instr, self.param["read_method"])
            if "write_method" in self.param:
                self.write = getattr(self.instr, self.param["write_method"])

        # Derived property without instrument
        else:
            mod = import_module(self.param["read_module"])
            self.read = getattr(mod, self.param["read_method"])

        # Last obtained value
        self.val = None

class DipProbeBase:
    """Base measurement system class"""
    def __init__(self):
        self.dev.param = {}
        self.seq_param = {}
        self.data = np.array([])
        self.devprops = []

    def help(self, *args):
        print("Not implemented yet.")

    def load_config(self, **kwargs):
        if "parameters" in kwargs:
            self.config = kwargs["parameters"]
        elif "file" in kwargs:
            pass

    def save_config(self, configfile):
        pass

    def init_devprop(self, prop):
        """Create data property object"""


    def get_dev_val(self, proplist):
        """Get device property value (DAQ)"""
        val = []
        for prop in proplist:
            if prop not in self.devprops:   # first time to use device prop
                self.init_devprop(prop)
            val.append(getattr(self, prop).read())  # get value
        return np.array(val)

    def set_dev_val(self, **kwargs):
        pass

    def append_data(self):
        pass

    def save_data(self, **kwargs):
        pass
