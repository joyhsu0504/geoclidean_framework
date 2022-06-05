import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiLineString
import descartes
import matplotlib.ticker as plticker

def initial_plot():
    loc = plticker.MultipleLocator(base=1.0)

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_locator(loc)
    ax.yaxis.set_major_locator(loc)
    ax.axis('equal')
    ax.axis('off') 
    return ax

def plot_obj(ax, obj, color="black"):
    if isinstance(obj, Polygon):
        obj = obj.exterior
    x, y = obj.xy
    ax.plot(x, y, linewidth=3, color=color)
    return ax
    
def plot_point(ax, point, color="black"):
    x, y = point.xy
    ax.scatter(x, y, linewidth=5, color=color)
    return ax
    
def plot_intersection(ax, intersection):
    if isinstance(intersection, MultiLineString):
        for i in intersection.geoms:
            plot_obj(ax, i)
    if isinstance(intersection, LineString):
        plot_obj(ax, intersection)
    if isinstance(intersection, MultiPoint):
        for i in intersection.geoms:
            plot_point(ax, i)
    if isinstance(intersection, Point):
        plot_point(ax, intersection)
    return ax
        
def save_plot(path):
    plt.savefig(path)
    