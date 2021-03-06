"""Provide base class for common instrument interfaces."""
import visa


def isGPIB(s):
    if len(s) > 4:                  # check if it's GPIB
        if s[:4].upper() == "GPIB":
            return True
    return False


def isserial(s):
    if len(s) > 3:                  # check if serial ("COM1")
        if s[:3].upper() == "COM":
            return True
    return False


def isDLL(s):
    return False


class Interface:
    """Dynamically define interface methods/parameters.

    To be inherited by each instrument class.
    """
    def __init__(self, interface="gpib0"):
        """Interpret interface string and return dictionary holding created
        interface object (with address included).
        """
        # GPIB (gpibN)
        if isGPIB(interface):
            unit = 0                       # normally 0 (single card)
            addr = int(interface[4:])
            rm = visa.ResourceManager()
            rm.list_resources()
            self._set_interface(
                rm.open_resource("GPIB{}::{}::INSTR".format(unit, addr)))

        # serial (comN)
        elif isserial(interface):
            rm = visa.ResourceManager()
            rm.list_resources()
            self._set_interface(rm.open_resource(interface))

        # DLL interface driver
        elif isDLL(interface):
            pass

        ## Fake interface for debugging
        #elif isfake(interface):
        #    self._set_interface(Fake())

        # general visa interface
        else:
            rm = visa.ResourceManager()
            rm.list_resources()
            self._set_interface(rm.open_resource(interface))

    def _set_interface(self, iface_obj):
        """Register essential methods."""
        self._iface = iface_obj
        self.write = self._iface.write
        self.read = self._iface.read
        self.query = self._iface.query
        self.query_binary_values = self._iface.query_binary_values
        self.clear = self._iface.clear	# clear buffer
        self.read_raw = self._iface.read_raw
        self.timeout = self._iface.timeout
#def isfake(s):
#    if s.lower() == "fake":
#        return True
#    else:
#        return False
#
#class Fake:
#    """Fake interface for debugging"""
#    def __init__(self):
#        self.nw = 0
#        self.nr = 0
#        print("Fake interface created.")
#
#    def write(self, msg):
#        self.nw += 1
#        return msg
#
#    def read(self):
#        self.nr += 1
#        return str(self.nr + self.nw)
