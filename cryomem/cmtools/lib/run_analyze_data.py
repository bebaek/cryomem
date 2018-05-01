# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Run analyze_data.py

BB, 2014
"""

import analyze_jjivarray as an
#from IPython.lib import deepreload; deepreload.reload(an)
from imp import reload; reload(an)

def app():    
    # set parameters
    #filename = '077_VItrace-HI_150323a_chip53_A01_mccdaqtest_5000 OeRP'
    filename = '047_VItrace-HI_150323a_chip56_A02_continued'
    rsjguess = [5e-6, 0.011, 0, 0]    # RSJ fit params
#    tn = 68    # AH fit param
    
	# plot raw
    #an.plot_raw_ivarraytds(filename)

    # fit
    #an.fit2rsj_ivarraytds(filename, rsjguess)   # RSJ fit
#    an.fit2ah_ivarraytds_1(filename, tn, step=4)   # AH fit
#    an.fit2ah_ivarraytds_2(filename, tn, step=1)

    # plot fit parameters
    an.plot_rsj_params(cind=1, filename='fit2RSJ_'+filename+'.txt') # FIMS
    #~ an.plot_rsj_params(cind=2, filename='fit2RSJ_'+filename+'.txt')  # CIMS
#    an.plot_ah_params('fit2AH_'+filename+'.txt')
#    an.plot_ah_params('fit2AH_'+filename+' - Copy.txt')
    
    # plot IV
    #an.plot_iv(-2, filename, showrsj=False, showah=False)
    #an.plot_iv(0, filename, showrsj=True, saveraw=False, saversj=False)


if __name__ == '__main__':
    import sys
    print(sys.version)
    app()
