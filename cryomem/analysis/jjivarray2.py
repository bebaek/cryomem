"""
Analyze JJ IV curve array (core) v.2

BB, 2016
"""

import numpy as np
from . import jjiv2 as jjiv
import sys

def fit2rsj_arr(iarr, varr, **kwargs):
    """Fit IV array to 2 Ic RSJ model and return arrays of fit params, error.

    Keyword arguments:
    guess: array of (Ic+, Ic-, Rn, Vo)
    io: fixed Io.
    updateguess: guess update ratio 0 to 1
    """
    if 'guess' in kwargs:
        kwargs['guess'] = np.array(kwargs['guess']) # array type
    update = kwargs.get('updateguess', 0.95)

    n = len(iarr)
    npopt = 4
    popt_arr, pcov_arr = np.zeros((n, npopt)), np.zeros((n, npopt, npopt))
    for k in range(n):
        try:
            done = False; l = 0
            while not done:
                # fit
                popt, pcov = jjiv.fit2rsj(iarr[k], varr[k], **kwargs)

                # update guess
                if k == 0:
                    kwargs['guess'] = popt
                else:
                    kwargs['guess'] = (1-update)*kwargs['guess'] + update*popt

                # check if fit is good
                l += 1
                if np.shape(pcov)==(4,4):
                    perr = np.sqrt(np.diag(pcov))
                else:
                    perr = (np.inf, np.inf, np.inf, np.inf)
                if (np.amax(perr) < .05) or (l > 5):
                    done = True
                    popt_arr[k], pcov_arr[k] = popt, pcov
                else:
                    print('Fit not good. Index: {}, Trial: {}'.format(k,l))
        except RuntimeError:
            print('Can\'t fit. Index: {}!'.format(k))

    return popt_arr, pcov_arr

