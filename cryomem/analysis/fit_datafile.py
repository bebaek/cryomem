"""
Fit (any) datafile.
"""
from . import jjivarray2
from ..common import datafile

def _get_fit_intention(fi, **kwargs):
    intention = {"data": "BIarrVarr_JJ", "model": "RSJ"}
    return intention

def fit_datafile(fi, **kwargs):
    """Fit datafile. Try to infer user's intention by context.

    Arguments:
        fi: Datafile
    Keyword arguments:
        fo: Output filename. Default: fi.
        model: Fit model. Default: RSJ.
    """
    fo = kwargs.get("fo", fi)

    # Load datafile
    data, md = datafile.load_data(fi)
    intention = _get_fit_intention(fi, **kwargs)

    # Fit
    if intention["data"] == "BIarrVarr_JJ":
        if intention["model"] == "RSJ":
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

            # Replace or add to data dictionary
            for k, key in enumerate(["fit_Ic", "fit_Rn", "fit_I0", "fit_V0"]):
                data[key] = popt_arr[:,k]

    # Save/overwrite data and md. (zipfile doesn't support modifying.)
    datafile.save_data(fo, data, md=md)

    return data
