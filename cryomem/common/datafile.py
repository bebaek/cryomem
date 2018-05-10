"""
Handle all kinds of datafiles.
"""
from . import datafile_cmtools
from . import metadata
import pandas as pd
import numpy as np
import os, zipfile
from io import StringIO, BytesIO

##### start of old cmtools stuff #####

def cdim_from_filename(filename):
    """Return N of control parameters"""
    if ('_VItrace-H_' in filename) or ('_VItrace-Hpulse_' in filename)\
      or ('_VIH_' in filename):
        cdim = 1
    elif ('_VItrace-IH_' in filename) or ('_VItrace-HI_' in filename):
        cdim = 2
    elif ('_VItrace-HIpulse_' in filename):
        cdim = 3
    else:
        print('Not a valid data file.'); sys.exit(1)
    return cdim

def load_tdsbin(fname, ftype='tdsbin'):
    root, ext = os.path.splitext(fname)
    if ftype == 'tdsbin':                          # Raw trace file
        cdim = cdim_from_filename(root)
        data = datafile_cmtools.IVArrayBin8b(root)
        data.readcfgfile()
        data.readdatafile(cdim=cdim)
        data.convert2iv()

        # Now make md and data dataframes.
        mdo = load_cmtools_cfg(root)
        mdo["srcfile"] = root + ".dat"
        datao = {"Bapp": data.c[:,0],   "Iapp": data.c[:,1],
                "Iarr": data.i,         "Varr": data.v}
    #elif ftype == 'icarr':               # RSJ fit file
    #    data = datafile.CMData_H_Ic_Rn(fname)
    return datao, mdo

def load_cmtools_cfg(fname):
    root, ext = os.path.splitext(fname)
    md = {}
    with open(root + ".txt", "r") as f:
        for line in f:
            key, value  = line.split("=")
            if key[0] != "#":                   # discard comments
                md[key.strip()] = value.strip()
    print(metadata.parse_md(md))
    return metadata.parse_md(md)

##### end of old cmtools stuff #####

def load_data(fname, dftype="zip"):
    """Load and return data (and metadata) from a zipped datafile.

    Return:
        data: Dictionary.
            Key: data label.
            Value: (n-dim but usually 1-d or 2-d) numpy array.
        md: YAML object (CommentedMap) or None. Metadata.
    """
    root, ext = os.path.splitext(fname)
    if dftype == "zip":
        data = {}
        md   = None
        with zipfile.ZipFile(root + ".zip") as zf:
            for dfname in zf.namelist():        # go through archived files
                #key = os.path.splitext(dfname)[0].split("_")[-1]
                key = os.path.splitext(dfname)[0]
                if key == "md":                 # load metadata
                    #tmpname = "tmp.yaml"
                    #zf.extract(dfname, tmpname)
                    #md = metadata.load_md(file=tmpname)
                    #os.remove(tmpname)
                    with zf.open(dfname) as df:
                        md = metadata.load_md(
                            StringIO(df.read().decode("utf-8")))
                else:                           # load data
                    with zf.open(dfname) as df:
                        data[key] = np.loadtxt(
                            StringIO(df.read().decode("utf-8")))
        return data, md

def save_data_old(fname, data, **kwargs):
    """Save metadata and data to a file.

    Arguments:
        data: Dictionary.
            Key: data label.
            Value: (n-dim but usually 1-d or 2-d) numpy array.
    Keyword arguments:
        md: YAML object (CommentedMap, preferred) or dictionary. Metadata.
    """
    md     = kwargs.get("md", None)
    dftype = kwargs.get("dftype", "zip")
    root, ext = os.path.splitext(fname)

    if dftype == "zip" or ext.lower() == "zip":
        with zipfile.ZipFile(root + ".zip", "a", zipfile.ZIP_DEFLATED) as fo:
            # save data
            for tag in data:
                tmpname = "{}.tmp".format(tag)
                foname  = "{}.txt".format(tag)
                np.savetxt(tmpname, data[tag], fmt="%.6e")
                fo.write(tmpname, foname)
                os.remove(tmpname)

            # save md
            if md != None:
                print("Saving md.")
                tmpname = "md.tmp"
                foname  = "md.txt"
                metadata.save_md(tmpname, md)       # save to tmp
                fo.write(tmpname, foname)           # copy to zip
                os.remove(tmpname)                  # remove tmp

def save_data(fname, data, mode="w", **kwargs):
    """Save metadata and data to a file.

    Arguments:
        data: Dictionary.
            Key: data label.
            Value: (n-dim but usually 1-d or 2-d) numpy array.
        mode: "w": overwrite (default), "a": append
    Keyword arguments:
        md: YAML object (CommentedMap, preferred) or dictionary. Metadata.
    """
    md     = kwargs.get("md", None)
    dftype = kwargs.get("dftype", "zip")
    root, ext = os.path.splitext(fname)

    if dftype == "zip" or ext.lower() == "zip":
        dfname = root + ".zip"
        with zipfile.ZipFile(dfname, mode, zipfile.ZIP_DEFLATED) as zf:
            # save data
            for tag in data:
                s = BytesIO()            # StringIO does not work for py3
                foname  = "{}.txt".format(tag)
                np.savetxt(s, data[tag], fmt="%.6e")    # to mem
                zf.writestr(foname, s.getvalue().decode())         # to zip

            # save md
            if md != None:
                s = StringIO()
                foname  = "md.txt"
                metadata.save_md(s, md)                 # to mem
                zf.writestr(foname, s.getvalue())         # to zip
    else:
        dfname = None
    return dfname

def conv_tdsbin(finame, foname=None):
    """Convert old tdsbin (BIarrVarr) datafile to zipped txt files.

    Arguments:
        finame : String
        foname : String. Default: same as finame
    """
    data, md = load_tdsbin(finame)
    if foname == None:
        foname = finame
    return save_data(foname, data, "w", md=md)
