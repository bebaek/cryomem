from picoscope.ps5000a import *
from ctypes import c_uint16
import numpy as np

class PS5000a_bb(PS5000a):
    """Add/override rapid-block methods in ps5000a picoscope wrapper"""
    def _lowLevelSetNoOfCaptures(self, numCaptures):
        m = self.lib.ps5000aSetNoOfCaptures(c_int16(self.handle),
            c_uint16(numCaptures))
        self.checkResult(m)

    def _lowLevelMemorySegments(self, numSegments):
        maxSamples = c_int32()
        m = self.lib.ps5000aMemorySegments(c_int16(self.handle),
            c_uint16(numSegments), byref(maxSamples))
        self.checkResult(m)
        return maxSamples.value

    def _lowLevelGetMaxSegments(self):
        maxSegments = c_int16()
        m = self.lib.ps5000aGetMaxSegments(c_int16(self.handle),
            byref(maxSegments))
        self.checkResult(m)
        return maxSegments.value

    # Bulk values.
    # These would be nice, but the user would have to provide us
    # with an array.
    # we would have to make sure that it is contiguous amonts other things
    def _lowLevelGetValuesBulk(self,
                               numSamples, fromSegmentIndex, toSegmentIndex,
                               downSampleRatio, downSampleRatioMode,
                               overflow):
        noOfSamples = c_uint32(numSamples)

        m = self.lib.ps5000aGetValuesBulk(
            c_int16(self.handle),
            byref(noOfSamples),
            c_uint32(fromSegmentIndex), c_uint32(toSegmentIndex),
            c_uint32(downSampleRatio), c_enum(downSampleRatioMode),
            overflow.ctypes.data_as(POINTER(c_int16))
            )
        self.checkResult(m)
        return noOfSamples.value

    def getDataRawBulk(self, channel='A', numSamples=0, fromSegment=0,
        toSegment=None, downSampleRatio=1, downSampleMode=0, data=None):
        '''
        Get data recorded in block mode.
        Override definition in picobase.
        '''
        if not isinstance(channel, int):
            channel = self.CHANNELS[channel]
        if toSegment is None:
            toSegment = self.noSegments - 1
        if numSamples == 0:
            numSamples = min(self.maxSamples, self.noSamples)

        numSegmentsToCopy = toSegment - fromSegment + 1
        if data is None:
            data = np.ascontiguousarray(
                np.zeros((numSegmentsToCopy, numSamples), dtype=np.int16)
                )

        # set up each row in the data array as a buffer for one of
        # the memory segments in the scope
        for i, segment in enumerate(range(fromSegment, toSegment+1)):
            # different from picobase
            self._lowLevelSetDataBuffer(channel,
                                            data[i],
                                            downSampleMode,
                                            segment)
        overflow = np.ascontiguousarray(
            np.zeros(numSegmentsToCopy, dtype=np.int16)
            )

        self._lowLevelGetValuesBulk(numSamples, fromSegment, toSegment,
            downSampleRatio, downSampleMode, overflow)

        return (data, numSamples, overflow)

