"""Useful functions for local directory data analysis"""
import os
import os.path
import platform
import numpy as np
import pandas as pd
from collections import OrderedDict
from copy import deepcopy

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

    #for ign in ignore:
    #    del target[target.index(ign)]
    target2 = deepcopy(target)
    for t in target:
        for ign in ignore:
            if os.path.split(t)[1] in ign:
                del target2[target2.index(t)]
                break
    return target2


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
    return _fix_winpath(os.path.join(head, "{}_{}{}".format(pref, root, ext)))


def od2list(od):
    """Convert OrderedDict to list"""
    return [key for key in od], [od(key) for key in od]


def list2od(self, keys, vals):
    """Convert two input lists to fit parameter dict-like to list"""
    return OrderedDict([(k, v) for k, v in zip(keys, vals)])
