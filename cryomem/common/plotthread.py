import threading, queue
import matplotlib as mpl
mpl.use("tkagg")
import matplotlib.pyplot as plt

class PlotThread:
    """Use an own thread for nonblocking plotting."""
    def __init__(self, **kwargs):
        """Init with keyword arguments for plotting parameters."""
        self.plotparams = kwargs
        self.xlabel = kwargs.get("xlabel", "x")
        self.ylabel = kwargs.get("ylabel", "y")
        self.title = kwargs.get("title", "Plot")

        self.q = queue.Queue()
        self.thr = threading.Thread(target=self.run, args=(self.q,))
        self.thr.start()

    def run(self, q):
        """Main loop and thread target."""
        self._setup_plot()
        while True:
            msg = q.get()
            if msg == "exit":
                plt.close(self.fig)
                break
            else:
                self._update_plot(msg)

    def _setup_plot(self):
        self.plotstyle = "o-"
        mpl.rcParams["toolbar"] = "None"            # disable toolbar
        self.fig = plt.figure()
        self.set_wloc()                             # place window
        self.set_title(self.title)           # set title
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        plt.pause(0.001)

    def _update_plot(self, msg):
        x, y = msg[0], msg[1]
        self.ax.cla()
        self.line = self.ax.plot(x, y, self.plotstyle)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        plt.tight_layout()
        plt.pause(0.001)

    def plot(self, x, y):
        """Update plot with arguments x, y."""
        self.q.put((x,y))

    def close(self):
        """Finish plotting thread."""
        self.q.put("exit")
        self.thr.join()

    def set_title(self, title):
        cfm = plt.get_current_fig_manager()
        cfm.set_window_title(title)

    def set_wloc(self):
        cfm = plt.get_current_fig_manager()
        if "wx" in self.plotparams and "wy" in self.plotparams:
            cfm.window.geometry("+{}+{}".format(self.plotparams["wx"], self.plotparams["wy"]))

    def get_wloc(self):
        cfm = plt.get_current_fig_manager()
        return map(int, cfm.window.geometry().split("+")[1:])

def demo():
    import numpy as np
    import time

    x = np.arange(10)
    y = np.arange(10)

    pt = PlotThread()
    for k, _ in enumerate(x):
        print(k, x[:(k+1)], y[:(k+1)])
        pt.plot(x[:(k+1)], y[:(k+1)])
        time.sleep(1)
    pt.close()

if __name__ == "__main__":
    demo()
