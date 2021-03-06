"""Fit and estimate wedge film rate distribution. Spatial units are micrometer."""
import sys
import cryomem.common.numstr as ns
import cryomem.common.defaults as defaults
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from io import StringIO
import ruamel_yaml as yaml
import os.path
import matplotlib.pyplot as plt

def _f(coord, a0, a1, a2, a3, a4, a5, a6, a7, a8):
    """Evaluate 2-d function by: a0*x**2*y**2 + a1*x**2*y + ... + a8

    Parameters:
    coord: (x,y): (float, float)
    a0,...,a8: float
    """
    x, y = coord
    res = a0*x**2*y**2 + a1*x**2*y + a2*x**2 \
            + a3*x*y**2 + a4*x*y + a5*x \
            + a6*y**2 + a7*y + a8
    return res

def _f2(coord, *a):
    """Evaluate 2-d function by: a[0]*x**n*y**n + a[1]*x**n*y**(n-1) + ...

    Parameters:
    coord: (x,y): (float, float)
    a[0], a[1], ..., a[k]: float. Polynomial coefficients. k should be the
    square of (order+1) (such as 9 for order 2).
    """
    x, y    = coord
    n       = int(np.sqrt(len(a)) - 1)     # polynomial order
    #print("_f2 is in use.")
    res = np.sum([a[(n + 1)*k + l]*x**(n - k)*y**(n - l)
                   for k in range(n + 1) for l in range(n + 1)], axis=0)
    return res

def _to_table(xys, vals):
    """Make a DataFrame from xy as columns and indices"""
    x = [xy[0] for xy in xys]
    y = [xy[1] for xy in xys]
    df = pd.DataFrame(index=("6","5","4","3","2","1"),
                      columns=("1","2","3","4","5","6"))
    for k, val in enumerate(vals):
        df.loc[y[k], x[k]] = val

    return df

def _get_globxy(col, row, xlocal, ylocal):
    """Return wafer-level coordinate."""
    return (col*10000 - 35000 + xlocal, row*10000 - 35000 + ylocal)

def _rotate(x, y, phi):
    """Return rotated x, y by angle phi (degree)"""
    x2 = x*np.cos(phi*np.pi/180) - y*np.sin(phi*np.pi/180)
    y2 = x*np.sin(phi*np.pi/180) + y*np.cos(phi*np.pi/180)
    return x2, y2

def _offset(x, y, xoffset=0, yoffset=0):
    """Return x + xoffset, y + yoffset."""
    return x + xoffset, y + yoffset

