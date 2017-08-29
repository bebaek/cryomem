import threading, queue
import matplotlib as mpl
mpl.use("tkagg")
import matplotlib.pyplot as plt

class PlotThread:
    """Use an own thread for nonblocking plotting."""
    def __init__(self, **kwargs):
        """Init with keyword arguments for plotting parameters."""
        self.xlabel = kwargs.get("xlabel", "x")
        self.ylabel = kwargs.get("ylabel", "y")

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
        mpl.rcParams["toolbar"] = "None"    # diable toolbar
        self.fig = plt.figure()
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
