import multiprocessing as mp
import queue
import matplotlib as mpl
mpl.use("tkagg")
import matplotlib.pyplot as plt
import time

#def _f_proc(q, **kwargs):
#    """Process target function"""
#    _Plotter(q, **kwargs)

class _Plotter(mp.Process):
    """Core plotting object. Controlled by queue message."""
    def __init__(self, q_in, q_out, **kwargs):
        """Init with keyword arguments for plotting parameters."""
        super().__init__()
        self.q_in = q_in
        self.q_out = q_out
        self.kwargs = kwargs

    def run(self):
        """Loop"""
        self._setup_plot(**self.kwargs)
        while True:
            if self.q_in.empty():
                plt.pause(0.1)
            else:
                msg = self.q_in.get()
                if msg[0] == "exit":
                    plt.close(self.fig)
                    break
                else:
                    self._process_msg(msg)

    def _process_msg(self, msg):
        """Process the argument tuple, of which 1st element is the command."""
        if msg[0] == "plot":
            self._update_plot(msg[1:])
        elif msg[0] == "get_wloc":
            self.q_out.put(self._get_wloc())
        else:
            print("Invalid queue message:", msg)

    def _setup_plot(self, **kwargs):
        """Create figure."""
        self.xlabel = kwargs.pop("xlabel", "x")
        self.ylabel = kwargs.pop("ylabel", "y")
        self.title = kwargs.pop("title", "Plot")
        self.plotparams = kwargs

        self.plotstyle = "o-"
        mpl.rcParams["toolbar"] = "None"            # disable toolbar
        self.fig = plt.figure()
        self._set_wloc()                             # place window
        self._set_title(self.title)           # set title
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        plt.pause(0.1)

    def _update_plot(self, msg):
        x, y = msg[0], msg[1]
        self.ax.cla()
        self.line = self.ax.plot(x, y, self.plotstyle)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        plt.tight_layout()
        plt.pause(0.1)

    def _set_title(self, title):
        cfm = plt.get_current_fig_manager()
        cfm.set_window_title(title)

    def _set_wloc(self):
        cfm = plt.get_current_fig_manager()
        if "wx" in self.plotparams and "wy" in self.plotparams:
            cfm.window.geometry("+{}+{}".format(self.plotparams["wx"], self.plotparams["wy"]))

    def _get_wloc(self):
        cfm = plt.get_current_fig_manager()
        return tuple(map(int, cfm.window.geometry().split("+")[1:]))

class PlotProc:
    """Spawn and manage plotting process."""
    def __init__(self, **kwargs):
        """Init with keyword arguments for plotting parameters."""
        self.q_in = mp.Queue()
        self.q_out = mp.Queue()
        #self.proc = mp.Process(target=_Plotter, args=(self.q,), kwargs=kwargs)
        self.proc = _Plotter(self.q_out, self.q_in, **kwargs)
        #self.proc = _Plotter()
        self.proc.start()

    def plot(self, x, y):
        """Update plot with arguments x, y."""
        self.q_out.put(("plot", x, y))

    def close(self):
        """Finish plotting thread."""
        self.q_out.put(("exit",))
        self.proc.join()

    def get_wloc(self):
        self.q_out.put(("get_wloc",))
        return self.q_in.get()

def demo():
    import numpy as np
    import time

    x = np.arange(10)
    y = np.arange(10)

    pp = PlotProc()
    for k, _ in enumerate(x):
        print(k, x[:(k+1)], y[:(k+1)])
        pp.plot(x[:(k+1)], y[:(k+1)])
        time.sleep(1)
    pp.close()
    print("demo() finishing.")

if __name__ == "__main__":
    demo()
