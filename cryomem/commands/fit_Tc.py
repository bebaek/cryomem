"""Call methods in a module from command line."""
# Modify the following 3 lines for new command module
from ..analysis import fit_Tc_datafile as target_module
_cmdlist = ["run"]
_target_class = "Tc_datafile"
# End of customization

from ..common.parse_cmd_argv import parse_cmd_argv
import sys

def main(argv):
    # process arguments
    if len(argv) < 2 or "--help" == argv[1]:
        print(target_module.__doc__)
        print("Commands: {}\n".format(_cmdlist))
        sys.exit(1)

    cmd = argv[1]
    target_instance = getattr(target_module, _target_class)()
    parsed_args = parse_cmd_argv(argv[2:])
    if cmd not in _cmdlist:
        print("Command not found:", cmd)
        sys.exit(1)

    if "--help" in argv[2:]:
        print(getattr(target_instance, cmd).__doc__)
        sys.exit(1)

    # Call the corresponding function (command)
    """
    try:
        if type(parsed_args) is tuple:
            # list arguments are present
            print(getattr(target_instance, cmd)(*parsed_args[0], **parsed_args[1]))
        else:
            # only keyword arguments are present
            print(getattr(target_instance, cmd)(**parsed_args))
    except KeyError as err:
        print("KeyError: {}".format(err))
        print(getattr(target_instance, cmd).__doc__)
    """
    if type(parsed_args) is tuple:
        # list arguments are present
        print(getattr(target_instance, cmd)(*parsed_args[0], **parsed_args[1]))
    else:
        # only keyword arguments are present
        print(getattr(target_instance, cmd)(**parsed_args))
