"""
Fit (any) datafile.
"""
from ..common import datafile
from . import jjivarray2
from . import jj_curves
from scipy.optimize import curve_fit
import numpy as np
import os.path

def _get_fit_intention(fi, **kwargs):
    intention = {"save": False}                 # Default
    if "VItrace-HI" in fi:
        intention["data"] = "BIarrVarr_JJ"
        if "RSJ" in fi:
            intention["model"]  = "Airypat"
        else:
            intention["model"]  = "RSJ"
            intention["bundle"] = ["Bapp"]
            intention["save"]   = True
    return intention

    intention = {"data": "BIarrVarr_JJ", "model": "RSJ", "bundle": ["Bapp"]}
    return intention

def fit_IarrVarr_RSJ(data, md=None, **kwargs):
    """Fit IVs to RSJ model and return fit parameter arrays as data dict."""
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

    # Build a new data dictionary with fit parameters
    datao = {}
    for k, key in enumerate(["Ic", "Rn", "I0", "V0"]):
        datao[key] = popt_arr[:,k]
    return datao, md

def fit_BIc_Airypat(data, md=None, **param):
    """Fit BIc to Airypat model and return fit parameters as data dict.

    Arguments:
        data, md=None
    Keyword arguments:
        start, end: integer. Index start and end values for fit.
        guess: dictionary. {"Ic": float, "Bcen": float, "Bnod": float}
    Return:
        datao, md: dictionary or None
    """
    end2        = param["end"] if "end" in param else len(data["Ic"])
    ind         = range(param.get("start", 0), end2)
    x, y        = data["Bapp"][ind], data["Ic"][ind]
    func        = jj_curves.airypat_easy

    # Process guess
    Ic0         = param.get("Ic", np.amax(y))
    ind2        = y > Ic0*0.9
    Bcen0       = param.get("Bcen", np.mean(x[ind2]))
    Bmax        = np.max(np.abs(x))
    Bnod0       = param.get("Hnod", Bcen0 + (Bmax - np.abs(Bcen0))*0.5)
    guess       = [Ic0, Bcen0, Bnod0]
    popt, pcov  = curve_fit(func, x, y, guess)
    datao       = {"Ic": popt[0], "Bcen": popt[1], "Bnod": popt[2]}
    return datao, md

def fit_datafile(fi, **kwargs):
    """Fit datafile. Try to infer user's intention by context.

    Arguments:
        fi: Datafile
    Keyword arguments:
        fo: Output filename. Default: fi.
        model: Fit model. Default: RSJ.
    """
    # Find intention
    intention   = _get_fit_intention(fi, **kwargs)
    root, ext   = os.path.splitext(fi)
    fo          = kwargs.get("fo", "{}_{}.{}".format(
                  intention["model"], root, ext))

    data, md    = datafile.load_data(fi)

    # Choose and run proper fit function
    if intention["data"] == "BIarrVarr_JJ":
        if intention["model"] == "RSJ":
            datao, md = fit_IarrVarr_RSJ(data, md=md, **kwargs)
        elif intention["model"] == "Airypat":
            datao, md = fit_BIc_Airypat(data, md=md, **kwargs)

    # Save fit results and md. Existing fit file will be overwritten.
    if intention["save"]:
        for key in intention["bundle"]:
            datao[key] = data[key]
        datafile.save_data(fo, datao, md=md)

    return datao, md
