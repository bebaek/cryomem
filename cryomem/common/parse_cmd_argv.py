def isfloat(s):
    try:
        val = float(s)
    except ValueError:
        return False
    else:
        return True

def isbool(s):
    if s == 'True' or s == 'False':
        return True
    else:
        return False

def str2bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False

# Convert value types to: float, bool, string 
def str2other(s):
    if isfloat(s):
        val = float(s)
    elif isbool(s):
        val = str2bool(s)
    else:
        val = s
    return val

# Convert command line args to kwargs.
# Convert types to one of string, float, boolean.
def convargs(args0):
    kwargs = {}
    nval = 0
    val = True            # default value
    isoption = False

    # Make dictionary first
    k = 0
    for k, arg0 in enumerate(args0):
        if len(arg0) > 2:       # detect option
            if arg0[:2] == '--':  
                if k > 0:       # if not first, add detected key-val pair
                   kwargs[key] = val
                key = arg0[2:]
                val = True      # reset default value
                isoption = True
                nval = 0
        if not isoption:        # detect a value
            if nval == 0:       # detect first value
                val = str2other(arg0)
                nval += 1
            elif nval == 1:     # multiple values per option -> list
                val = [val, str2other(arg0)]
                nval += 1
            else:               # multiple values per option -> list
                val += [str2other(arg0)]
        else:                   # get to value detection mode
            isoption = False
            
    if k > 0:               # take care of the last argument
        kwargs[key] = val
    #print('converted kwargs =', kwargs)
    return kwargs

def parse_cmd_argv(argv):
    """Parse command line arguments into list and keyword arguments"""
    #print(argv)
    return [], convargs(argv[1:])
