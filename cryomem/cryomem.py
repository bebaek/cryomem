"""
Main user command line executable. Just runs subpackage main commands.
"""

import sys
from importlib import import_module
from os.path import abspath, dirname, splitext, split
from glob import glob
from .common.parse_cmd_argv import parse_cmd_argv

# Define commands for command line run
cmd_params = {
    "fit":      {"module": "cryomem.analysis.fit_datafile", "function":
                "fit_datafile"},
    "conv_tdsbin": {"module": "cryomem.common.datafile", "function":
                "conv_tdsbin"},

    "wedge":    {"module": "cryomem.fab.wedge", "class": "Wedge",
                "methods": ["fit", "get_rate", "plot", "get_thickness"]},
}

def call(argv):
    """"Import and call a module as a subcommand. Deprecated."""
    mod = import_module("cryomem.commands.{}".format(argv[1]))
    getattr(mod, "main")(argv[1:])

def call2(argv):
    """Call a command defined by cmd_params above."""
    command = argv[1]
    if command in cmd_params:
        mod = import_module(cmd_params[command]["module"])
    else:
        print("Commands:", [key for key in cmd_params])
        sys.exit(1)

    # case 1: call function (command)
    if "function" in cmd_params[command]:
        runner = getattr(mod, cmd_params[command]["function"])

        # show usage and exit
        if argv[2] == "--help":
            print(runner.__doc__)
            sys.exit(1)

        # Run!
        parsed_args = parse_cmd_argv(argv[2:])
        if type(parsed_args) is tuple:      # list and keyword arguments
            res = runner(*parsed_args[0], **parsed_args[1])
            if "q" not in parsed_args[1]:   # --q: quiet option
                print(res)
        else:                               # only keyword arguments
            res = runner(**parsed_args)
            if "q" not in parsed_args:
                print(res)

    # case 2: call method (subcommand) in a class (command)
    elif "class" in cmd_params[command]:
        inst    = getattr(mod, cmd_params[command]["class"])()
        methods = cmd_params[command]["methods"]

        # show available methods and exit
        if argv[2] == "--help":
            print("Commands: {}\n".format(methods))
            sys.exit(1)

        # deal with method
        if argv[2] in methods:
            runner = getattr(inst, argv[2])    # "subcommand"
            if argv[3] == "--help":
                print(runner.__doc__)
                sys.exit(1)
            else:
                # Run!
                parsed_args = parse_cmd_argv(argv[3:])
                if type(parsed_args) is tuple:      # list and keyword arguments
                    res = runner(*parsed_args[0], **parsed_args[1])
                    if "q" not in parsed_args[1]:
                        print(res)
                else:                               # only keyword arguments
                    res = runner(**parsed_args)
                    if "q" not in parsed_args:
                        print(res)

def show_help():
    print('\n'
          'Usage: cryomem\n'
          '       cryomem <command> [<subcommand> --<option1> <value1> <value2> ...]\n'
          '\n'
          'Examples (\'[...]\' means optional):\n'
          '       cryomem wedge --help                : Show help for wedge command\n'
          '       cryomem wedge get_thickness --help  : Show help for get_thickness\n'
          'Common options:\n'
          '       --q: Do not print the final result.\n'
      )
    #cmdpath = abspath(dirname(abspath(__file__))+"/commands")
    #cmdlist = [splitext(split(name)[-1])[0] for name in glob(cmdpath + '/*.py')]
    #cmdlist.remove("__init__")
    #print("Commands: {}\n".format(cmdlist))
    print("Commands:", [key for key in cmd_params])

def main():
    """Entrypoint"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    if sys.argv[1] == "--help":
        show_help()
        sys.exit(0)

    call2(sys.argv)

if __name__ == '__main__':
    main()