class Wedge:
    """Object to handle a wedge film thickness distribution"""
    def _read_rawcal(self, srcfile, wafer):
        """Search and return a list of [die, measured step] from a file."""
        with open(srcfile, "r") as f:
            print("Source file:", srcfile)

            # search a line for matching wafer wedge calibration
            found = False
            for line in f:
                if wafer in line:
                    line_lc = line.lower()
                    if "wedge" in line_lc:
                        kw = "wedge"
                        found = True
                    elif "rate" in line_lc:
                        kw = "rate"
                        found = True

                    if found:
                        print("Found wafer:", line)
                        words = line.split()
                        material = words[words.index(kw) - 1]
                        break
            if not found:
                print("Not found:", wafer)
                return -1

            # search for local coordinates
            while True:
                line = f.readline()
                if ("x,y" in line) or ("x, y" in line):
                    self.xloc, self.yloc = map(float,line.split(":")[-1].split(","))
                    print("Found coordinates:", self.xloc, self.yloc)
                    break

            # search for start of step height lines
            line = f.readline()
            words = line.split()
            while (not ns.isnumstr(words[-1])) and (not ns.isnumstr(words[-4])):
                line = f.readline()
                words = line.split()

            # read step heights
            dies, steps = [], []
            while len(words) > 4:
                left, right = line.split(":")

                # get die IDs
                die_start, die_end = left.split()[-1].split("-")
                row = die_start[1]
                col1, col2 = int(die_start[0]), int(die_end[0])
                if col2 > col1:
                    dies += [str(n) + row for n in range(col1, col2+1, 1)]
                else:
                    dies += [str(n) + row for n in range(col1, col2-1, -1)]

                # get steps
                steps += [float(s) for s in right.split()]

                line = f.readline()
                words = line.split()

        self.rawdata = _to_table(dies, steps)
        print("Found thicknesses:\n", self.rawdata)
        self.cal_meta = {"material": material}
        self.cal_data = pd.DataFrame({"dies": dies, "thicknesses": steps})

    def _rawcal_to_rates(self, deduction, duration, method, **kwargs):
        if method == "normal":
            # typical situation: uniform deduction (seed/cap layer)
            self.cal_data["rates"] = (self.cal_data["thicknesses"] - deduction)/duration
        elif method == "deductwedge2":
            for key2 in kwargs:
                if key2[-1] == "2":     # remove dangling "2" from key
                    key = key2[:-1]
                    kwargs[key] = kwargs[key2]
                    del kwargs[key2]

            for idx in self.cal_data.index:
                deduction = self.get_rate(self.cal_data.loc[idx,"x"],
                                          self.cal_data.loc[idx,"y"], **kwargs)
                self.cal_data["rates"] = (self.cal_data["thicknesses"] - deduction)/duration
        print(self.cal_data.head())

    def _dies_to_coords(self):
        """Make tables of global coordinates for each die"""
        self.cal_data["x"] = pd.Series()
        self.cal_data["y"] = pd.Series()
        for k,die in enumerate(self.cal_data["dies"]):
            self.cal_data.loc[k,"x"] = (int(die[0]) - 3.5)*10000 + self.xloc
            self.cal_data.loc[k,"y"] = (int(die[1]) - 3.5)*10000 + self.yloc
        #print(self.cal_data.head())

    def _fit_rates(self):
        p0 = [0,0,0,0,0,0,0,0,0]
        xx = [self.cal_data["x"], self.cal_data["y"]]
        yy = self.cal_data["rates"]
        self.popt, self.pcov = curve_fit(_f, xx, yy, p0)
        print(self.popt)

    def _fit_rates2(self, fitorder):
        p0 = [0 for k in range((fitorder + 1)**2)]
        xx = [self.cal_data["x"], self.cal_data["y"]]
        yy = self.cal_data["rates"]
        self.popt, self.pcov = curve_fit(_f2, xx, yy, p0)
        print(self.popt)

    def save_cal(self, calfile):
        """Save raw and fit wedge data to a file"""
        output = StringIO()

        output.write("#### Raw calibration data ####\n")
        self.rawdata.to_csv(output, sep="\t")

        output.write("\n#### Fit parameters ####")
        np.savetxt(calfile, self.popt, fmt="%.11g", delimiter="\t",
                   header=output.getvalue())

    def _name_calfile(self, wafer):
        material = self.cal_meta['material']
        return '{}/wedge_{}_{}.dat'.format(defaults.dbroot, material, wafer)

    def fit(self, **kwargs):
        """Return fit parameters for the 2-D rate profile.

        Keyword arguments:
            srcfile, wafer, duration, [deduction, fitorder, save]
        """
        srcfile     = kwargs["srcfile"]
        wafer       = kwargs["wafer"]
        duration    = kwargs["duration"]
        deduction   = kwargs.get("deduction", 0)
        fitorder    = kwargs.get("fitorder", 2)
        wantsave    = kwargs.get("save", False)
        method      = kwargs.get("method", "normal")

        # kwargs for unusual situation; deduct extra wedge layer
        kwargs2 = {}
        for key in kwargs:
            if key[-1] == "2":          # grab parameters of the form "xxx2"
                kwargs2[key] = kwargs[key]

        status = self._read_rawcal(srcfile, wafer)
        if status == -1:
            print("_rawcal_to_rates() failed.")
            sys.exit(-1)
        self._dies_to_coords()
        self._rawcal_to_rates(deduction, duration, method, **kwargs2)
        #self._fit_rates()
        self._fit_rates2(fitorder)
        if wantsave:
            calfile = kwargs.get("calfile", self._name_calfile(wafer))
            self.save_cal(calfile)
        return 0

    def _get_rate(self, x=0, y=0, **kwargs):
        """Get the rate at the absolute coordinate. Called by another
        method."""
        return _f2((x,y), *self.popt)

    def get_rate(self, x=0, y=0, **kwargs):
        """Get the rate at the absolute coordinate. Called by user.

        Arguments:
            x, y
        Keyword argument:
            calfile, angle, duration
        """
        if "popt" not in dir(self):
            self.popt = np.loadtxt(self._search_dbfile(kwargs["calfile"]))
        x, y = _rotate(x, y, kwargs.get('angle', 0))
        x, y = _offset(x, y, xoffset=kwargs.get("xoffset", 0),
                       yoffset=kwargs.get("yoffset", 0))

        #thickness = _f2((x,y), *self.popt)*kwargs.get('duration', 1)
        thickness = self._get_rate(x, y)*kwargs.get('duration', 1)
        return thickness

    def plot(self, **kwargs):
        """Plot rate distribution.

        Keyword arguments:
            calfile, ncontour
        """
        if "popt" not in dir(self):
            self.popt = np.loadtxt(self._search_dbfile(kwargs["calfile"]))
        n = 100
        x = np.linspace(-30000, 30000, n)
        y = np.linspace(-30000, 30000, n)
        rate = np.empty([n, n])
        for k, yy in enumerate(y):
            rate[k] = np.array(self.get_rate(x, yy))
        #plt.pcolor(x, y, rate)
        plt.contourf(x, y, rate, kwargs.get("ncontour", 10))
        plt.xlabel("x (um)")
        plt.ylabel("y (um)")
        plt.colorbar()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        return 0

    def _load_chip_design(self, filename):
        with open(filename, "r") as f:
            #self.chip_design = yaml.load(f)
            self.chip_design = yaml.safe_load(f)

    def _get_device_coord(self, reticle, device):
        x = self.chip_design[reticle]["device"][device]["x"]
        y = self.chip_design[reticle]["device"][device]["y"]
        return float(x), float(y)

    def _search_dbfile(self, filename):
        """Return valid path where the db file exists."""
        if os.path.exists(filename):
            return filename
        else:
            altpath = "{}/{}".format(defaults.dbroot, filename)
            if os.path.exists(altpath):
                return altpath
            else:
                print("No path found: ", filename)
                return None

    def get_thickness(self, **kwargs):
        """Return thickness based on high-level design details.

        Keyword arguments:
            calfile -- Wedge calibration file
            duration -- Scaling factor to convert rate to thickness
            reticle -- Reticle ID such as "SF1"
            chip -- Chip ID such as "33"
            device -- Device name on the chip such as "A01"

        Optional keyword arguments:
            chip_design_file -- Default: <package dir>/data/chip_design.yaml
            angle -- Angle in degree to rotate the coordinate. Default: 0
            xoffset, yoffset -- x, y offsets in micrometer from regular 6x6
            design.
        """
        calfile = kwargs["calfile"]
        duration = kwargs.get("duration", 1)
        reticle = kwargs["reticle"].upper()
        chip = str(kwargs["chip"])
        device = kwargs["device"]
        chip_design_file = kwargs.get("chip_design_file",
                                      "{}/chip_design.yaml".format(defaults.dbroot))
        angle = kwargs.get("angle", 0)
        xoffset = kwargs.get("xoffset", 0)
        yoffset = kwargs.get("yoffset", 0)

        # Load fit parameters
        self.popt = np.loadtxt(self._search_dbfile(calfile))

        # Load device info and calculate global device coordinate
        self._load_chip_design(chip_design_file)
        xlocal, ylocal = self._get_device_coord(reticle, device)
        x, y = _get_globxy(int(chip[0]), int(chip[1]), xlocal, ylocal)
        x, y = _rotate(x, y, angle)
        x, y = _offset(x, y, xoffset=xoffset, yoffset=yoffset)

        thickness = self._get_rate(x, y, angle=angle)*duration
        return thickness

#def main(argv):
#    """Entrypoint"""
#    # process arguments
#    if len(argv) < 2:
#        print("Commands: {}\n".format(_cmdlist))
#        sys.exit(0)
#
#    cmd = argv[1]
#    parsed_args = parse_cmd_argv(argv[2:])
#    if cmd not in _cmdlist:
#        print("Commands: {}\n".format(_cmdlist))
#        sys.exit(0)
#
#    # Call the corresponding function (command)
#    #globals()[cmd](*args, **kwargs)
#    w = Wedge()
#    try:
#        if type(parsed_args) is tuple:
#            print(getattr(w, cmd)(*parsed_args[0], **parsed_args[1]))
#        else:
#            print(getattr(w, cmd)(**parsed_args))
#    except KeyError:
#        print("Keyerror!")
#        print(getattr(w, cmd).__doc__)
