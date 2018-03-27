"""Load and fit Tc from datafile."""
import numpy as np
import sys
from .Tc_logistic import T_R_genlogistic
import matplotlib.pyplot as plt
import pandas as pd
from ..common.plothyst import plothyst

class Tc_datafile:
    """Load and fit Tc from datafile."""
    def _get_format(self, filename):
        # Single format for now
        return "0.1_dipprobe_T_V"

    def _load_data(self, filename):
        fileformat = self._get_format(filename)
        if fileformat == "0.1_dipprobe_T_V":
            data = pd.read_table(filename, sep='\s+', comment="#")
            if "Vac_device" in data:
                self.x, self.y = (data['T'], data["Vac_device"])
            else:
                self.x, self.y = (data['T'], data["Rac_device"])
        else:
            print("No supported format:", filename)

    def _open_figure(self):
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)

    def _plot_data(self):
        #plothyst(self.x, self.y)
        plt.plot(self.x, self.y, "o")

    def _fit(self):
        self.fitter = T_R_genlogistic(self.x, self.y)
        self.fit_results = self.fitter.fit()

    def _plot_fit(self):
        xf, yf = self.fitter.build_fitcurve()  # Plot fit curve
        plt.plot(xf, yf, "-")

    def _get_result(self):
        Tc, Rc, perr = self.fit_results
        return {"Tc": Tc, "Rc": Rc, "perr": perr}

    def run(self, **kwargs):
        """Load and fit from datafile.

        Keyword arguments:
            datafile -- string or array-like of string
        """
        datafiles = kwargs["datafile"]
        if type(datafiles) == str:
            datafiles = [datafiles]

        # Fit multiple datafiles
        self._open_figure()
        results = []
        for datafile in datafiles:
            self._load_data(datafile)
            self._plot_data()
            self._fit()
            self._plot_fit()
            results = results + [self._get_result()]

        # Wait for user to close figure
        plt.show()
        try:
            return results
        except NameError:
            return None

def test():
    import glob
    print(Tc().run(datafile=glob.glob("*.dat")[0]))

if __name__ == "__main__":
    test()
