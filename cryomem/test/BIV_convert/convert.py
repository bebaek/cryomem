"""Convert all cmtools oscilloscope datafiles to zip datafiles."""
from cryomem.common.datafile import conv_tdsbin
from glob import glob
import os.path
import os

datadir = "data"
datafiles = sorted(glob(datadir + "/*.dat"))
for df in datafiles:
    # make a new datafile
    root, ext = os.path.splitext(df)
    print("Datafiles converted to:", conv_tdsbin(df))

    # remove old files
    for ext in [".dat", ".txt", ".osccfg"]:
        os.remove(root + ext)
        print("Removed", root + ext)
