"""
User interface for magnetotransport DAQ for magnetic JJ research

Minimize codes here and delegate details to libcmtools modules.

BB, 2015
"""

import sys
import numpy as np
import ntpath

from cmtools.lib import daq_dipstick
from cmtools.lib import datafile
from cmtools.lib import convargs

# main class
class cmdaqiv:

    # For now, just wrap the slightly-modified old codes
    def call(self, cmd, **kwargs):
        print(kwargs)
        getattr(daq_dipstick, cmd)(**kwargs)

# Handle command line run. Convert shell args to kw args
def main():
    if len(sys.argv) < 2:
        print('\n'
          'Usage: cmdaq\n'
          '       cmdaq <command> [--option1 value1 value2 ...]\n'
          '*Values are in Oe, A, V, s.\n'
          '\n'
          'Examples (\'[...]\' means optional):\n'
          '       cmdaq reset\n'
          '       cmdaq set_dccurrent --i 10e-6\n'
          '       cmdaq set_field --h 100 [--noramp] [--t 5]\n'
          '       cmdaq set_field --h1 0 --h2 1000 [--t 5]\n'
          '       cmdaq set_heat [--t 5] [--i 0.05]\n'
          '       cmdaq set_sweepvolt --v 0.1\n'
          '       cmdaq get_vitrace_vs_h_i --h 300 '
                    '[-10 -300 [10 300 [...]] [--dbl_bias]\n'
          '       cmdaq get_v_dvdi_vs_h_i --h 300 '
                    '[-10 -300 [10 300 [...]] [--dbl_bias]\n'
          '\n'
          '--h1, --h2: initial and final fields; ramp mode by default\n'
          '--t: set pulse mode with t second duration\n'
          '--noramp: disable ramp\n'
          '--dbl_bias: use two aux outs; channels specified in cfg\n'
          )
        sys.exit(0)
    cmd = sys.argv[1]
    kwargs = convargs.convargs(sys.argv[2:])   # make args kwargs
    main = cmdaqiv()
    main.call(cmd, **kwargs)

if __name__ == '__main__':
    main()
