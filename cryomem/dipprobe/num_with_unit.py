def isnumstr(s):
    try:
        a = int(s)
        return True
    except:
        try:
            a = float(s)
            return True
        except:
            return False

def numstr2num(s):
    """Return a converted number or a trimmed string."""
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return s.strip()

_std_unit = ("s", "V", "A", "Ohm", "Hz", "T")
_extra_unit = {
    "Oe": ("T", 1e-4),
    "Ang": ("m", 1e-10)
}
_unit_prefix = {
    "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12,
    "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e18
}

def convert_num_with_unit(s):
    """Return a number scaled to the standard unit or just a trimmed string"""
    words = s.split()
    if len(words) == 2:
        try:
            num, unit = float(words[0]), words[1]

            # Scale the number to the standard unit (in future)
            if unit in (_std_unit):
                return num
            else:
                print("Nonstandard unit: " + unit)
        except:
            pass
    return s.strip()
