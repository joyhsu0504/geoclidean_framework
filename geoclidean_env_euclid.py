from utils import *
from plot_utils import *
import random
import os
import re
import numpy as np

import shapely
from shapely.ops import substring


CANVAS_SIZE = 16

class GeoclideanPoint:
    def __init__(self, name, obj_constraints):
        self.name = name
        self.obj_constraints = obj_constraints
        
    def __str__(self):
        return 'Point ' + self.name + '(' + self.obj_constraints + ')'

class GeoclideanObj:
    def __init__(self, name, obj_type, parameters, visibility):
        self.name = name
        self.obj_type = obj_type
        self.parameters = parameters
        self.visibility = visibility
        
    def __str__(self):
        return 'Obj ' + self.name + ': ' + self.obj_type
    
def parse_rule(rule):
    regex = r'(.*) = (.*)\((.*)\((.*)\), (.*)\((.*)\)\)'
    match = re.match(regex, rule).groups()

    if '*' in match[0]:
        visibility = True
        name = match[0][:-1]
    else:
        visibility = False
        name = match[0]

    obj_type = match[1]

    param_a_name = match[2]
    param_a_constraints = match[3]
    param_b_name = match[4]
    param_b_constraints = match[5]

    param_a = GeoclideanPoint(param_a_name, param_a_constraints)
    param_b = GeoclideanPoint(param_b_name, param_b_constraints)

    obj = GeoclideanObj(name, obj_type, [param_a, param_b], visibility)
    return obj

def shapely_point_for_point(point, all_shapely_obj, all_shapely_point):
    if point.name in all_shapely_point:
        return all_shapely_point[point.name]
    
    if len(point.obj_constraints) == 0:
        shapely_point = Point(np.random.uniform(0, CANVAS_SIZE), np.random.uniform(0, CANVAS_SIZE))
    else:
        obj_constraints = point.obj_constraints.split(', ')
        if len(obj_constraints) > 1:
            base_obj = action_create_intersection(all_shapely_obj[obj_constraints[0]], all_shapely_obj[obj_constraints[1]])

        else:
            base_obj = all_shapely_obj[obj_constraints[0]]
        potential_points =  all_interpolated_points_from_obj(base_obj)
        if len(potential_points) == 1:
            shapely_point = potential_points[0]
        else:
            idx = np.random.randint(len(potential_points), size=1)[0]
            shapely_point = potential_points[idx]
    return shapely_point
    
def all_interpolated_points_from_obj(obj, sample_distance=0.2):
    interpolated_points = []

    if isinstance(obj, Polygon):
        for i in obj.exterior.coords:
            p = Point(i[0], i[1])
            interpolated_points.append(p)

    elif isinstance(obj, MultiLineString):
        mp = MultiPoint()
        for linestring in obj.geoms:
            for i in np.arange(0, linestring.length, sample_distance):
                s = substring(linestring, i, i+sample_distance)
                mp = mp.union(s.boundary)
        interpolated_points = [p for p in mp.geoms]

    elif isinstance(obj, LineString):
        mp = MultiPoint()
        for i in np.arange(0, obj.length, sample_distance):
            s = substring(obj, i, i+sample_distance)
            mp = mp.union(s.boundary)
        interpolated_points = [p for p in mp.geoms]

    elif isinstance(obj, MultiPoint):
        interpolated_points = [p for p in obj.geoms]

    elif isinstance(obj, Point):
        interpolated_points = [obj]

    return interpolated_points

def render(rules, mark_points=False):
    # Parse to construction
    euclidean_objects = [parse_rule(rule) for rule in rules]

    # Render
    all_shapely_obj, all_shapely_point = {}, {}
    all_viewable_objs = []
    
    current_plot = initial_plot()
    for euc_obj in euclidean_objects:
        point_a_shapely = shapely_point_for_point(euc_obj.parameters[0], all_shapely_obj, all_shapely_point)
        point_b_shapely = shapely_point_for_point(euc_obj.parameters[1], all_shapely_obj, all_shapely_point)
        if euc_obj.obj_type == 'line':
            obj_shapely = action_create_line(point_a_shapely, point_b_shapely)
        if euc_obj.obj_type == 'circle':
            obj_shapely = action_create_circle(point_a_shapely, point_b_shapely)
        all_shapely_point[euc_obj.parameters[0].name] = point_a_shapely
        all_shapely_point[euc_obj.parameters[1].name] = point_b_shapely
        all_shapely_obj[euc_obj.name] = obj_shapely
            
        if euc_obj.visibility == True:
            current_plot = plot_obj(current_plot, obj_shapely)
            all_viewable_objs.append(obj_shapely)
            
        if mark_points:
            current_plot = plot_point(current_plot, point_a_shapely)
            current_plot = plot_point(current_plot, point_b_shapely)
        
    return all_viewable_objs

def numpy_from_plot(ax):
    ax.figure.canvas.draw()
    data = np.frombuffer(ax.figure.canvas.tostring_rgb(), dtype=np.uint8)
    w, h = ax.figure.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return im

def plot_all_except_i(all_viewable_objs, i):
    curr_plot = initial_plot()
    for curr_i, o in enumerate(all_viewable_objs):
        if curr_i == i:
            curr_plot = plot_obj(curr_plot, o, color='white')
        else:
            curr_plot = plot_obj(curr_plot, o)
    curr_plot = numpy_from_plot(curr_plot)
    plt.close()
    return curr_plot

def visibility_test(all_viewable_objs, threshold=400):
    all_plot = initial_plot()
    for o in all_viewable_objs:
        all_plot = plot_obj(all_plot, o)
    all_plot = numpy_from_plot(all_plot)
    plt.close()
    
    for i, o in enumerate(all_viewable_objs):
        curr_plot = plot_all_except_i(all_viewable_objs, i)
        diff = curr_plot[:, :, 0] - all_plot[:, :, 0]
        diff[diff > 1] = 1
        if np.sum(diff) < threshold:
            return False
    return True

def save_steps(all_viewable_objs, dir_name):
    curr_plot = initial_plot()
    for i, o in enumerate(all_viewable_objs):
        curr_plot = plot_obj(curr_plot, o)
        save_plot(dir_name + 'step_' + str(i+1) + '.png')
    plt.close()
    
def save_steps_joint(all_viewable_objs, dir_name, num_steps=3):
    loc = plticker.MultipleLocator(base=1.0)
    fig, plts = plt.subplots(1, num_steps, figsize=(5*num_steps, 5))
    for p in range(num_steps):
        plts[p].xaxis.set_major_locator(loc)
        plts[p].yaxis.set_major_locator(loc)
        plts[p].axis('equal')
        plts[p].axis('off')
        for i in range(p+1):
            plts[p] = plot_obj(plts[p], all_viewable_objs[i])

    save_plot(dir_name)
    plt.close()
            
def generate_concept(rules, mark_points=False, steps_path=None, path=None, dup_path=None, show_plots=False):
    i = 0
    while i < 1:
        try:
            all_viewable_objs = render(rules, mark_points)
            if visibility_test(all_viewable_objs):
                if steps_path:
                    save_steps_joint(all_viewable_objs, steps_path)
                if path:
                    save_plot(path)
                if dup_path:
                    save_plot(dup_path)
                    
                i += 1
                if not show_plots:
                    plt.close()
                
            else:
                plt.close()
        except:
            plt.close()
            continue 
            
