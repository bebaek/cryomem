"""Useful functions for local directory data analysis"""
import os, platform
import numpy as np
import pandas as pd
from collections import OrderedDict

def _fix_winpath(pathstr):
    if platform.system() == 'Windows':
        #print("Platform: Windows")
        pathstr = '/'.join(pathstr.split('\\'))
    return pathstr

fix_winpath = lambda x: list(np.vectorize(_fix_winpath)(x))

def get_device_id(filename):
    tags = os.path.basename(filename).split('_')
    wafer, chip, device = tags[3], tags[4][-2:], tags[5]
    return wafer, chip, device

def pick_datafiles(target, ignore):
    """Filter out non-datafiles from target list."""
    # apply ignore list
    try:
        ignore = fix_winpath(ignore)
    except:
        ignore = []
    try:
        target = fix_winpath(target)
    except:
        target = []
    for ign in ignore:
        del target[target.index(ign)]

    return target

def load_db(dbname):
    """Open csv-like db file and return the dataframe."""
    try:
        #df = pd.read_table("summary.dat", sep='\s+')
        df = pd.read_csv(dbname)
        #df["chip"] = df["chip"].astype(str)
        print("Loaded existing db:", dbname)
    except:
        df = pd.DataFrame()
    return df

def add_prefix2filename(path, pref):
    head, tail  = os.path.split(path)
    root, ext   = os.path.splitext(tail)
    return os.path.join(head, "{}_{}{}".format(pref, root, ext))

def od2list(od):
    """Convert OrderedDict to list"""
    return [key for key in od], [od(key) for key in od]

def list2od(self, keys, vals):
    """Convert two input lists to fit parameter dict-like to list"""
    return OrderedDict([(k, v) for k, v in zip(keys, vals)])
