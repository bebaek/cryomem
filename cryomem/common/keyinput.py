"""Cross-platform keyin processor"""
#from contextlib import contextmanager
import platform
_platform = platform.system()
if _platform == "Linux":
    import select, termios, sys, tty

    class _KeyInput:
        """Nonblocking key input processor."""
        def __init__(self):
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

        def getch(self):
            """Return the key if pressed or None."""
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                return sys.stdin.read(1)
            else:
                return None

        def close(self):
            """Restore terminal setting."""
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

elif _platform == "Windows":
    from msvcrt import kbhit, getch

    class _KeyInput:
        """Nonblocking key input processor."""
        def getch(self):
            """Return the key if pressed or None."""
            if kbhit():
                return getch().decode()
            else:
                return None

        def close(self):
            return

class KeyInput:
    """Class for context managing _KeyInput."""
    def __enter__(self):
        self._keyin = _KeyInput()
        return self._keyin

    def __exit__(self, *args):
        self._keyin.close()

#@contextmanager
#def key_press():
#    keypr = _KeyInput()
#    yield keypr
#    keypr.close()

def test1():
    import time

    with key_press() as keyin:
        time.sleep(3)
        print("key:", keyin.getch())
        someerr

def test2():
    import time

    with KeyInput() as keyin:
        time.sleep(3)
        print("key:", keyin.getch())
        #someerr

if __name__ == "__main__":
    test2()
