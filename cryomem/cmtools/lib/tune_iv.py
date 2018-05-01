"""
Autotune I-V DAQ using scope
"""
from . import daq_dipstick
import numpy as np
from . import jjiv2 as jjiv

class bias:
    """Bias handler"""
    def __init__(self, meas):
        self.meas = meas
        self.istep = 100e-6

    def get_i(self):
        return self.meas.get_sweepi()

    def set_i(self, i):
        self.meas.set_sweepi(i)

    def inc(self):
        i = self.get_i()
        if self.istep < 0:
            self.istep *= -0.5
        i += self.istep
        self.set_i(i)

    def dec(self):
        i = self.get_i()
        if self.istep > 0:
            self.istep *= -0.5
        i += self.istep
        self.set_i(i)

def get_jjparam(i, v, **kwargs):
    """Extract Ic and Rn from I and V.

    Keyword parameters:
    guess: fit guess [Ic+, Ic-, Rn, Vo]
    """
    rmin = kwargs.get('rmin', 1e-5)

    # linear fit to R
    r, v0 = np.polyfit(i, v, 1)

    if r < rmin:        # all supercurrent
        return 0.1, r
    else:               # if R looks good, fit to RSJ model
        guess = kwargs.get('guess', [10e-6, -10e-6, r, 0])
        popt, pcov = jjiv.fit2rsj_asym(i, v, io=0, guess=guess)
        ic, rn = max(abs(popt[:2])), popt[2]
        return ic, rn

def tune_iv(**kwargs):
    """Autotune IV scoping.

    ch1: device out, ch2: bias monitor
    kwargs: guess Ic, Rn
    """
    meas = daq_dipstick.DAQDipstick()
    b = bias(meas)
    ibias_min = 1e-6
    rmin = 1e-5
    rmax = 100
    
    def inc_yscale(ch):
        scale = meas.instr_scope.get_vscale(ch)
        if scale - 5 < 0.5:
            print('{} scale is already max.'.format(ch))
            return
        elif str(scale)[0] == '2':
            scale *= 2.5
        else:
            scale *= 2
        meas.instr_scope.set_vscale(ch, scale)

    def dec_yscale(ch):
        scale = meas.instr_scope.get_vscale(ch)
        if scale - 0.002 < 0.0002:
            print('{} scale is already min.'.format(ch))
            return
        elif str(scale)[0] == '5':
            scale /= 2.5
        else:
            scale /= 2
        meas.instr_scope.set_vscale(ch, scale)

    def get_wfm(ch):
        ybin = meas.instr_scope.gettracebin(int(ch[2]))
        yoff = meas.instr_scope.get_yoff(ch)
        ymult = meas.instr_scope.get_ymult(ch)
        return meas.instr_scope.wfm2array(ybin, yoff, ymult)

    def traces2iv(vbias, vout):
        i = meas.v2i_sweepbias(vbias)
        v = meas.vout2vdev(vout)
        #self.v /= meas.daqparams.gain            # apply v amp gain
        #self.i *= meas.daqparams.i_per_v_swpbias # apply i/v factor
        return i, v

    # init scope
    # turn on ch1, ch2, coupling dc, (y scale 5V), offset 0; 
    # t scale 10 ms, (offset 0)
    # acq avg n=4; trig ch2, auto, rising, level 0
    meas.init_scope(timeout=3)  # timeout means no trigger
    meas.instr_scope.write('SEL:CH1 ON')
    meas.instr_scope.write('SEL:CH2 ON')
    meas.instr_scope.write('CH1:COUP DC')
    meas.instr_scope.write('CH2:COUP DC')
    #meas.instr_scope.write('CH1:SCA 5')
    #meas.instr_scope.write('CH2:SCA 5')
    #meas.instr_scope.set_vpos(1, 0)
    meas.instr_scope.set_vpos(2, 0)
    meas.instr_scope.write('HOR:MAI:SCA 5E-4')
    meas.instr_scope.write('HOR:MAI:POS 0')
    #meas.instr_scope.write('HOR:DEL:POS 0')
    meas.instr_scope.write('ACQ:MOD AVE')
    meas.instr_scope.write('ACQ:NUMAV 4')
    meas.instr_scope.write('TRG:MAI:SOU CH2')
    meas.instr_scope.write('TRG:MAI:TYP EDGE')
    meas.instr_scope.write('TRG:MAI:MOD AUTO')
    meas.instr_scope.write('TRG:MAI:LEV 0')

    # init fgen: triangular, freq 93 Hz, (ampl 0)
    meas.init_sweepvolt()
    meas.instr_sweepvolt.set_waveform('triangle')
    meas.instr_sweepvolt.set_freq(93)
    if b.get_i() < ibias_min:
        b.set_i(ibias_min)

    # main loop
    tuned = False
    while not tuned:
        # loop: tune scope
        scopetuned = False
        while not scopetuned:
            # get traces
            msg = meas.instr_scope.acquiresingle()
            triggered = False if msg == 'timeout' else True

            if not triggered:
                # reduce ch2 range until triggered 
                dec_yscale('ch2')
            else:
                # adjust scope range
                scopetuned = {}
                y = {}
                for ch in ('ch2', 'ch1'):
                    scopetuned[ch] = False
                    y = get_wfm(ch)
                    ymax, ymin = (np.amax(y), np.amin(y))
                    ymid = (ymax - ymin)/2
                    
                    if ymid > 24:       # check center. 1 tick off
                        meas.instr_scope.set_vpos(ch, ymid*8/256)
                        ymax2 = ymax - ymid
                        if ymax2 < 60:
                            inc_yscale(ch)
                        elif ymax2 > 120:
                            dec_yscale(ch)
                    elif ymax < 60:     # check scale
                        dec_yscale(ch)
                    elif ymax > 120:
                        inc_yscale(ch)
                    else:               # no more change
                        scopetuned[ch] = True
                        y[ch] = y
                scopetuned = scopetuned['ch1'] & scopetuned['ch2']

        # extract Ic and Rn
        i, v = convert2iv(y['ch2'], y['ch1'])
        ic, rn = get_jjparam(i, v, rmin=rmin)

        # adjust bias
        if biasiter > maxbiasiter:          # too many iteration
            print('Failed: Max bias iteration reached.')
            tuned = True
        elif abs(bias.step) < minibiasstep: # too many iteration
            print('Failed: Min bias step reached.')
            tuned = True
        elif rn > rmax:                     # open device
            print('Failed: Too high resistance.')
            tuned = True
        elif rn < rmin:                     # v = 0 
            b.inc()
            biasiter += 1
        elif ic/bias.i > .25:               # high Ic
            b.inc()
            biasiter += 1
        elif ic/bias.i < .2:                # low Ic
            b.dec()
            biasiter += 1
        else:                               # success 
            tuned = True

if __name__ == '__main__':
    tune_iv()
