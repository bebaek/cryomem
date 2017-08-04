"""
Main user command line executable. Just runs subpackage main commands.
"""

import sys
from importlib import import_module

def call(cmd, argv):
    """"Import and call subcommand."""
    mod = import_module("cryomem.{}.{}".format(cmd, cmd))
    getattr(mod, "main")(argv)

def main():
    """Entrypoint"""
    if len(sys.argv) < 2:
        print('\n'
              'Usage: cryomem\n'
              '       cryomem <command> [<subcommand> --<option1> <value1> <value2> ...]\n'
              '\n'
              'Examples (\'[...]\' means optional):\n'
              '       cryomem fab           : Show help for fab command\n'
              '       cryomem fab wedge     : Show help for fab/wedge subcommand\n'
              '\n'
          )
        sys.exit(0)
    cmd = sys.argv[1]
    call(cmd, sys.argv[1:])

if __name__ == '__main__':
    main()
