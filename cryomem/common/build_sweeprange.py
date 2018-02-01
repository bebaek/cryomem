import numpy as np

def build_sweeprange(swpparams):
    """Convert multi-segment list format to a simple array."""
    # swpparams = [a0, astep0, a1, astep1, a2, ...] or just [a0]
    
    carray = np.array([])
    nseg = int((len(swpparams)-1)/2)
    print("nseg =", nseg, flush=True)
    if nseg == 0:
        carray = np.array([swpparams[0]])
    else:
        for k in range(nseg):
            swpstart = swpparams[k*2]
            swpstep  = swpparams[k*2+1]
            swpend   = swpparams[k*2+2]
            
            # bypass floating point anomaly in arange
            #if (swpstep < 100):
            #    #print -np.log10(swpstep/100)
            #    m = 10**np.ceil(-np.log10(abs(swpstep)/100))
            #    #print("m =", m)
            #    swpstart = round(m*swpstart)
            #    swpstep  = round(m*swpstep)
            #    swpend   = round(m*swpend)
            #else:
            #    m = 1
            m = 1
            print(swpstart, swpstep, swpend, flush=True)
            carray = np.hstack((carray, np.arange(swpstart, swpend, swpstep)/m))
        carray = np.hstack((carray, np.array([swpend/m])))
    print(carray, flush=True)
    return carray
