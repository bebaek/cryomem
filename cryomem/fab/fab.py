from importlib import import_module
import sys

_cmdlist = ["wedge2"]

def _call(cmd, argv):
    """"Import and call subcommand."""
    pkg = "cryomem.fab"
    mod = import_module("{}.{}".format(pkg, cmd))
    getattr(mod, "main")(argv)

def main(argv):
    """Entrypoint"""
    if len(argv) < 2:
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(0)
    cmd = argv[1]
    if cmd in _cmdlist:
        _call(cmd, argv[1:])

