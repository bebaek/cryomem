"""
JJ I-V data manipulation v.2

BB, 2016
"""

import numpy as np
from scipy.optimize import curve_fit

# RSJ model
def v_rsj(i, ic, rn, io, vo):
    """Return voltage in RSJ model"""
    if ic < 0 or rn < 0:
        v = 1e10
    else:
        v = np.zeros(len(i))
        n = i>io+ic; v[n] = rn*np.sqrt((i[n]-io)**2-ic**2)+vo
        n = i<io-ic; v[n] = -rn*np.sqrt((i[n]-io)**2-ic**2)+vo
        n = np.logical_and(i>=io-ic, i<=io+ic); v[n]=vo
    return v

def v_rsj_asym(i, ic_pos, ic_neg, rn, io, vo):
    """Return voltage with asymmetric Ic's in RSJ model"""
    if ic_pos < 0 or ic_neg > 0 or rn < 0:
        #or abs(ic_neg/ic_pos) > 1.2 or abs(ic_pos/ic_neg) > 1.2 :
        # set boundaries for fitting
        #pass
        v = 1e10
    else:
        v = np.zeros(len(i))
        n = i>io+ic_pos; v[n] = rn*np.sqrt((i[n]-io)**2-ic_pos**2)+vo
        n = i<io+ic_neg; v[n] = -rn*np.sqrt((i[n]-io)**2-ic_neg**2)+vo
        n = np.logical_and(i>=io+ic_neg, i<=io+ic_pos); v[n]=vo
    return v

def fit2rsj(i, v, **kwargs):
    """Fit with v_rsj or v_rsj_asym. Fix Io.
    Initial guess=[ic, rn, vo] or [ic_pos, ic_neg, rn, vo]
    Return
        popt: optimized params: (Ic, Rn, Vo) or (Ic_pos, Ic_neg, Rn, Vo)
        pcov: covariance of popt
    """
    model = kwargs['model']
    io = kwargs.get('io', 0)
    if 'guess' in kwargs:
        guess = kwargs['guess']
    else:
        # quick guess
        imax = max(i)
        idx = abs(i) < 0.1*imax
        vo = np.mean(v[idx])                    # vo guess

        vmax = max(v)
        idx = abs(v - vo) < 0.1*(vmax - vo)
        ic = (np.max(i[idx]) - np.min(i[idx]))/2    # ic guess

        #idx = i > imax/2
        idx = (v - vo) > (vmax - vo)/2
        rn = np.polyfit(i[idx], v[idx], 1)[0]   # rn guess

        if model == 'rsj':
            guess = [ic, rn, vo] 
        if model == 'rsj_asym':
            guess = [ic, -ic, rn, vo] 
        print('Quick guess:', guess)

    # fit with function with fixed io
    if model == 'rsj':
        _v = lambda _i, ic, r, vo: v_rsj(_i, ic, r, io, vo)
    if model == 'rsj_asym':
        _v = lambda _i, icp, icn, r, vo: v_rsj_asym(_i, icp, icn, r, io, vo)
    #popt, pcov = curve_fit(_v, i, v, guess)
    bounds = ([0,-np.inf,-np.inf,-np.inf],[np.inf,0,np.inf,np.inf])
    popt, pcov = curve_fit(_v, i, v, guess, bounds=bounds, method='trf')

    # if Ic is too low, narrow range and re-fit.
    #icp, icn, r, v0 = popt
    #if min((icp, icn)) < 0.2*imax:
    #    k = abs(i) < 0.3*imax           # narrower I range
    #    _v2 = lambda _i, icp, icn, vo: v_rsj_asym(\
    #        _i, icp, icn, r, io, v0) # fix R
    #    guess2 = (icp, icn, v0)
    #    popt2, pcov2 = curve_fit(_v2, i[k], v[k], guess2)
    #    popt = np.array([popt2[0], popt2[1], popt[2], popt2[2]])
    #    #pcov = np.array([pcov2[0], pcov2[1], pcov[2], pcov2[2]])

    return popt, pcov

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    i = np.linspace(-100, 100, 200)
    v = v_rsj_asym(i, 10, -20, 10, 0, 5)
    #v = v_rsj(i, 10, 10, 0, 5)
    fig = plt.figure()
    ax = fig.add_subplot()
    plt.plot(i,v)
    plt.show()
