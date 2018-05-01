"""
Main caller
"""
import importlib, sys
from . import daq_dipstick

def main(args):
    """Call DAQ user functions from shell command line"""
    def str2bool(s):
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            raise ValueError

    if len(args) < 2:
        print('')
        print('Usage: python daq_dipstick.py <command> [<arguments>]\n')
        print('Examples:')
        print('python daq_dipstick.py reset')
        print('python daq_dipstick.py set_dccurrent i=1e-4')
        print('python daq_dipstick.py set_dccurrent i=1e-4 t=3')
        print('python daq_dipstick.py set_field h=80')
        print('python daq_dipstick.py set_field h1=0 h2=1000 t=5')
        print('python daq_dipstick.py set_heat t=3')
        print('python daq_dipstick.py sqwave_field h=150')
        print('python daq_dipstick.py set_sweepvolt .7')
        print('python daq_dipstick.py get_sweepvolt')
        print('python daq_dipstick.py set_accurrent ampl=1e-6 freq=190')
        print('python daq_dipstick.py get_dvdi')
        print('python daq_dipstick.py get_vitrace_vs_h_i h=0,20,100,-20,0 '
          'pulse=True')
        print('python daq_dipstick.py get_vitrace_vs_h_i h=100 '
          'i=0,.001,.02,-.001,-.02,.001,.02 dbl_bias=True')
        print('python daq_dipstick.py get_v_dvdi_vs_h_i h=100 '
          'i=0,.001,.02,-.001,-.02,.001,.02 dbl_bias=True')
        print('python daq_dipstick.py save_daqparams "datafile tag = jj0_CIMS"', flush=True)
        sys.exit(0)
    func = args[1]
    #print(args[2])
    posargs = []
    kwargs = {}
    if func in ['set_dccurrent', 'set_field', 'set_heat', 'reset',\
      'set_sweepvolt', 'get_sweepvolt', 'sqwave_field', 'save_params',\
      'save_daqparams', 'set_accurrent', 'get_dvdi']:
        # easy ones: no list argument
        for arg in args[2:]:
            try:
                posargs.append(float(arg))
            except ValueError:
                pass
            try:
                tmp = arg.split('=')
                kw = tmp[0].strip()
                val = tmp[1].strip()
                if val:
                    try:
                        kwargs[kw] = float(val)
                    except ValueError:
                        try:
                            kwargs[kw] = str2bool(val)
                        except ValueError:
                            kwargs[kw] = val
                    print(kw, kwargs, flush=True)
            except (ValueError, IndexError):
                pass
        #globals()[func](*posargs, **kwargs)
        getattr(daq_dipstick, func)(*posargs, **kwargs)
    elif func in ['get_vitrace_vs_h_i', 'get_v_dvdi_vs_h_i']:
        # less easy ones: list arguments as main
        for arg in args[2:]:
            try:
                newposarg = list(map(float, arg.split(',')))
                posargs.append(newposarg)
            except ValueError:
                pass
            try:
                kw, val = arg.split('=')
                if val:
                    #~ try:
                        #~ kwargs[kw] = float(val)
                    #~ except ValueError:
                    try:
                        kwargs[kw] = list(map(float, val.split(',')))
                    except ValueError:
                        kwargs[kw] = str2bool(val)
            except ValueError:
                pass
        #globals()[func](*posargs, **kwargs)
        getattr(daq_dipstick, func)(*posargs, **kwargs)
    elif func in ['tune_iv']:
        # run function from external module
        getattr(importlib.import_module(func), func)()

    #print('posargs = ', posargs, flush=True)
    #print('kwargs =', kwargs, flush=True)
    #globals()[func](*posargs, **kwargs)

