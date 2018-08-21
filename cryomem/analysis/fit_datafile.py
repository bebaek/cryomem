"""
Fit (any) datafile.
"""
from ..common import datafile
from . import jjivarray2
from . import jj_curves
from scipy.optimize import curve_fit
from collections import OrderedDict
import numpy as np
import os.path
from copy import deepcopy

def _get_fit_intention(fi, **kwargs):
    intention = {"save": False}                 # Default
    if ("VItrace-HI" in fi) or ('BIV' in fi):
        intention["data"] = "BIarrVarr_JJ"
        if "RSJ" in fi:
            intention["model"]  = "Airypat"
        else:
            intention["model"]  = "RSJ"
            intention["bundle"] = ["B"]
            intention["save"]   = True
    return intention

    intention = {"data": "BIarrVarr_JJ", "model": "RSJ", "bundle": ["Bapp"]}
    return intention

def fit_IarrVarr_RSJ(data, md=None, **kwargs):
    """Fit IVs to RSJ model and return fit parameter arrays as data dict.
    Deprecated."""
    func = lambda _i, icp, icn, r, vo: \
            jj_curves.V_RSJ_asym(_i, icp, icn, r, 0, vo)
    kwargs2 = {}
    kwargs2['model'] = "rsj_asym"
    kwargs2['io'] = io = kwargs.get('io', 0)
    if 'guess' in kwargs:
        kwargs2['guess'] = kwargs['guess']
    if 'updateguess' in kwargs:
        kwargs2['updateguess'] = kwargs['updateguess']
    else:
        kwargs2['updateguess'] = 0.8
        print('Default updateguess =', kwargs2['updateguess'])

    Iarr, Varr = data["Iarr"], data["Varr"]
    popt_arr, pcov_arr = jjivarray2.fit2rsj_arr(Iarr, Varr, **kwargs2)

    # Build a new data ordereddict with fit parameters
    datao = OrderedDict()
    for k, key in enumerate(["Icp", "Icn", "Rn", "V0"]):
        datao[key] = popt_arr[:,k]

    # Add extra info to md
    md["fitfunc_nosave"]   = func
    md["fitx_nosave"]      = data["Iarr"]
    return datao, md

def fit_BIV_RSJ(data, md=None, **kwargs):
    """Fit IVs to RSJ model and return fit parameter arrays as data dict."""
    func = lambda _i, icp, icn, r, vo: \
            jj_curves.V_RSJ_asym(_i, icp, icn, r, 0, vo)
    kwargs2 = {}
    kwargs2['model'] = "rsj_asym"
    kwargs2['io'] = io = kwargs.get('io', 0)
    if 'guess' in kwargs:
        kwargs2['guess'] = kwargs['guess']
    if 'updateguess' in kwargs:
        kwargs2['updateguess'] = kwargs['updateguess']
    else:
        kwargs2['updateguess'] = 0.8
        print('Default updateguess =', kwargs2['updateguess'])

    #Iarr, Varr = data["Iarr"], data["Varr"]
    # Separate I and V and deserialize multi-D data
    data['I'], data['V'] = data['IV'][:, 0], data['IV'][:, 1]
    tmp = datafile.deserialize_data(data, ['B'], ['I', 'V'])
    Iarr, Varr = tmp['I'], tmp['V']
    #print('Iarr, Varr:', Iarr, Varr)
    #Iarr, Varr = IVarr[:, 0], IVarr[:, 1]

    popt_arr, pcov_arr = jjivarray2.fit2rsj_arr(Iarr, Varr, **kwargs2)

    # Build a new data ordereddict with fit parameters
    datao = OrderedDict()
    for k, key in enumerate(["Icp", "Icn", "Rn", "V0"]):
        datao[key] = popt_arr[:,k]

    # Add extra info to md
    md["fitfunc_nosave"]   = func
    md["fitx_nosave"]      = data["I"]
    return datao, md

def fit_BIc_Airypat(data, md=None, **param):
    """Fit BIc to Airypat model and return fit parameters as data dict.

    Arguments:
        data, md=None
    Keyword arguments:
        istart, iend:       integer. Index start and end values for fit.
        Icp0, Bcen0, Bnod0:    float. Fit guess
    Return:
        datao, md: dictionary or None
    """
    ind        = range(param.get("istart", 0), param.get("iend", len(data["B"])))
    x, y        = data["B"][ind], data["Icp"][ind]
    func        = jj_curves.airypat_easy

    # Make quick guess and fit
    Ic0         = param.get("Icp0", np.amax(y))
    ind2        = y > Ic0*0.9
    Bcen0       = param.get("Bcen0", np.mean(x[ind2]))
    Bmax        = np.max(x)
    Bnod0       = param.get("Bnod0", Bcen0 + (Bmax - Bcen0)*0.7)
    guess       = [Ic0, Bcen0, Bnod0]
    popt, pcov  = curve_fit(func, x, y, guess)
    Rn          = np.mean(data['Rn'])   # often needed for IcRn eval
    datao       = OrderedDict([("Icp", popt[0]), ("Bcen", popt[1]),
                               ("Bnod", popt[2]), ('Rn', Rn)])

    # Add extra info to md
    md["fitfunc_nosave"]   = func
    md["fitx_nosave"]      = x
    return datao, md

def fit_datafile(fi, **kwargs):
    """Fit datafile. Try to infer user's intention by context.

    Arguments:
        fi: Datafile
    Keyword arguments:
        fo: Output filename. Default: fi.
        model: Fit model. Default: RSJ.
        The rest is handed over to the called fitting function.
    Return:
        data, md, fit_function
    """
    # Find intention
    intention   = _get_fit_intention(fi, **kwargs)
    head, tail  = os.path.split(fi)
    root, ext   = os.path.splitext(tail)
    fo          = kwargs.get("fo", os.path.join(head, "{}_{}{}".format(
                  intention["model"], root, ext)))

    data, md    = datafile.load_data(fi)

    # Choose and run proper fit function
    if intention["data"] == "BIarrVarr_JJ":
        if intention["model"]   == "RSJ":
            #datao, md  = fit_IarrVarr_RSJ(data, md=md, **kwargs)
            datao, md  = fit_BIV_RSJ(data, md=md, **kwargs)
        elif intention["model"] == "Airypat":
            datao, md  = fit_BIc_Airypat(data, md=md, **kwargs)

    # If fit results are arrays, save to file.
    if intention["save"]:
        for key in intention["bundle"]:
            datao[key] = data[key]

        # Cannot directly save the added md elements: fitfunc, fitx
        #md2 = deepcopy(md); del md2["fitfunc"]; del md2["fitx"]
        datafile.save_data(fo, datao, md=md)

    return datao, md
