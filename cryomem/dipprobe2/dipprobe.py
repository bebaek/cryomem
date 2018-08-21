"""Measurement control module for Dip Probe"""
import time
import sys
from .dipprobe_base import DipProbeBase
from ..common.parse_cmd_argv import parse_cmd_argv
from ..common.keyinput import KeyInput
from ..common.build_sweeprange import build_sweeprange

class DipProbe(DipProbeBase):
    """Main application methods based on DipProbeBase"""
    def log(self, *args, **kwargs):
        """Log measured device parameters"""
        # load config if not present
        if not hasattr(self.config, "content"):
            self.load_config(file=kwargs["config"])

        # Pick out sequence config and also override if applicable
        seq_param = self.config.content["sequence"]["log"]
        for key in kwargs:
            seq_param[key] = kwargs[key]    # can override config with kwargs
        print("Sequence parameters:")
        print("  Arguments:", args)
        print("  Keyword arguments:", seq_param)

        # Set up key input monitoring
        print("Hit q to finish cleanly.")
        with KeyInput() as keyin:
            time.sleep(3)
            if keyin.getch() == "q": return 1

            # list of device property names to read
            v = seq_param["read"]
            val = self.get_dev_val(v)   # dummy read

            # Measurement loop
            tick = -1
            while tick < seq_param["duration"]:
                val = self.get_dev_val(v)
                self.append_data(val, tmpfile=True, show=False)
                self.plot_data(*seq_param["plot_prop"])
                if tick == -1:       # first data point
                    tick0 = val[0]
                tick = val[0] - tick0
                print(tick, seq_param["duration"], val.values)
                time.sleep(seq_param["delay"])

                # Check finish request by user key input
                if keyin.getch() == "q":
                    s = input("\nSave data before exit? (y/[n]) ")
                    if s.lower() == "y":
                        self.save_data(filename=seq_param["datafile_name"],
                                       datafile_increment=seq_param["datafile_increment"])
                    else:
                        print("Discarding data.")
                    self.close_plot()
                    return tick

        # Finish with time out
        self.save_data(filename=seq_param["datafile_name"],
                       datafile_increment=seq_param["datafile_increment"])
        self.close_plot()
        return tick

    def set_device(self, prop="T_set", val=0, **kwargs):
        """Set device property value.

        Arguments:
            prop -- String. Device property name.
            val -- Numeric. Value to write.
        Keyword arguments:
            config -- String. Config file name.
            [val1, val2, step, delay]
        """
        args = [prop, val]

        # load config if not already present
        if not hasattr(self.config, "content"):
            self.load_config(file=kwargs["config"])

        # Gather sequence parameters
        device_param = self.config.content["device"][prop]
        seq_param = self.config.content["sequence"]["set_device"]
        for key in kwargs:
            seq_param[key] = kwargs[key]    # can override config with kwargs
        seq_param["ramp"] = True if "val2" in kwargs else False
        print("Sequence parameters:")
        print("  Arguments:", args)
        print("  Keyword arguments:", seq_param)

        # list of device property names to write to
        if not seq_param["ramp"]:
            val_actual = self.set_dev_val(prop, val)
        else:
            step = seq_param.get("step", device_param["step"])
            delay = seq_param.get("delay", device_param["delay"])
            val_actual = self.ramp_dev_val(prop, seq_param["val1"],
                                           seq_param["val2"],
                                           step=step, delay=delay)
        return val_actual

    def sweep(self, **kwargs):
        """Sweep and measure device parameters.
        
        Arguments:
            sweep property name
        Keyword arguments:
            sweep -- sweep property
            range -- sweep value range. Format: start step stop [step stop
            ...]
            read -- measurement properties
        """
        # load config if not present
        if not hasattr(self.config, "content"):
            self.load_config(file=kwargs["config"])

        # Pick out sequence config and also override if applicable
        seq_param = self.config.content["sequence"]["sweep"]
        for key in kwargs:
            seq_param[key] = kwargs[key]    # can override config with kwargs
        print("Sequence parameters:")
        #print("  Arguments:", args)
        print("  Keyword arguments:", seq_param)

        # Set up key input monitoring
        print("Hit q to finish cleanly.")
        with KeyInput() as keyin:
            time.sleep(3)
            if keyin.getch() == "q": return 1

            # Get main parameters: device property names, values
            sweepprop = seq_param["sweep"][0]
            sweeprange = build_sweeprange(seq_param["range"])
            v = seq_param["read"]

            # Pre-loop operation
            #self.init_prop(seq_param['init'])
            val = self.get_dev_val(v)   # dummy read

            # Measurement loop
            tick0 = time.time()
            #while tick < seq_param["duration"]:
            for sweepval in sweeprange:
                sweepval2 = self.set_dev_val(sweepprop, sweepval)  # set
                time.sleep(seq_param["delay"])                      # delay
                val = self.get_dev_val(v)                           # measure

                val[sweepprop] = sweepval2
                self.append_data(val, tmpfile=True, show=False)
                #self.plot_data(*seq_param["plot_prop"])
                #if tick == -1:       # first data point
                #    tick0 = val[0]
                tick = time.time() - tick0
                print(tick, val[sweepprop])
                #time.sleep(seq_param["delay"])

                # Check finish request by user key input
                if keyin.getch() == "q":
                    s = input("\nSave data before exit? (y/[n]) ")
                    if s.lower() == "y":
                        self.save_data(filename=seq_param["datafile_name"],
                                       datafile_increment=seq_param["datafile_increment"])
                    else:
                        print("Discarding data.")
                    #self.close_plot()
                    return tick

        # Finish with time out
        self.save_data(filename=seq_param["datafile_name"],
                       datafile_increment=seq_param["datafile_increment"])
        #self.close_plot()
        return tick

def test(argv):
    """Call a method given by the subcommand and optional parameter arguments."""
    cmd = argv[1]
    parsed_args = parse_cmd_argv(argv[2:])

    probe = DipProbe()
    probe.load_config(file="dipprobe.yaml")
    #probe.log()
    if type(parsed_args) is tuple:
        print(getattr(probe, cmd)(*parsed_args[0], **parsed_args[1]))
    else:
        print(getattr(probe, cmd)(**parsed_args))

if __name__ == '__main__':
    test(sys.argv)
