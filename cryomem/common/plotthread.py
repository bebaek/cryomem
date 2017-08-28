import threading, queue
import matplotlib.pyplot as plt

class PlotThread:
    """Use an own thread for nonblocking plotting."""
    def __init__(self):
        """Init with an argument queue."""
        self.q = queue.Queue()
        self.thr = threading.Thread(target=self.run, args=(self.q,))
        self.thr.start()

    def run(self, q):
        """Main loop and thread target."""
        self._setup_plot()
        while True:
            msg = q.get()
            if msg == "exit":
                break
            else:
                self._update_plot(msg)

    def plot(self, x, y):
        self.q.put((x,y))

    def _setup_plot(self):
        self.plotstyle = "o-"
        fig = plt.figure()
        self.ax = fig.add_subplot(111)

    def _update_plot(self, msg):
        x, y = msg[0], msg[1]
        self.ax.cla()
        self.line = self.ax.plot(x, y, self.plotstyle)
        plt.pause(0.05)

    def close(self):
        self.q.put("exit")
        self.thr.join()

if __name__ == "__main__":
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
