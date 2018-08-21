import os
import numpy as np
from numpy import log10
from numpy.polynomial.chebyshev import chebval
import ruamel_yaml as yaml

class Cernox:
    def __init__(self, **kwargs):
        sn = kwargs.get("serial", "X104724")
        if sn == "X104724":
            fpath = "{}/{}.cof".format(os.path.dirname(os.path.abspath(__file__)), sn)
            with open(fpath, "r") as f:
                s = f.read()
            _config = yaml.load(s)
            self.fitdata = self._get_fitdata(_config)

    def _get_fitdata(self, cfg):
        """Return a list of Chebyshev coefficient data for calibration"""
        result = []
        for n in range(1,cfg["Number of fit ranges"]+1):
            section = {}

            # log of resistance range
            key = "Zlower for fit range"
            section[key] = cfg[key + str(n)]
            key = "Zupper for fit range"
            section[key] = cfg[key + str(n)]

            # coefficients
            section["coef"] = []
            for m in range(cfg["Order of fit range" + str(n)]):
                key = "C({}) Equation {}".format(m, n)
                section["coef"].append(cfg[key])

            result.append(section)
        return result

    def _get_temperature(self, R):
        """Return temperature from input resistance or voltage based on
        calibration"""
        # Find the right resistance range
        for n in range(len(self.fitdata)):
            Z = log10(R)
            ZL = self.fitdata[n]["Zlower for fit range"]
            ZU = self.fitdata[n]["Zupper for fit range"]
            if Z > ZL and Z < ZU:
                # Apply the formula
                k = ((Z-ZL)-(ZU-Z))/(ZU-ZL)
                T = chebval(k, self.fitdata[n]["coef"])
                return T

        print("Temperature out of calibration range.")

    def get_temperature(self, R):
        if hasattr(R, "__iter__"):
            return np.vectorize(self._get_temperature)(R)
        else:
            return self._get_temperature(R)

if __name__ == "__main__":
    R = 42
    #R = 555.3051
    Z = log10(R)
    print("R = {}. Z = {}".format(R, Z))
    print("T =", Cernox(serial="X104724").get_temperature(R))
