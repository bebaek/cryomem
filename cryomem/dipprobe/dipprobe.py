import time, sys
from .dipprobe_base import DipProbeBase

class DipProbe(DipProbeBase):
    """Main application methods based on DipProbeBase"""
    def log(self, **kwargs):
        """Log measured device parameters"""
        # convert config of this sequence properly
        exception = ()
        seq_param = self.parse_config(self.config["sequence"]["log"], exception=exception)
        print(seq_param)

        # list of device property names to read
        v = seq_param["read"]

        # Measurement loop
        tick = -1
        try:
            while tick < seq_param["duration"]:
                val = self.get_dev_val(v)
                #print(val)
                self.append_data(val, show=True)
                if tick == -1:       # first data point
                    tick0 = val[0]
                tick = val[0] - tick0
                print(tick, seq_param["duration"])
                time.sleep(seq_param["delay"])
        except KeyboardInterrupt:
            s = input("\nSave data before exit? (y/[n]) ")
            if s.lower() == "y":
                self.save_data(filename=seq_param["datafile_name"])
            else:
                print("Discarding data.")
            sys.exit()

        self.save_data(filename=seq_param["datafile_name"])
