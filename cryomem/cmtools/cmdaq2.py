"""
User interface for data management for magnetic JJ research
    Raw data processing (I-V fit) and plot
    High level data management (dev parameter database) and plot

Minimize codes here and delegate details to libcmtools modules.

BB, 2015
"""

import sys
from cmtools.lib import cmdaq_main

def main():
    cmdaq_main.main(sys.argv)

if __name__ == '__main__':
    main()
