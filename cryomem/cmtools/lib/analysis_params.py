# -*- coding: utf-8 -*-
"""
Data analysis setup (source/output directory, etc).

BB 2014
"""

from collections import OrderedDict
    
# Config file used by analysis
class AnalysisParams:
    def __init__(self, filename='cfg_analysis.txt'):
        self.configfilename = filename
        f = open(filename, 'r')
        self.params = OrderedDict([])
        for line in f:
            l = line.split('=')
            self.params[l[0].strip()] = l[1].strip()
        f.close()
        self.datapath = self.params.get('data path root','.') + '/' \
                    + self.params.get('data folder','')
        self.tag = self.params.get('output file tag','x')


if __name__=='__main__':
    
    filename = 'test'    
    data = AnalysisParams(filename)
    data.readcfgfile()
    data.readdatafile()
    data.convert2iv()
    print(data.i, data.v)
    exit(0)
