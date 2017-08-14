"""Call methods in dipprobe/dipprobe.py from command line"""
from ..dipprobe import dipprobe
from ..common.parse_cmd_argv import parse_cmd_argv
import sys

# Register user commands
_cmdlist = ['log']

def main(argv):
    # process arguments
    if len(argv) < 2:
        print(dipprobe.__doc__)
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(0)

    cmd = argv[1]
    parsed_args = parse_cmd_argv(argv[2:])
    if cmd not in _cmdlist:
        print(dipprobe.__doc__)
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(0)

    # Call the corresponding function (command)
    probe = dipprobe.DipProbe()
    try:
        if type(parsed_args) is tuple:
            # list arguments are present
            probe.load_config(file=parsed_args[1]["config"])
            print(getattr(probe, cmd)(*parsed_args[0], **parsed_args[1]))
        else:
            # only keyword arguments are present
            probe.load_config(file=parsed_args["config"])
            print(getattr(probe, cmd)(**parsed_args))
    except KeyError as err:
        print("KeyError: {}".format(err))
        print(getattr(probe, cmd).__doc__)
