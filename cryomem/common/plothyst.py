# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 17:46:27 2013

@author: linda
"""

import matplotlib.pyplot as plt
import numpy as np
import copy

# plot hysteretic 1-d data
def plothyst_old(x, y, color='black', label='data'):
    dx = x[1:] - x[:-1]
    dxcorr = dx[1:]*dx[:-1]
    iturn = (dxcorr<0).nonzero()[0] + 1
    iturn = np.hstack((np.array([0]), iturn, np.array([len(x)-1])))

    #self.axes = self.figure.add_subplot(111)
    #self.axes.hold(True)
    for m in range(len(iturn)-1):
        idx = list(range(iturn[m],iturn[m+1])) + [iturn[m+1]]
        if m == 0:
            plt.plot(x[idx], y[idx], color=color, linewidth=m+1, label=label)
        else:
            plt.plot(x[idx], y[idx], color=color, linewidth=m+1)

# general purpose Feb 2017
def plothyst(*args, **kwargs):
    """Plot hysteretic y(x)

    keywords:
    sglcolor
    colors, markers, mfcolors -- [<down sweep>, <up sweep>]
    any keyword for pyplot.plot()
    """
    # list args
    if not hasattr(args[0], '__iter__'):
        plothyst_old2(*args, **kwargs)  # backward compatible
        return 1
    else:
        x, y = map(np.array, args[:2])
        ax = plt.gca()

    # keyword args
    plotparam = kwargs
    sglcolor = plotparam.get('sglcolor', False)
    if sglcolor:
        color = plotparam.get('c', plotparam.get('color', 'b'))
    colors = plotparam.get('colors', ['b', 'r'])
    markers = plotparam.get('markers', ['s-', 'o-'])
    mfcolors = plotparam.get('mfcolors', ['w', 'w'])
    if 'c' in plotparam: del plotparam['c']
    if 'color' in plotparam: del plotparam['color']
    if 'sglcolor' in plotparam: del plotparam['sglcolor']
    if 'autocolor' in plotparam: del plotparam['autocolor']
    if 'colors' in plotparam: del plotparam['colors']
    if 'markers' in plotparam: del plotparam['markers']
    if 'mfcolors' in plotparam: del plotparam['mfcolors']
    if not 'ms' in plotparam: plotparam['ms'] = 6
    if not 'mew' in plotparam: plotparam['mew'] = 1.6
    if not 'alpha' in plotparam: plotparam['alpha'] = 1

    # single point
    if len(x) < 2:
        return ax.plot(x[0], y[0], 'x')

    # split different sweep directions
    #~ dx = x[1:] - x[:-1]
    #~ dxcorr = dx[1:]*dx[:-1]
    #~ iturn = (dxcorr<0).nonzero()[0] + 1
    #~ iturn = np.hstack((np.array([0]), iturn, np.array([len(x)-1])))
    #~ print(iturn)
    iturn = [0]
    prevsign = float(np.sign(x[1]-x[0]))
    for i in range(2,len(x)):
        thissign = float(np.sign(x[i]-x[i-1]))
        if thissign == -prevsign and thissign != 0:
            iturn.append(i-1)
            prevsign = thissign
        if not i in iturn:
            iturn.append(i)
    #print(iturn)
    #iturn = np.array(iturn)
    
    # plot
    #self.axes = self.figure.add_subplot(111)
    #self.axes.hold(True)
    ax.set_color_cycle(None)        # windows bug?
    for m in range(len(iturn)-1):
        idx = list(range(iturn[m],iturn[m+1])) + list([iturn[m+1]])
        if m == 0:  # 1st segment
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            if sglcolor:
                plotparam['color'] = color # windows prefers 'color' to 'c'?
                plotparam['mec'] = color
            else:
                plotparam['color'] = colors[isw]
                plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            line = ax.plot(x[idx], y[idx], mk, **plotparam)
            if 'label' in plotparam: del plotparam['label']
            
            # mark the first data point
            plotparam0 = copy.deepcopy(plotparam)
            plotparam0['mew'] = 2.4
            plotparam0['ms'] = plotparam['ms']*2.2
            line = ax.plot(x[idx[0]], y[idx[0]], 'x', **plotparam0)
        else:   # the rest after the 1st segment
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            if sglcolor:
                plotparam['color'] = color
                plotparam['mec'] = color
            else:
                plotparam['color'] = colors[isw]
                plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            line = ax.plot(x[idx], y[idx], mk, **plotparam)

    return line

# general purpose (obsolete)
def plothyst_old2(ax, x, y, **plotparam):
    """Plot hysteretic y(x)

    ax -- axes
    keywords:
    sglcolor
    colors, markers, mfcolors -- [<down sweep>, <up sweep>]
    any keyword for pyplot.plot()
    """
    # plot parameters
    sglcolor = plotparam.get('sglcolor', False)
    if sglcolor:
        color = plotparam.get('c', plotparam.get('color', 'b'))
    colors = plotparam.get('colors', ['b', 'r'])
    markers = plotparam.get('markers', ['s-', 'o-'])
    mfcolors = plotparam.get('mfcolors', ['w', 'w'])
    if 'c' in plotparam: del plotparam['c']
    if 'color' in plotparam: del plotparam['color']
    if 'sglcolor' in plotparam: del plotparam['sglcolor']
    if 'autocolor' in plotparam: del plotparam['autocolor']
    if 'colors' in plotparam: del plotparam['colors']
    if 'markers' in plotparam: del plotparam['markers']
    if 'mfcolors' in plotparam: del plotparam['mfcolors']
    if not 'ms' in plotparam: plotparam['ms'] = 6
    if not 'mew' in plotparam: plotparam['mew'] = 1.6
    if not 'alpha' in plotparam: plotparam['alpha'] = 1
    
    # split different sweep directions
    #~ dx = x[1:] - x[:-1]
    #~ dxcorr = dx[1:]*dx[:-1]
    #~ iturn = (dxcorr<0).nonzero()[0] + 1
    #~ iturn = np.hstack((np.array([0]), iturn, np.array([len(x)-1])))
    #~ print(iturn)
    iturn = [0]
    prevsign = float(np.sign(x[1]-x[0]))
    for i in range(2,len(x)):
        thissign = float(np.sign(x[i]-x[i-1]))
        if thissign == -prevsign and thissign != 0:
            iturn.append(i-1)
            prevsign = thissign
    if not i in iturn:
        iturn.append(i)
    #print(iturn)
    #iturn = np.array(iturn)
    
    # plot
    #self.axes = self.figure.add_subplot(111)
    #self.axes.hold(True)
    ax.set_color_cycle(None)        # windows bug?
    for m in range(len(iturn)-1):
        idx = list(range(iturn[m],iturn[m+1])) + list([iturn[m+1]])
        if m == 0:  # 1st segment
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            if sglcolor:
                plotparam['color'] = color # windows prefers 'color' to 'c'?
                plotparam['mec'] = color
            else:
                plotparam['color'] = colors[isw]
                plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            ax.plot(x[idx], y[idx], mk, **plotparam)
            if 'label' in plotparam: del plotparam['label']
            
            # mark the first data point
            plotparam0 = copy.deepcopy(plotparam)
            plotparam0['mew'] = 2.4
            plotparam0['ms'] = plotparam['ms']*2.2
            ax.plot(x[idx[0]], y[idx[0]], 'x', **plotparam0)
        else:   # the rest after the 1st segment
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            if sglcolor:
                plotparam['color'] = color
                plotparam['mec'] = color
            else:
                plotparam['color'] = colors[isw]
                plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            ax.plot(x[idx], y[idx], mk, **plotparam)

# deprecated by plothyst 2/24/15
def plothystcolor(ax, x, y, **plotparam):
    # plot parameters
    colors = plotparam.get('colors', ['b', 'r'])
    markers = plotparam.get('markers', ['s-', 'o-'])
    mfcolors = plotparam.get('mfcolors', ['w', 'w'])
    if 'colors' in plotparam: del plotparam['colors']
    if 'markders' in plotparam: del plotparam['markers']
    if 'mfcolors' in plotparam: del plotparam['mfcolors']
    if not 'ms' in plotparam: plotparam['ms'] = 6
    if not 'mew' in plotparam: plotparam['mew'] = 1.6
    if not 'alpha' in plotparam: plotparam['alpha'] = 1
    
    # split different sweep directions
    #~ dx = x[1:] - x[:-1]
    #~ dxcorr = dx[1:]*dx[:-1]
    #~ iturn = (dxcorr<0).nonzero()[0] + 1
    #~ iturn = np.hstack((np.array([0]), iturn, np.array([len(x)-1])))
    #~ print(iturn)
    iturn = [0]
    prevsign = np.sign(x[1]-x[0])
    for i in range(2,len(x)):
        thissign = np.sign(x[i]-x[i-1])
        if thissign == -prevsign:
            iturn.append(i)
            prevsign = thissign
    #iturn = np.array(iturn)
    
    # plot
    #self.axes = self.figure.add_subplot(111)
    #self.axes.hold(True)
    for m in range(len(iturn)-1):
        idx = list(range(iturn[m],iturn[m+1])) + list([iturn[m+1]])
        if m == 0:
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            plotparam['c'] = colors[isw]
            plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            ax.plot(x[idx], y[idx], mk, **plotparam)
            
            # mark the first data point
            plotparam0 = copy.deepcopy(plotparam)
            plotparam0['mew'] = 2.4
            plotparam0['ms'] = plotparam['ms']*2.2
            ax.plot(x[idx[0]], y[idx[0]], 'x', **plotparam0)
        else:
            isw = 1 if (x[idx[0]] < x[idx[-1]]) else 0  # sweep up or down?
            mk = markers[isw]
            plotparam['c'] = colors[isw]
            plotparam['mec'] = colors[isw]
            plotparam['mfc'] = mfcolors[isw]
            ax.plot(x[idx], y[idx], mk, **plotparam)

def plothystcolor_old(ax, x,y,colors=['b','r'],markers=['s-','o-'],label='data',\
                mfcolor=['w','w'], msize=6):
    dx = x[1:] - x[:-1]
    dxcorr = dx[1:]*dx[:-1]
    iturn = (dxcorr<0).nonzero()[0] + 1
    iturn = np.hstack((np.array([0]), iturn, np.array([len(x)-1])))
    
    #self.axes = self.figure.add_subplot(111)
    #self.axes.hold(True)
    for m in range(len(iturn)-1):
        idx = list(range(iturn[m],iturn[m+1])) + list([iturn[m+1]])
        if m == 0:
            if (x[idx[0]] < x[idx[-1]]):  # choose color based on x direction
                col = colors[1]; mk = markers[1]; mfcc = mfcolor[1]
            else:
                col = colors[0]; mk = markers[0]; mfcc = mfcolor[0]
            ax.plot(x[idx], y[idx], mk, alpha=1,mfc=mfcc,c=col,\
                mec=col,mew=1,ms=msize, label=label)
            ax.plot(x[idx[0]], y[idx[0]], 'x', alpha=1,mfc=mfcc,c=col,\
                mec=col,mew=2.4,ms=msize*2.2)
        else:
            if (x[idx[0]] < x[idx[-1]]):  # choose color based on x direction
                col = colors[1]; mk = markers[1]; mfcc = mfcolor[1]
            else:
                col = colors[0]; mk = markers[0]; mfcc = mfcolor[0]
            ax.plot(x[idx], y[idx], mk, alpha=1,mfc=mfcc,c=col,\
                mec=col,mew=1,ms=msize)

def plothystcolor2(x, y, colors=['blue','red'], label='data', markersize=6):
    dx = x[1:] - x[:-1]    
    iinc = (dx>0).nonzero()[0]
    idec = (dx<0).nonzero()[0]
    plt.plot(x[iinc], y[iinc], 'o', alpha=1,mfc='white',mec=colors[0],mew=1,ms=markersize, label=label)
    plt.plot(x[idec], y[idec], 'o', alpha=1,mfc='white',mec=colors[1],mew=1,ms=markersize)

def plothystcolor3(x, y, marker='o', colors=['blue','red'], mfc='white', mew=1,\
    **params):
    dx = x[1:] - x[:-1]    
    iinc = (dx>0).nonzero()[0]
    idec = (dx<0).nonzero()[0]
    plt.plot(x[iinc], y[iinc], marker, mec=colors[1], mfc=mfc,mew=mew,**params)
    plt.plot(x[idec], y[idec], marker, mec=colors[0], mfc=mfc,mew=mew,**params)
