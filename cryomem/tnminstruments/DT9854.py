"""
Data Translation DAQ (.net wrapper)
"""

import sys
try:
    import clr
    OLlocation = r'C:\Program Files (x86)\Data Translation\DotNet\OLClassLib\Framework 2.0 Assemblies'
    sys.path.append(OLlocation)
    clr.AddReference('OpenLayers.Base')
    import OpenLayers.Base as OL
    devMgr = OL.DeviceMgr.Get() # start device manager for DT DAQ
except NameError:
    print('Cannot load DT DAQ library.')

class DT9854:
    def __init__(self, **kwargs):
        resAd = 'DT9854-M(00)'
        self.dev = devMgr.GetDevice(resAd) # 1 device object for a given board
        self.AOutss = self.dev.AnalogOutputSubsystem(0)

        # configure device
        valid_AO = list(range(0,self.AOutss.SupportedChannels.Count))
        print('Valid V out channels: ', valid_AO)     # checkpoint
        self.AOutss.DataFlow = OL.DataFlow.SingleValue  # single value out mode
        self.AOutss.Config()                            # update device
        voltGains = self.AOutss.SupportedGains

    def set_vout(self, voltage, channel=-1):
        #print("Voltage:", voltage)
        self.AOutss.SetSingleValueAsVolts(channel, voltage)
    
if __name__ == '__main__':
    import sys,time

    dev = DT9854()
    if len(sys.argv) < 3:
        print('Usage: <script name> <V> <ch>')
    else:
        v, ch = int(sys.argv[1]), float(sys.argv[2])
    dev.set_vout(v, ch)
    time.sleep(1)

    # wave out
    #import numpy as np
    #while True:
        #v = -v
        #dev.set_vout(ch,v)
