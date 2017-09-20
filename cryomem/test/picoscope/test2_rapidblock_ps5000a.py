import ps5000a_bb as ps5000a
import numpy as np
import matplotlib.pyplot as plt
import time

scope = ps5000a.PS5000a_bb()

# device info
msg = scope.getAllUnitInfo()
print(msg)

# prep scope
scope.setResolution('12')
scope.setChannel(channel="A", coupling="DC", VRange=0.1, VOffset=0.0, enabled=True, BWLimited=False, probeAttenuation=1.0)
sampl_intvl, durtn = 0.02/100, 0.02
interval, nsample, maxsample = scope.setSamplingInterval(sampl_intvl, durtn)
scope.setSimpleTrigger("A", threshold_V=0)

# rapid block setup
ncapt = 64
max_sampl_per_seg = scope.memorySegments(ncapt)
sampl_per_seg = 100
scope.setNoOfCaptures(ncapt)
#data = np.zeros((ncapt, sampl_per_seg), dtype=np.int16)

# run scope
t0 = time.time()
for k in range(100):
    scope.runBlock()
    scope.waitReady()
    data = scope.getDataRawBulk("A")[0]
    if k%10 == 0:
        print("Run number:", k)
t1 = time.time()
print('Duration: ', t1-t0)

# convert to voltage
v = np.empty((ncapt, sampl_per_seg))
for k in range(ncapt):
    v[k] = scope.rawToV("A", data[k])
print('Raw     Min, Avg, Max =', np.amin(data), np.average(data), np.amax(data))
print('Voltage Min, Avg, Max =', np.amin(v), np.average(v), np.amax(v))

# close scope
scope.stop()
scope.close()

# plot
#for k in range(ncapt):
#    plt.subplot(ncapt, 1, k+1)
#    #plt.plot(data[0][k])
#    plt.plot(v[k])
plt.plot(v[k])
plt.show()
