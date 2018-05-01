"""Handle device specification

BB, 2016
"""
import pandas as pd

class DevLoc:
    def __init__(self, fname):
        """Load spec file"""
        self.df = pd.read_excel(fname, sheetname='dev_loc')

    def get_devloc(self, devid):
        """Return device location x, y in um"""
        x, = self.df[self.df.device==devid].x.values
        y, = self.df[self.df.device==devid].y.values
        return float(x), float(y)

if __name__ is '__main__':
    devloc = DevLoc('sfs9.xlsx')
    print(devloc.get_devloc('A03'))

