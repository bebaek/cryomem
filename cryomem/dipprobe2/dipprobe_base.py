"""Define base methods for DipProbe class."""
import os, time
from glob import glob
from importlib import import_module
from pathlib import Path
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
#from ..common.plotthread import PlotThread
from ..common.plotproc import PlotProc
from .config import Config
from ..common.numstr import isnumstr
from ..common.datafile import save_data


class DeviceProp:
    """Device measurement property handler"""
    def __init__(self, **kwargs):
        self.param = kwargs

        # Raw property from instrument (to phase out)
        if "instrument" in self.param:
            instr_name = self.param["instrument"].upper()
            mod = import_module("cryomem.tnminstruments." + instr_name)
            self.instr = getattr(mod, instr_name)(self.param["interface"])

            # Assign access methods
            if "read_method" in self.param:
                self._read = getattr(self.instr, self.param["read_method"])
            if "write_method" in self.param:
                self.write = getattr(self.instr, self.param["write_method"])
            self.lastval = None

        # Derived property without instrument
        elif "read_module" in self.param:
            mod = import_module(self.param["read_module"])
            if "read_class" in self.param:
                class_name = self.param["read_class"]
                kwargs = self.param["read_class_keyword_arguments"]
                self.obj = getattr(mod, class_name)(**kwargs)
                self._read = getattr(self.obj, self.param["read_method"])
                #print("read_class found: ", self.param)
                #self._read = self.fakeread
                #print("trying read: ", self.read())
            else:
                self._read = getattr(mod, self.param["read_method"])
            self.lastval = None

        # Write property (device control parameter)
        elif "write_module" in self.param:
            mod = import_module(self.param["write_module"])
            if "write_class" in self.param:
                class_name = self.param["write_class"]
                kwargs = self.param.get("write_class_keyword_arguments", {})
                self.obj = getattr(mod, class_name)(**kwargs)
                self._write = getattr(self.obj, self.param.get("write_method", "write"))
            else:
                self._write = getattr(mod, self.param.get("write_method", "write"))

            # Set scaling parameters
            self._offset = 0
            self._scale = 1
            if "offsets" in self.param:
                for key in self.param["offsets"]:
                    self._offset += self.param["offsets"][key]
            if "multipliers" in self.param:
                for key in self.param["multipliers"]:
                    self._scale *= self.param["multipliers"][key]
            if "divisors" in self.param:
                for key in self.param["divisors"]:
                    self._scale /= self.param["divisors"][key]
            self.lastval = None

        # Initialize instrument if needed. E.g. oscilloscope setup.
        if 'init_method' in self.param:
            self._init = getattr(self.obj, self.param["init_method"])
            self._init(**self.param.get('init_method_keyword_arguments', {}))
            
    def fakeread(self, *args):
        print("fakeread called.")
        return 23

    def read(self, *args, **kwargs):
        """Return device read value and update lastval."""
        self.lastval = self._read(*args, **kwargs)
        return self.lastval

    def write(self, val, **kwargs2):
        """Write a (optionally scaled) value to device and update lastval."""
        kwargs = self.param.get("write_method_keyword_arguments", {})
        for key2 in kwargs2:
            kwargs[key2] = kwargs2[key2]

        if abs(val) <= self.param.get("max", np.inf):
            scaled_val = (val + self._offset)*self._scale
            self._write(scaled_val, **kwargs)
            self.lastval = val
            return self.lastval
        else:
            return None

