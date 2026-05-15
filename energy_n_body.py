import numpy as np 
from rk import *
import pyglet as pg 
import draw as d 
from body import Body 

t_final = 10000
G = 1 # 6.674e-11
tick = 60*200 # fps / tick rate 

# initial conditions: [ [x,y,z], [vx,vy,vz], [m, 0, 0] ] per row 

# The Montgomery-Chenciner Figure-8 Orbit
bodies = 3 
w = 5 # width of screen
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
    [ [97.000436, -24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B1
    [ [-97.000436, 24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B2
    [ [0.0, 0.0, 0.0], [-0.93240737, -0.86473146, 0], [100, 0, 0] ],               # B3
]) # Add B-n rows for the Bn-th body

def to_CM_ref(body_objects, CM_object, only_compute_CM=False):
    r_abs = [] # pos WRT abs ref frame
    mass = []

    for body in body_objects:
        r_abs = np.append(r_abs, body.position)
        mass = np.append(mass, body.mass)

    # calculate center of mass 
    r_cm = np.zeros(3) # [x_cm, y_cm, z_cm] 
    for i in range(3):
        r_cm[i] = np.dot(r_abs[:, i], mass) / np.sum(mass) 

    CM_object.position = r_cm 

    if only_compute_CM:
        return r_cm

    # body is in abs ref frame before this 
    for body in body_objects:
        # r_abs to r_cm
        body.position -= r_cm

        # v_abs to v_cm 
        body.velocity -= CM_object.velocity

# converts to absolute ref frame (absolute = origin)
def to_abs_ref(body_objects, CM_object):
    # body is in CM ref frame before this 
    for body in body_objects:
        # r_cm to r_abs 
        body.position += CM_object.position

        # v_cm to v_abs 
        body.velocity += CM_object.velocity

# returns magnitude of vector
def vec_mag(vec):
    sum = 0
    for e in vec:
        sum += e**2
    return np.sqrt(sum)

# returns potential energy of bodies in CM ref frame 
def potential_energy(body_objects):
    # body is (assumed to be) in CM ref frame 
    potential = 0
    for i in range(len(body_objects)):
        for j in range(len(body_objects)):
            if i != j:
                delta_r = vec_mag(body_objects[i].position - body_objects[j].position)

                # if bodies have collided, potential b/w those is 0
                if (delta_r < (body_objects[i].radius + body_objects[j].radius)):
                    continue

                potential += -G * body_objects[i].mass * body_objects[j].mass / delta_r 

    return potential

def kinetic_energy(body_objects):
    # body is (assumed to be) in CM ref frame 
    kinetic = 0
    for body in body_objects:
        kinetic += 0.5 * body.mass * (vec_mag(body.velocity))**2

    return kinetic 


