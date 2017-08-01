import copy
import ruamel_yaml as yaml
from cryomem.common.numstr import convert_num_with_unit

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

    def dump_config(self, **kwargs):
        ascomments = kwargs.get("ascomments", False)
        s = yaml.dump(self.content, default_flow_style=False)
        if ascomments:
            s = '# ' + "# ".join(s.splitlines(True))  # comment form
        return s