class DipProbeBase:
    """Base measurement system class"""
    def __init__(self, **kwargs):
        #self.dev_param = {}
        #self.seq_param = {}
        #self.data = []
        self.data = {}		# dictionary-type data
        #self.devprops = []
        self.devprop = {}
        self.proplist = []
        self.dataroot = "data"
        self.dataext = "zip"
        self.config = Config()
        self.prog_config = Config()

    def help(self, *args):
        print("Not implemented yet.")

    def load_config(self, **kwargs):
        """Load program and user config files."""
        # Load program config file if exists
        #prog_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dipprobe.yaml")
        prog_config_file = os.path.join(str(Path.home()), ".dipprobe.yaml")
        try:
            self.prog_config.load_config(file=prog_config_file)
        except:
            print("No program config file found.")
            self.prog_config.load_config(parameters={})

        # Load user config file
        self.config.load_config(**kwargs)
        return 0

    def create_devprop(self, prop):
        """Create device property object (data)

        prop: device property name (string)"""
        self.devprop[prop] = DeviceProp(**self.config.content["device"][prop])
        self.proplist.append(prop)

    def get_dev_val(self, proplist):
        """Get device property value (DAQ)

        proplist: list of device property names (string) to read.
        """
        #val = []
        #val = pd.Series()		# old data type
        val = {}			# new dictionary-type data
        for prop in proplist:
            # first time to get the device prop
            if prop not in self.devprop:
                self.create_devprop(prop)

            # get value
            kwargs = self.config.content['device'][prop].get(
                'read_method_keyword_arguments', {})
            if "input_variable" in self.config.content["device"][prop]:
                arg = self.devprop[self.config.content["device"][prop]["input_variable"]].lastval
                #val.append(self.devprop[prop].read(arg))
                val[prop] = self.devprop[prop].read(arg, **kwargs)
            else:
                #val.append(self.devprop[prop].read())
                val[prop] = self.devprop[prop].read(**kwargs)
        return val

    def set_dev_val(self, prop, val):
        """Set device property value and return actually written value.

        Arguments:
            prop: string
            val: float
        """
        # first time to get the device prop
        if prop not in self.devprop:
            self.create_devprop(prop)

        # Set value
        val_actual = self.devprop[prop].write(val)
        return val_actual

    def ramp_dev_val(self, prop, val1, val2, step=1e-9, delay=0):
        """Ramp device property value and return actually written last value.

        Arguments:
            prop: string
            val1, val2, step=0, delay=0: float
        """
        # first time to get the device prop
        if prop not in self.devprop:
            self.create_devprop(prop)

        # Set value
        step = np.sign(val2 - val1)*abs(step)
        for val in np.arange(val1, val2, step):
            val_actual = self.set_dev_val(prop, val)
            time.sleep(delay)
        val_actual = self.set_dev_val(prop, val2)
        return val_actual

    def append_data(self, data, **kwargs):
        """Accumulate data in memory (dict of array) for plotting/saving.

	data: dict.
	"""
        # add to data arrays
        #self.data = self.data.append(data, ignore_index=True)
        for key in data:
            data2add = data[key]
            if type(data2add) is not np.array:
                data2add = np.array(data2add)
            if key not in self.data:
                self.data[key] = data2add      # first data
            else:
                self.data[key] = np.vstack((self.data[key], data2add))

        # write to temp file
        #if kwargs.get("tmpfile", False):
        #    msg = ""
        #    for datum in data:
        #        msg += "{}\t".format(datum)
        #    msg += "\n"
        #    try:
        #        self.tmpdatafile.write(msg)
        #        self.tmpdatafile.flush()
        #    except:
        #        self.tmpdatafile = open("tmpdata.txt", "w")
        #        self.tmpdatafile.write(msg)
        #        self.tmpdatafile.flush()

        # display data
        if kwargs.get("show", False):
            print("Data:", str(data)[:70])

    def plot_data(self, xprop, yprop):
        """Real time plot."""
        x, y = self.data[xprop], self.data[yprop]
        if self.data.shape[0] == 1:
            # first data point
            plotparams = {"xlabel": xprop, "ylabel": yprop, "title": "Plot - Dip Probe"}
            if "wx" in self.prog_config.content and "wy" in self.prog_config.content:
                plotparams["wx"] = self.prog_config.content["wx"]
                plotparams["wy"] = self.prog_config.content["wy"]
            self.plotter = PlotProc(**plotparams)

        self.plotter.plot(x, y)

    def close_plot(self):
        """Clean up plot."""
        # Get plotting window location and save
        wloc = self.plotter.get_wloc()
        wx, wy = wloc
        self.prog_config.content["wx"] = wx
        self.prog_config.content["wy"] = wy
        self.prog_config.save_config()

        self.plotter.close()

    def plot_data_old(self, xprop, yprop):
        #tmp = list(zip(*self.data))
        x, y = self.data[xprop], self.data[yprop]
        if self.data.shape[0] == 1:
            # first data point
            self.plotstyle = "o-"
            #self.ix = self.proplist.index(xprop)
            #self.iy = self.proplist.index(yprop)
            #x, y = tmp[self.ix], tmp[self.iy]

            fig = plt.figure()
            self.ax = fig.add_subplot(111)
            self.pl = self.ax.plot(x, y, self.plotstyle)
        else:
            # add a new data point
            #x, y = tmp[self.ix], tmp[self.iy]
            #self.pl[0].set_xdata(x)
            #self.pl[0].set_ydata(y)
            #self.ax.autoscale_view()
            #x, y = tmp[self.ix], tmp[self.iy]
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
            fnlist = list(Path(self.dataroot).glob('*.zip'))
            if len(fnlist) == 0:
                n = 1
                print ('1st datafile.')
            else:
                #n = max([int(fn.split('\\')[-1].split('_')[0]) for fn in fnlist])+1
                tmp = [os.path.basename(fn).split('_')[0] for fn in fnlist]
                tmp2 = []
                for s in tmp:
                    if isnumstr(s):
                        tmp2.append(int(s))
                n = max(tmp2) + 1

            filename = "{:03n}_{}.{}".format(n, dataname, self.dataext)
            datapath = "{}/{}".format(self.dataroot, filename)

        # do not prefix the datafile name
        else:
            datapath = "{}/{}.{}".format(self.dataroot, dataname, self.dataext)
        # save data and metadata to zip
        print("Saving data to: {}...".format(datapath))
        save_data(datapath, self.data, md=self.config.content)

        ## make header from config
        #header = self.config.dump_config(ascomments=True)

        ## save
        #data = self.data.to_string(float_format='%.11g')
        #with open(datapath, 'w') as f:
        #    f.write(header + '\n' + data + '\n')
