import copy
import ruamel_yaml as yaml

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

def parse_config(config, **kwargs):
    """Return a copy of config with some strings converted"""
    result = copy.deepcopy(config)

    # Recursively reduce down to basic element
    if type(result) is list:
        for k, config2 in enumerate(result):
            result[k] = parse_config(config2, **kwargs)
    elif type(result) is dict:
        for key in result:
            result[key] = parse_config(result[key], **kwargs)
    #elif isnumstr(result):
    #    # Try to convert a number string to int or float
    #    result = numstr2num(result)
    elif type(result) is str:
        # Try to convert a number with a unit to a scaled int or float
        result = convert_num_with_unit(result)

    return result

class Config:
    def __init__(self, **kwargs):
        pass

    def load_config(self, **kwargs):
        # Sources of config parameters: argument or file
        if "parameters" in kwargs:
            rawconfig = kwargs["parameters"]
        elif "file" in kwargs:
            with open(kwargs["file"], "r") as f:
                rawconfig = yaml.load(f)

        self.content = parse_config(rawconfig)
        return self.content

    def save_config(self, configfile):
        with open(configfile, "w") as f:
            yaml.dump(self.content, f, default_flow_style=False)

    def dump_config(self):
        return yaml.dump(self.content, default_flow_style=False)
