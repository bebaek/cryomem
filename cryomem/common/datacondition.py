"""Data conditioning tools"""
import numpy as np

def deglitch(data, **kwargs):
    """Mark False at elements with too big a difference from the neighbor and
    return the index list.
    """
    factor = kwargs.get("factor", 10)
    x = np.array(data)
    dx = x[1:] - x[:-1]
    idx = abs(dx) < factor*abs(np.mean(dx))
    return np.insert(idx, 0, True)
