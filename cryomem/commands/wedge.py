"""Call methods in fab/wedge.py from command line"""
from ..fab import wedge
from ..common.parse_cmd_argv import parse_cmd_argv
import sys

# Register user commands
_cmdlist = ["fit", "get_rate", "get_thickness"]

def main(argv):
    # process arguments
    if len(argv) < 2:
        print(wedge.__doc__)
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(0)

    cmd = argv[1]
    parsed_args = parse_cmd_argv(argv[2:])
    if cmd not in _cmdlist:
        print(wedge.__doc__)
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(0)

    # Call the corresponding function (command)
    #globals()[cmd](*args, **kwargs)
    w = wedge.Wedge()
    try:
        if type(parsed_args) is tuple:
            # list arguments are present
            print(getattr(w, cmd)(*parsed_args[0], **parsed_args[1]))
        else:
            # only keyword arguments are present
            print(getattr(w, cmd)(**parsed_args))
    except KeyError as err:
        print("KeyError: {}".format(err))
        print(getattr(w, cmd).__doc__)
