import numpy as np
from importlib import import_module
import tnminstruments
from .num_with_unit import isnumstr, numstr2num, convert_num_with_unit
import ruamel_yaml as yaml
import copy

class DeviceProp:
    """Class for a device measurement property"""
    def __init__(self, **kwargs):
        self.param = kwargs

        # Raw property from instrument
        if "instrument" in self.param:
            instr_name = self.param["instrument"].upper()
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
        #self.dev_param = {}
        #self.seq_param = {}
        self.data = [] 
        self.devprops = []

    def help(self, *args):
        print("Not implemented yet.")

    def load_config(self, **kwargs):
        # Sources of config parameters: argument or file
        if "parameters" in kwargs:
            self.config = kwargs["parameters"]
        elif "file" in kwargs:
            with open(kwargs["file", "r"]) as f:
                self.config = yaml.load(f)

    def save_config(self, configfile):
        with open(configfile, "w") as f:
            yaml.dump(self.config, f)

    def parse_config(self, config, **kwargs):
        """Return a copy of config with some strings converted"""
        exception = kwargs["exception"]
        result = copy.deepcopy(config)

        # Recursively reduce down to string element
        if type(result) is list:
            for k, config2 in enumerate(result):
                result[k] = self.parse_config(config2, **kwargs)
        elif type(result) is dict:
            for key in result:
                result[key] = self.parse_config(result[key], **kwargs)
        elif isnumstr(result):
            # Try to convert a number string to int or float
            result = numstr2num(result)
        else:
            # Try to convert a number with a unit to a scaled int or float
            result = convert_num_with_unit(result)
        return result

    def create_devprop(self, prop):
        """Create device property object (data)

        prop: device property name (string)"""
        propobj = DeviceProp(**self.config["device"][prop])
        setattr(self, prop, propobj)
        self.devprops.append(prop)

    def get_dev_val(self, proplist):
        """Get device property value (DAQ)

        proplist: list of device property names (string) to read"""
        val = []
        for prop in proplist:
            if prop not in self.devprops:   # first time to use device prop
                self.create_devprop(prop)
            val.append(getattr(self, prop).read())  # get value
        return val

    def set_dev_val(self, **kwargs):
        pass

    def append_data(self, data, **kwargs):
        self.data.append(data)
        if kwargs.get("show", False):
            print("Data:", data)

    def save_data(self, **kwargs):
        filename = kwargs.get("filename", "testdata.txt")
        data = self.data
        print("Data to save:", data)
        print("Saving data to: {}...".format(filename))
        np.savetxt(filename, data, fmt="%.4e")

