"""
Metadata handler.
Metadata contain experimental conditions, data format, etc.
Structure: YAML.
"""
import copy
import ruamel_yaml as yaml
from .numstr import numstr2num
import collections
from io import StringIO, TextIOWrapper

def parse_md(md, **kwargs):
    """Return a copy of metadata with some strings converted"""
    result = copy.deepcopy(md)

    # Recursively reduce down to basic element
    if type(result) is list:
        for k, md2 in enumerate(result):
            result[k] = parse_md(md2, **kwargs)
    elif type(result) is dict:
        for key in result:
            result[key] = parse_md(result[key], **kwargs)
    #elif isnumstr(result):
    #    # Try to convert a number string to int or float
    #    result = numstr2num(result)
    elif type(result) is str:
        # Try to convert a number with a unit to a scaled int or float
        result = numstr2num(result)

    return result

def load_md(src):
    """Load metadata in YAML from a source.

    Arguments:
        src: dict-like (data), string (filename), or file-like
    """
    # Sources of config parameters: argument or file
    #if "parameters" in kwargs:
    #    rawconfig = kwargs["parameters"]
    #elif "fname" in kwargs:
    #    with open(kwargs["fname"], "r") as f:
    #        rawconfig = yaml.load(f)
    #elif "fobj" in kwargs:
    #    rawconfig = yaml.load(kwargs["fobj"])

    if isinstance(src, collections.Mapping):            # dict or yaml is given
        rawconfig = src
    elif isinstance(src, str):                              # filename is given
        with open(src, "r") as f:
            rawconfig = yaml.load(f)
    elif (isinstance(src, TextIOWrapper) or
         isinstance(src, StringIO)):    # file is given
        rawconfig = yaml.load(src)

    return parse_md(rawconfig)

def save_md(dest, md):
    """Save metadata to a file-like.

    Arguments:
        dest: file-like
        md: dict-like
    """
    if isinstance(dest, str):                           # filename is given
        with open(dest, "w") as f:
            yaml.dump(md, f, default_flow_style=False)
    elif (isinstance(dest, TextIOWrapper) or
         isinstance(dest, StringIO)):                 # file-like is given
        yaml.dump(md, dest, default_flow_style=False)

def dump_md(md, **kwargs):
    """Convert metadata content to a yaml string."""
    ascomments = kwargs.get("ascomments", False)
    s = yaml.dump(md, default_flow_style=False)
    if ascomments:
        s = '# ' + "# ".join(s.splitlines(True))  # comment form
    return s
