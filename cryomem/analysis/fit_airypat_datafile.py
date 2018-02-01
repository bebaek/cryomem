"""Load and fit from datafile."""
import numpy as np
import sys
from .fraunhoferpat import AiryPat
from ..common.datafile_cmtools import CMData_IcArr, CMData_H_I_Ic_Rn
import matplotlib.pyplot as plt
#import pandas as pd
from ..common.plothyst import plothyst

class FitAiryPat:
    """Load and fit from datafile to Airy pattern."""
    def _get_format(self, filename):
        # Single format for now
        return "cmdata_icarr"

    def _load_data(self, filename):
        fileformat = self._get_format(filename)
        if fileformat == "cmdata_icarr":
            try:
                data = CMData_IcArr(filename)       # dual Ic
                self.x, self.y = data.happ, data.ic_pos
            except:
                data = CMData_H_I_Ic_Rn(filename)   # single Ic
                self.x, self.y = data.happ, data.ic

    def _plot_data(self):
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)
        plothyst(self.x, self.y)
        #plt.show()
        plt.pause(1)

    def _query_param(self):
        """Get user input."""
        done = input("End fit? (y/[n]) ")
        if done.lower() == "y":
            return True
        self.i1 = int(input("Start data index? "))
        self.i2 = int(input("End data index? "))
        self.Ic_guess = float(input("Ic guess? "))
        self.H0_guess = float(input("H0 guess? "))
        self.dH1_guess = float(input("|Hnode1 - H0| guess? "))
        return False

    def _fit(self):
        p1 = 3.81/np.pi/self.dH1_guess
        guess = [self.Ic_guess, p1, self.H0_guess]
        self.fitter = AiryPat(self.x[self.i1:self.i2], self.y[self.i1:self.i2])
        self.popt, self.pcov = self.fitter.fit(guess)

    def _plot_fit(self):
        self.ax.cla()
        #plothyst(self.x, self.y)            # Plot data
        plothyst(self.fitter.x, self.fitter.y) # Plot data
        xf, yf = self.fitter.build_curve()  # Plot fit curve
        plt.plot(xf, yf, "-")
        #plt.show()
        plt.pause(1)

    def _get_result(self):
        Ic = self.popt[0]
        H0 = self.popt[2]
        dH1 = 3.81/np.pi/self.popt[1]
        return {"Ic": Ic, "H0": H0, "dH1": dH1, "pcov": self.pcov}

    def run(self, **kwargs):
        """Load and fit datafile to Airy pattern.

        Keyword arguments:
            datafile -- string
        """
        self._load_data(kwargs["datafile"])
        self._plot_data()
        done = self._query_param()

        # Repeat until user is satisfied
        while not done:
            self._fit()
            self._plot_fit()
            done = self._query_param()

        try:
            return self._get_result()
        except NameError:
            return None

def test():
    print(FitAiryPat().run(datafile="testdata.txt"))

def main():
    """Entrypoint"""
    if len(sys.argv) > 5:
        guess = tuple(map(float, sys.argv[1:]))
    else:
        guess = None

    dfiles = glob.glob("*.dat")
    for dfile in dfiles:
        data = pd.read_table(dfile, sep='\s+', comment="#")
        x, y = (data['T'], data["Vac_device"])
        plt.plot(x, y, "o", label=dfile)
        plt.legend(loc=2)

        if len(sys.argv) > 5:
            y2 = genlogistic(x, *guess)
            plt.plot(x, y2, "-")
        plt.pause(5)

        fitter = T_R_genlogistic(x, y)
        Tc, Rc, perr = fitter.fit()
        print("Tc, Rc, error =", Tc, Rc, perr)
        print("Fit parameters =", fitter.popt)
        xfit, yfit = fitter.build_fitcurve()
        plt.plot(xfit, yfit, "-")
        #plt.plot(Tc, Rc, "s")
        plt.pause(5)
        plt.cla()
    #plt.pause(10)

if __name__ == "__main__":
    test()
