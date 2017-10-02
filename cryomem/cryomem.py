"""
Main user command line executable. Just runs subpackage main commands.
"""

import sys
from importlib import import_module
from os.path import abspath, dirname, splitext, split
from glob import glob

def call(argv):
    """"Import and call subcommand."""
    mod = import_module("cryomem.commands.{}".format(argv[1]))
    getattr(mod, "main")(argv[1:])

def show_help():
    print('\n'
          'Usage: cryomem\n'
          '       cryomem <command> [<subcommand> --<option1> <value1> <value2> ...]\n'
          '\n'
          'Examples (\'[...]\' means optional):\n'
          '       cryomem wedge --help                : Show help for wedge command\n'
          '       cryomem wedge get_thickness --help  : Show help for get_thickness\n'
      )
    cmdpath = abspath(dirname(abspath(__file__))+"/commands")
    cmdlist = [splitext(split(name)[-1])[0] for name in glob(cmdpath + '/*.py')]
    print("Commands: {}\n".format(cmdlist))

def main():
    """Entrypoint"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    if sys.argv[1] == "--help":
        show_help()
        sys.exit(0)

    call(sys.argv)

if __name__ == '__main__':
    main()
