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
            self.x, self.y = (data['T'], data["Vac_device"])
        else:
            print("No supported format:", filename)

    def _plot_data(self):
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)
        plothyst(self.x, self.y)

    def _fit(self):
        self.fitter = T_R_genlogistic(self.x, self.y)
        self.fit_results = self.fitter.fit()

    def _plot_fit(self):
        xf, yf = self.fitter.build_fitcurve()  # Plot fit curve
        plt.plot(xf, yf, "-")
        plt.show()
        #plt.pause(1)

    def _get_result(self):
        Tc, Rc, perr = self.fit_results
        return {"Tc": Tc, "Rc": Rc, "perr": perr}

    def run(self, **kwargs):
        """Load and fit from datafile.

        Keyword arguments:
            datafile -- string
        """
        self._load_data(kwargs["datafile"])
        self._plot_data()
        self._fit()
        self._plot_fit()
        try:
            return self._get_result()
        except NameError:
            return None

def test():
    import glob
    print(Tc().run(datafile=glob.glob("*.dat")[0]))

if __name__ == "__main__":
    test()
