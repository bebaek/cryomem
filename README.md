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
  device: {
    R_device1: {
      name: "Device 1 resistance",
      instrument: "SR830",
      interface: "GPIB5",
      read_method: "get_r",
      unit: "0.01 Ohm"
    },
    R_thermometer: {
      name: "Thermometer resistance",
      instrument: "KT2001",
      interface: "GPIB6",
      read_method: "fetch",
      raw_unit: "1 Ohm",
      sensor: "lakeshore_X104724",
      unit: "K"
    },
    T: {
      name: "Temperature",
      input_parameter: "R_thermometer",
      read_module: "cryomem.cal.DT670",
      read_method: "R_to_T",
      read_args: {
        input_parameter,
        cal_file: "cal_DT-670_dipprobe.txt"
      }
    },
    t: {
      name: "Time",
      read_module: "time"
      read_method: "time"
    }
  },
  sequence: {
    log: {
      read: {"t", "R_device1", "R_thermometer", "T"},
      delay: "10 s",
      duration: "1800 s",
      datafile_format: "xlsx",  
      datafile_postfix: "sample 1"      
    }
  }
}
probe.load_config(parameters=parameters)
probe.log(datafile_postfix="sample 2")
```
