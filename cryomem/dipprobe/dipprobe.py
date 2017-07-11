import time

class DipProbe(DipProbeBase):
    """Main application methods based on DipProbeBase"""
    def log(self, **kwargs):
        """Log measured device parameters"""
        sp = self.seq_param["log"]
        v = sp["read"]
        tick = 0
        try:
            while tick < sp["duration"]:
                val = self.get_dev_val(v)
                self.append_data(val, show=True)
                if tick == 0:       # first data point
                    abs_tick = val[0]
                tick = val[0] - abs_tick
                time.delay(sp["delay"])
        except KeyboardInterrupt:
            s = input("Save data before exit? (y/n) ")
            if s.lowercase = "y":
                self.save_data()
        self.save_data()
