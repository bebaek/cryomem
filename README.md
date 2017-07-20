# Cryomem
Code for dc transport measurements.

## Installation
Go to the root of the repository where setup.py is located, then run
```
pip install -e .
```

To uninstall, run
```
pip uninstall cryomem
```

## Usage
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
