# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Manage database of SV JJ device fab/measurement parameters
File format: HDF5.
Two tables: FabDevice, JJParams
BB, 2015
"""

import numpy as np
import tables as tb

## To be nested
#class ChipFab(tb.IsDescription):
#    wafer   = tb.StringCol(16)
#    name    = tb.StringCol(16)
#    layer_names = tb.StringCol(16, shape=100)
#    layer_thicknesses = tb.Float64Col(shape=100)
#    unit_thickness = tb.StringCol(8)
#    comment = tb.StringCol(256)
#
## To be nested
#class DeviceFab(tb.IsDescription):
#    chip = ChipFab()
#    name = tb.StringCol(16)
#    shape = tb.StringCol(16)
#    dimensions = tb.Float64Col(shape=8)
#    comment = tb.StringCol(256)

_maxnlayer = 16
_maxndim = 4

# Main table structure for measured device parameters
class JJParams(tb.IsDescription):
    # ID
    wafer   = tb.StringCol(16)
    chip    = tb.StringCol(16)
    device  = tb.StringCol(16)
    
    # Structure
    nlayer = tb.UInt32Col()             # n of layers (exclude S1, WR, ...)
    layer_names = tb.StringCol(16, shape=_maxnlayer)
    layer_thicknesses = tb.Float64Col(shape=_maxnlayer)
    shape = tb.StringCol(16)            # Ellipse or Circle
    dimensions = tb.Float64Col(shape=_maxndim) # [x_major, y_major] or [diameter] in m
    
    # Measurement conditions
    meas_date = tb.StringCol(8)         # MM/DD/YY
    #meastime = tb.Time64()
    meas_equip = tb.StringCol(32)       # Dipstick by default
    meas_method = tb.StringCol(32)      # IV trace by default
    temperature = tb.Float64Col()       # 4 by default
    
    # analysis condition
    analysis_method = tb.StringCol(32)  # RSJ by default

    # Units
    unit_length = tb.StringCol(8)       # m by default
    unit_temperature = tb.StringCol(8)  # K
    unit_current = tb.StringCol(8)      # A
    unit_resistance = tb.StringCol(8)   # Ohm
    unit_field = tb.StringCol(8)        # T

    # Resulting parameters
    ic_p    = tb.Float64Col()           # Superconducting critical currents
    ic_ap   = tb.Float64Col()
    rn_p   = tb.Float64Col()            # Normal resistances
    rn_ap   = tb.Float64Col()
    h_sw_p = tb.Float64Col()            # Switching fields
    h_sw_ap = tb.Float64Col()

class DB():
    def __init__(self, **kwargs):
        if 'filename' in kwargs:
            self.open_db(kwargs['filename'])

        # Default data
        layer_names0 = ['Nb'] + ['Air']*(_maxnlayer - 1)
        layer_thicknesses0 = [100e-9] + [1e-12]*(_maxnlayer - 1)
        dimensions0 = [100e-9] + [1e-12]*(_maxndim - 1)
        self.param0 = {'wafer': 'Byymmdd', 'chip': '66', 'device': 'A01', 'nlayer': 7, 'layer_names': layer_names0, 'layer_thicknesses': layer_thicknesses0, 'shape': 'ellipse', 'dimensions': dimensions0, 'meas_date': 'mm/dd/15', 'meas_equip': 'dipstick', 'meas_method': 'IV traces on scope', 'temperature': 4, 'analysis_method': 'RSJ', 'unit_length': 'm', 'unit_temperature': 'K', 'unit_current': 'A', 'unit_resistance': 'Ohm', 'unit_field': 'T', 'ic_p': 100e-6, 'ic_ap': 20e-6, 'rn_p': 1.1, 'rn_ap': 1.1, 'h_sw_p': 0.005, 'h_sw_ap': 0.005}

    def create_db(self, filename, title='SV JJs'):
        self.h5file = tb.open_file(filename, mode='w', title=title)
        self.table = self.h5file.create_table('/', 'jjparams', JJParams,\
                'Measured JJ parameters')

    def open_db(self, filename):
        self.h5file = tb.open_file(filename, mode='a')
    
    def close_db(self):
        self.h5file.close()
    
    def read_jj(self, cols):
        """Return data columns specified
        """
        data = [x[c] for c in cols]
        return data

    # Get inputs from argument or interactively
    # Use val0 as default for interactive case
    def in_param(self, key, val0='0', **kwargs):
        wantinteract = kwargs.get('wantinteract', True)
        datatype = kwargs.get('datatype', 'string')
        if wantinteract:
            msg = input(key + '? [%s] '%str(val0))
            if msg == '': msg = val0          # empty input means default

            if datatype == 'string': val = msg
            if datatype == 'uint': val = int(msg)
            if datatype == 'float': val = float(msg)
        else:
            val = val0
        return val

    def add_jj(self, **kwargs):
        jj = self.table.row
        wantinteract=kwargs.get('wantinteract', True)
        col = 'wafer'
        self.param0[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        jj[col] = self.param0[col].encode()
        col = 'chip'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'device'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'nlayer'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='uint')
        
        col1 = 'layer_names'
        col2 = 'layer_thicknesses'
        for k in range(jj['nlayer']):
            #self.param0[col1][k] = jj[col1][k] = self.in_param(col1+str(k+1), self.param0[col1][k], wantinteract=wantinteract)
            #self.param0[col2][k] = jj[col2][k] = self.in_param(col2+str(k+1), self.param0[col2][k], wantinteract=wantinteract)
            self.param0[col1][k] = self.in_param(col1+' '+str(k+1), self.param0[col1][k], wantinteract=wantinteract)
            self.param0[col2][k] = self.in_param(col2+' '+str(k+1), self.param0[col2][k], wantinteract=wantinteract, datatype='float')
        jj[col1] = [self.param0[col1][k].encode() for k in range(_maxnlayer)]
        jj[col2] = self.param0[col2]
        print(self.param0[col1], jj[col1])
        print(self.param0[col2], jj[col2])

        col = 'shape'
        self.param0[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        jj[col] = self.param0[col].encode()

        col = 'dimensions'
        if jj['shape'].decode() == 'circle':
            ndim = 1
        elif jj['shape'].decode() == 'ellipse':
            ndim = 2
        else:
            ndim = 3
        for k in range(ndim):
            #self.param0[col][k] = jj[col][k] = self.in_param(col+str(k+1), self.param0[col][k], wantinteract=wantinteract)
            self.param0[col][k] = self.in_param(col+str(k+1), self.param0[col][k], wantinteract=wantinteract, datatype='float')
        jj[col] = self.param0[col]
        print(self.param0[col], jj[col])

        col = 'meas_date'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'meas_equip'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'meas_method'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'temperature'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'analysis_method'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'unit_length'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'unit_temperature'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'unit_current'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'unit_resistance'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'unit_field'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract)
        col = 'ic_p'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')
        col = 'ic_ap'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')
        col = 'rn_p'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')
        col = 'rn_ap'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')
        col = 'h_sw_p'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')
        col = 'h_sw_ap'
        self.param0[col] = jj[col] = self.in_param(col, self.param0[col], wantinteract=wantinteract, datatype='float')

        jj.append()
        if kwargs.get('wantflush', True):   # Flush by default
            self.table.flush()

    def del_jj(self, **kwargs):
        pass

    def edit_jj(self, **kwargs):
        pass
    
if __name__ == '__main__':
    import sys
    print(sys.version)

    filename = input('DB filename? (no extension) ') + '.h5'
    db = DB()
    db.create_db(filename)
    db.add_jj()
    db.close_db()
    print('Bye!')
