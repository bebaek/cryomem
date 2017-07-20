import numpy as np
import matplotlib.pyplot as plt
from importlib import import_module
import tnminstruments
from .num_with_unit import isnumstr, numstr2num, convert_num_with_unit
import ruamel_yaml as yaml
import copy, os
from glob import glob

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
                self._read = getattr(self.instr, self.param["read_method"])
            if "write_method" in self.param:
                self.write = getattr(self.instr, self.param["write_method"])

        # Derived property without instrument
        else:
            mod = import_module(self.param["read_module"])
            if "read_class" in self.param:
                class_name = self.param["read_class"]
                kwargs = self.param["read_class_keyword_argument"]
                self.obj = getattr(mod, class_name)(**kwargs)
                self._read = getattr(self.obj, self.param["read_method"])
                #print("read_class found: ", self.param)
                #self._read = self.fakeread
                #print("trying read: ", self.read())
            else:
                self._read = getattr(mod, self.param["read_method"])

        # Last obtained value
        self.lastread = None

    def fakeread(self, *args):
        print("fakeread called.")
        return 23

    def read(self, *args):
        """Returns assigned read result and also stores the value"""
        self.lastread = self._read(*args)
        return self.lastread

class DipProbeBase:
    """Base measurement system class"""
    def __init__(self):
        #self.dev_param = {}
        #self.seq_param = {}
        self.data = []
        #self.devprops = []
        self.devprop = {}
        self.proplist = []
        self.dataroot = "data"
        self.dataext = "dat"

    def help(self, *args):
        print("Not implemented yet.")

    def load_config(self, **kwargs):
        # Sources of config parameters: argument or file
        if "parameters" in kwargs:
            self.rawconfig = kwargs["parameters"]
        elif "file" in kwargs:
            with open(kwargs["file"], "r") as f:
                self.rawconfig = yaml.load(f)
            self.config = self.parse_config(self.rawconfig)

    def save_config(self, configfile):
        with open(configfile, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def parse_config(self, config, **kwargs):
        """Return a copy of config with some strings converted"""
        result = copy.deepcopy(config)

        # Recursively reduce down to basic element
        if type(result) is list:
            for k, config2 in enumerate(result):
                result[k] = self.parse_config(config2, **kwargs)
        elif type(result) is dict:
            for key in result:
                result[key] = self.parse_config(result[key], **kwargs)
        #elif isnumstr(result):
        #    # Try to convert a number string to int or float
        #    result = numstr2num(result)
        elif type(result) is str:
            # Try to convert a number with a unit to a scaled int or float
            result = convert_num_with_unit(result)

        return result

    def create_devprop(self, prop):
        """Create device property object (data)

        prop: device property name (string)"""
        self.devprop[prop] = DeviceProp(**self.rawconfig["device"][prop])
        self.proplist.append(prop)

    def get_dev_val(self, proplist):
        """Get device property value (DAQ)

        proplist: list of device property names (string) to read"""
        val = []
        for prop in proplist:
            # first time to get the device prop
            if prop not in self.devprop:
                self.create_devprop(prop)

            # get value
            if "input_variable" in self.rawconfig["device"][prop]:
                arg = self.devprop[self.rawconfig["device"][prop]["input_variable"]].lastread
                val.append(self.devprop[prop].read(arg))
            else:
                val.append(self.devprop[prop].read())
                #val.append(getattr(self, prop).read())  # get value
        return val

    def set_dev_val(self, **kwargs):
        pass

    def append_data(self, data, **kwargs):
        self.data.append(data)

        # write to temp file
        if kwargs.get("tmpfile", False):
            msg = ""
            for datum in data:
                msg += "{}\t".format(datum)
            msg += "\n"
            try:
                self.tmpdatafile.write(msg)
                self.tmpdatafile.flush()
            except:
                self.tmpdatafile = open("tmpdata.txt", "w")
                self.tmpdatafile.write(msg)
                self.tmpdatafile.flush()

        # display data
        if kwargs.get("show", False):
            print("Data:", data)

    def plot_data(self, xprop, yprop):
        tmp = list(zip(*self.data))
        if len(self.data) == 1:
            # first data point
            self.plotstyle = "o-"
            self.ix = self.proplist.index(xprop)
            self.iy = self.proplist.index(yprop)
            x, y = tmp[self.ix], tmp[self.iy]
            fig = plt.figure()
            self.ax = fig.add_subplot(111)
            self.pl = self.ax.plot(x, y, self.plotstyle)
        else:
            # add a new data point
            #x, y = tmp[self.ix], tmp[self.iy]
            #self.pl[0].set_xdata(x)
            #self.pl[0].set_ydata(y)
            #self.ax.autoscale_view()
            x, y = tmp[self.ix], tmp[self.iy]
            self.ax.cla()
            self.pl = self.ax.plot(x, y, self.plotstyle)

        plt.pause(0.05)

    def save_data(self, **kwargs):
        dataname =  kwargs.get("filename", "testdata.txt")
        increment = kwargs.get("datafile_increment", False)

        # create data directory if it doesn't exist.
        if not os.path.isdir(self.dataroot):
            os.makedirs(self.dataroot)

        # look for the last number of datafiles and increase it.
        if increment:
            fnlist = glob(self.dataroot+'\\*.dat')
            if len(fnlist)==0:
                n=1
                print ('1st data!')
            else:
                n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1

            filename = "{:03n}_{}.{}".format(n, dataname, self.dataext)
            datapath = "{}/{}".format(self.dataroot, filename)

        # do not prefix the datafile name
        else:
            datapath = "{}/{}.{}".format(self.dataroot, dataname, self.dataext)

        data = self.data
        print("Saving data to: {}...".format(datapath))
        np.savetxt(datapath, data)
