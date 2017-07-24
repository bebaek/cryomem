"""
Provide base class including various interface for user instruments.
"""

def isGPIB(s):
    if len(s) > 4:                  # check if it's GPIB
        if s[:4].upper() == "GPIB":
            return True
    return False

def isDLL(s):
    pass

class Interface:
    """Dynamically define interface methods/parameters.

    To be inherited by each instrument class.
    """
    def __init__(self, iface_str):
        """Interpret interface string and return dictionary holding created
        interface object (with address included).
        """
        # GPIB
        if isGPIB(iface_str):              # check if GPIB is called ("gpibN")
            unit = 0                       # normally 0 (single card)
            addr = int(iface_str[4:])
            if addr >= 0 and addr < 31:
                #try:
                    # Instantiate GPIB and assign user methods
                    from .visa import GPIB
                    # debug
                    #test = GPIB(unit, addr)
                    #test.write("*IDN?")
                    #print(test.read())
                    self._set_interface(GPIB(unit, addr))
                #except:
                #    print("Interface failure: GPIB, " + iface_str)

        # DLL interface driver
        elif isDLL(iface_str):
            pass

        # Fake interface for debugging
        elif isfake(iface_str):
            self._set_interface(Fake())

        # Invalid interface
        else:
            print("Invalid interface.")

    def _set_interface(self, iface_obj):
        self._iface = iface_obj
        self.write = self._iface.write
        self.read = self._iface.read

def isfake(s):
    if s.lower() == "fake":
        return True
    else:
        return False

class Fake:
    """Fake interface for debugging"""
    def __init__(self):
        self.nw = 0
        self.nr = 0
        print("Fake interface created.")

    def write(self, msg):
        self.nw += 1
        return msg

    def read(self):
        self.nr += 1
        return str(self.nr + self.nw)
