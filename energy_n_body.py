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

    return body_objects

# converts to absolute ref frame (absolute = origin)
def to_abs_ref(body_objects, CM_object):
    # body is in CM ref frame before this 
    for body in body_objects:
        # r_cm to r_abs 
        body.position += CM_object.position

        # v_cm to v_abs 
        body.velocity += CM_object.velocity

    return body_objects

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

# returns potential energy of a single body in CM ref frame (copied from above)
def potential_energy_single(body_objects, body_index):
    i = body_index
    potential = 0
    for j in range(len(body_objects)):
        if i != j:
            delta_r = vec_mag(body_objects[i].position - body_objects[j].position)

            # if bodies have collided, potential b/w those is 0
            if (delta_r < (body_objects[i].radius + body_objects[j].radius)):
                continue

            potential += -G * body_objects[i].mass * body_objects[j].mass / delta_r 

    return potential

# returns kinetric energy in CM ref frame 
def kinetic_energy(body_objects):
    # body is (assumed to be) in CM ref frame 
    kinetic = 0
    for body in body_objects:
        kinetic += 0.5 * body.mass * (vec_mag(body.velocity))**2

    return kinetic 

def kinetic_energy_single(body_objects, body_index):
    i = body_index
    return 0.5 * body_objects[i].mass * (vec_mag(body_objects[i].velocity))**2

# returns current momentum in CM ref frame 
def momentum(body_objects):
    # body is (assumed to be) in CM ref frame 
    p = np.zeros(3) # [px, py, pz]
    for body in body_objects:
        p += body_objects.velocity * body_objects.mass

    return p 

# returns negative gradient vector of a body at body_index in body_objects at current position in CM ref frame 
def gradient_neg(body_objects, body_index):
    grad_vec = np.zeros(3) # [dx, dy, dz]

    for i in range(len(body_objects)):
        if (i != body_index):
            delta_r = body_objects[i].position - body_objects[body_index].position
            delta_r_mag = vec_mag(delta_r)

            # collision detection
            if (delta_r_mag < (body_objects[i].radius + body_objects[body_index].radius)):
                continue

            grad_vec += -G*body_objects[i].mass*body_objects[body_index].mass*delta_r / (delta_r_mag)**3

    return grad_vec

def fg(t, i, bodies_arr):
    def mag(vec): # returns magnitude of vec 
        sum = 0
        for e in vec:
            sum += e**2
        return np.sqrt(sum)

    position_next = bodies_arr[i].position
    velocity_next = np.zeros(3, dtype=float)
    # b1_next = np.zeros((2,3))

    # b1_next[0] = b1_old[1]7
    for j in range(len(mass)):
        if (i == j):
            continue
        delta_r = bodies_arr[i].position - bodies_arr[j].position

        # Handles collisions
        # 1 is the width of the bodies. change this based on size of bodies
        # NOTE: Mass isn't conserved; the mass of one of the w bodies involved in the collisions gets destroyed
        if (mag(delta_r) < 1):
            # TODO: Implement elastic collisions
            # m1v1 = m2v2
            # NOTE: COULD BE WRONG!! BAD!!!!! UNTESTED
            # TODO: Handle deletion
            position_next = 0
            velocity_next = bodies_arr[i].velocity + bodies_arr[j].velocity
            # b1_next[0] = 0
            # b1_next[1] = 0

            continue

        velocity_next += -G * bodies_arr[j].mass * delta_r / (mag(delta_r)) ** 3
        # b1_next[1] += -G*mass[i]*(delta_r) / (mag(delta_r))**3

    # return b1_next
    body_next = copy.deepcopy(bodies_arr[i])
    body_next.position = position_next
    body_next.velocity = velocity_next
    return body_next

# calculates next position based on 
def calculate_position(body_objects, step=0.01):
    body_objects_next = body_objects
    for i in range(len(body_objects)):
        potential_i = potential_energy_single(body_objects, i)
        kinetic_i = kinetic_energy_single(body_objects, i)
        total_i = potential_i + kinetic_i

        # normalize then scale gradient vector
        grad_vec = gradient_neg(body_objects, body_index)
        grad_vec /= vec_mag(grad_vec)
        grad_vec *= step

        # temporarily make the change in the body_objects list
        body_objects[i].position += grad_vec
        potential_i_next = potential_energy_single(body_objects, i)
        
        # write then revert the change here so we get the original conditions
        body_objects_next[i].position = body_objects[i].position
        body_objects[i].position -= grad_vec

        # solve for new kinetic energy and velocity magnitude
        kinetic_i_next = total_i - potential_i_next
        velocity_mag_next = (2 * kinetic_i_next / body_objects[i].mass) ** 0.5

        # conserve momentum to get new velocity
        
    return body_objects_next

### WARN: New plan for calculating:
#   First, run RK to get the force changes
#   Then, remove any leftover momentum
#   Lastly, rescale velocities to conserve energy
