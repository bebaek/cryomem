"""
zipdata handler classes. Unused but kept in case OOP becomes preferable.
"""
from . import datafile
from scipy.optimize import curve_fit

class ZipData():
    """Base class for dict-like data and dict-like metadata.

    data/md are saved as text files in a zip file.

    data and md can be dict, OrderedDict, or CommentedMap (YAML)

    fitp is OrderedDict.
    """
    def __init__(self, **kwargs):
        """
        Keyword arguments: 
            datafile: string. zipfile name.
            data: dict-like.
            md: dict-like.
            guessf: function. Quick guess function
            fitf: function. Fit function
        """
        self.datafile   = kwargs.get("datafile", None)
        If datafile != None:
            self.load_data(filename)
        self.data       = kwargs.get("data", None)
        self.md         = kwargs.get("md", None)
        self.guessf     = kwargs.get("guessf", None)
        self.fitf       = kwargs.get("fitf", None)

    def load_data(self, filename):
        """Argument: filename"""
        self.data, self.md = datafile.load_data(filename)

    def save_data(self, filename):
        """Argument: filename"""
        try:
            return datafile.save_data(self.dfname, self.data, md=self.md)
        except:
            return datafile.save_data(self.dfname, self.data)

    def list_data(self):
        """Return a list of names (labels) of data"""
        return [key for key in self.data]

    def get_data(self, name):
        """Argument: name (label) of data"""
        return self.data[name]

    def set_data(self, name, data):
        """Argument: name (str), data (array-like)"""
        self.data[name] = data

    def list_md(self):
        """Return a list of names (labels) of metadata"""
        return [key for key in self.md]

    def get_md(self, name):
        """Argument: name (label) of md"""
        return self.md[name]

    def set_md(self, name, md):
        """Argument: name (str), md (array-like)"""
        self.md[name] = md

    # 2 methods for fit method below
    def _fitp2list(self):
        return [self.fitp(key) for key in self.fitp]

    def _list2fitp(self, l):
        for k, key in enumerate(self.fitp):
            self.fitp[key] = l[k]

    # Override this in derived class as needed
    def fit(self, xname, yname, **kwargs):
        """Fit simple y(x) data. Results are accessible by get_fitp()
        
        Arguments: xname, yname
        Keyword arguments:
            indices: sequence. For partial data fitting
            quickguess: bool. Run quickguess instead of main fit.
        """
        # partial data?
        try:
            ind  = range(kwargs["istart"], kwargs["iend"])
            x, y = data[xname][ind], data[yname][ind]
        except:
            x, y = data[xname], data[yname]
        self.fitxmin, self.fitxmax = np.amin(x), np.amax(x) # remember fit range

        # quickguess or main fit?
        if kwargs.get("quickguess", False):
            self.fitp       = self.quickguessf(x, y)
        else:
            popt, self.pcov = curve_fit(f, x, y, *self._fitp2list())
            self.fitp       = self._list2fitp(popt)

    def get_fitf(self):
        """Return fit function"""
        return self.fitf

    def set_fitf(self, fitf):
        """Set fit function. Argument: fitf (function)"""
        self.fitf = fitf

    def get_fitp(self):
        """Return fit parameters (dict)"""
        return self.fitp

    def set_fitp(self, **fitp):
        """Set fit/guess parameters. Arguments: **popt"""
        return self.fitp

    def eval_fitf(self, x):
        """Argument: x (array-like)"""
        return self.fitf(x)

    def set_guessf(self, guessf):
        """Argument: guess function"""
        self.guessf(guessf)

class BIarrVarrData(Zipdata):
    """B-I-V array data handler"""
    def fit(self):
        """Fit and return resulting BIcData"""

