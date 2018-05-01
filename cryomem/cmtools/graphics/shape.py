"""
Draw custom shapes on matplotlib axes
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def cylinder(x, y, **kwargs):
    """Draw cylinder projected to 2-d
    
    x,y: center coordinates
    **kwargs:
    width, height, facecolor, sidecolor, angle
    """
    ax = plt.gca()
    w = kwargs['width']
    h = kwargs['height']
    fc = kwargs.get('facecolor', kwargs.get('fc', 'white'))
    sidecolor = kwargs.get('facecolor', kwargs.get('sc', 'white'))
    edgewidth = kwargs.get('edgewidth', 1)
    edgecolor = kwargs.get('edgecolor', 'black')
    angle = kwargs.get('angle', 30)     # not implemented

    # bottom
    el = Ellipse(xy=(x,y), width=w, height=w/4)
    ax.add_artist(el)
    ax.set_facecolor(fc)

if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot()
    
    # example
    cylinder(0, 0, width=2, height=1, facecolor='orange', sidecolor='red')
    
    plt.show()
