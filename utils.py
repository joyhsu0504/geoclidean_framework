import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiLineString
import descartes
import matplotlib.ticker as plticker

def action_create_line(point_a, point_b):
    line = LineString([(point_a.x, point_a.y), (point_b.x, point_b.y)])
    return line

def action_create_circle(point_center, point_c):
    radius = point_center.distance(point_c)
    circle = Point(point_center.x, point_center.y).buffer(radius)
    return circle

def action_create_circle_with_radius(point_center, radius):
    circle = Point(point_center.x, point_center.y).buffer(radius)
    return circle

def action_create_intersection(obj_a, obj_b):
    if isinstance(obj_a, Polygon):
        obj_a = obj_a.boundary
    if isinstance(obj_b, Polygon):
        obj_b = obj_b.boundary
    intersection = obj_a.intersection(obj_b)
    return intersection