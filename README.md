# Cryomem
Python library/command utilities for Cryomem research project. The package includes test/measurment control code as well as useful analysis code. Routine utility functions/methods are also executable directly from the command line. More involving analyses can be done by importing from a script/Jupyter notebook.

## Installation
Go to the root of the repository where setup.py is located, then run
```
pip install -e .
```

To uninstall, run
```
pip uninstall cryomem
```

You may need to install required packages including numpy, matplotlib, scipy, pandas. In miniconda system, run ```conda install <package>``` first and then, if not available from conda, ```pip search <package>``` then ```pip install <package>```.

To upgrade the version, cd to the new source and run
```
pip install -e . -U
```

## Usage
### Command line
Although the package is basically a library, some functions/methods can be run from the command line. This is the recommended usage for routine test/measurement works.

Display help message:
```
> cryomem [--help]
```

Display help message for \<command>
```
> cryomem <command> --help
```

General form. \<parameters> is a list of arguments followed by keyword arguments. A keyword argument is given by ```--<key> <value> [more values]```.
```
> cryomem <command> [<parameters>]
```

### Python script
Load the code and prompt help as needed:
```
from cryomem.dipprobe.dipprobe import DipProbe
probe = DipProbe()
probe.help()
```

Example with a config file:
```
probe.load_config(file="log_R_T.yaml")
probe.log()
```

To forgo a config file:
```
parameters = {
  "device": {
    "R_thermometer": {
      "name": "Thermometer resistance",
      "instrument": "KT2001",
      "interface": "gpib11",
      "read_method": "read_R4W",
      "raw_unit": "1 Ohm",
      "sensor": "lakeshore_X104724",
      "unit": "K"
    },
    "Rac_device": {
      "name": "Device lock-in amplitude",
      "instrument": "SR830",
      "interface": "gpib9",
      "read_method": "get_r",
      "unit": "V"
    },
    "t": {
      "name": "Time",
      "read_module": "time",
      "read_method": "time"
    }
  },
  "sequence": {
    "log": {
      "read": ["t", "R_thermometer", "Rac_device"],
      "delay": "5 s",
      "duration": "20 s",
      "datafile_name": "test sample 1.txt",
      "datafile_increment": "No"
    }
  }
}
probe.load_config(parameters=parameters)
probe.log()
```

### Config file
Subpackage dipprobe has been written to use config files extensively for test/measurement settings. Measurement instruments, target parameters, DAQ sequence parameters can be specified in a YAML file to achieve both flexibility and efficiency. See ```cryomem/test/dipprobe/testconfig.yaml``` for an example.

A config file is loaded from the command line by a parameter

```
--config <config file>
```

or from a python script by calling a method:

```
<obj>.load_config(file=<config file>)
```

### Implemented functions
- dipprobe DAQ
  - Instrument control: GPIB, RS232, USB dll.
  - Superconducting R-T
  - JJ B-I-V
- YAML configuration file management
- Zip-format datafile management
- Fit:
  - Superconducting R-T
  - JJ I-V: RSJ, AH
  - JJ B-Ic: Airy pattern
  - Magnetic JJ d-Ic (clean limit)

## Development

### Structure
Subpackages are intended to be independent from each other except "common" subpackage. Example subpackages:
- common: shared utility code
- data: static data requiring frequent access (ex: thickness calibration)
- analysis: data analysis including fit.
- dipprobe: new dipprobe control code
- fab: fab-related code (ex. thickness calibration)
- cmtools: old dipprobe control code

### Command line execution
The entrypoint is "cryomem.py". The run commands are registered around its beginning in a dictionary "cmd_params".
