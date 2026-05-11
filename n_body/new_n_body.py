import numpy as np
import pyglet as pg
import draw as d
import copy
from body import *

bodies = 3 # number of bodies
t_final = 10000

w = 5 # width of the screen
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
    [ [97.000436, -24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B1
    [ [-97.000436, 24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B2
    [ [0.0, 0.0, 0.0], [-0.93240737, -0.86473146, 0], [100, 0, 0] ],               # B3
]) # Add B-n rows for the Bn-th body

G = 1 # 6.674e-11
fps = 60*200 # tick rate

# arr: initial conditions
# n: number of bodies
def bodies_init(arr, n):
    bodies_arr = []
    for i in range(n):
        color = [0] * 3
        color[i] = 255
        color = tuple(color)

        bodies_arr.append(Body(
            position=arr[i+1, 0],
            velocity=arr[i+1, 1],
            mass=arr[i+1, 2][0],
            color=color,
        ))

    return bodies_arr

def abs_to_rel(bodies_arr):
    bodies = len(bodies_arr)

    r_cm = np.zeros(3)
    for k in range(3):
        sum = 0
        for i in range(bodies):
            r_cm[k] += bodies_arr[i].position[k] * bodies_arr[i].mass
            sum += bodies_arr[i].mass

        r_cm[k] /= sum

    for i in range(1, bodies):
        bodies_arr[i].position -= r_cm
        bodies_arr[i].velocity -= bodies_arr[0].velocity

    return r_cm

# def to_CM_ref(r_abs, vel_abs, mass, CM_only=False):
#     bodies = len(r_abs) # number of true bodies + 1 
#
#     # calculate center of mass
#     r_cm = np.zeros(3) # [x_cm, y_cm, z_cm]
#     for i in range(3):
#         r_cm[i] = np.dot(r_abs[1:,i], mass) / np.sum(mass) # i+1 to leave out CM values
#
#     if CM_only:
#         return r_cm 
#
#     # get positions WRT CM
#     r = np.array([]) 
#     r = np.zeros_like(r_abs) 
#     r[0] = r_abs[0] # preserves position of CM across function calls
#     for i in range(1, bodies):
#         r[i] = r_abs[i] - r_cm # Fill the rows directly
#
#     # get velocities WRT CM (non-relativistic)
#     vel = np.zeros_like(vel_abs)
#     vel[0] = vel_abs[0] # preserves velocity of CM across function calls
#     for i in range(1, bodies):
#         vel[i] = vel_abs[i] - vel_abs[0] # Fill the rows directly
#
#     return r, vel, r_cm

# converts to absolute reference frame (absolute = origin)
def rel_to_abs(bodies_arr, r_cm):
    bodies = len(bodies_arr)

    for i in range(1, bodies):
        bodies_arr[i].position += bodies_arr[0].position + r_cm
        bodies_arr[i].velocity += bodies_arr[0].velocity

# def to_abs_ref(r, vel, r_cm):
#     bodies = len(r)
#
#     # get absolute positions
#     r_abs = np.zeros_like(r)
#     r_abs[0] = r[0] # preserves CM position across function calls
#     for i in range(1, bodies):
#         r_abs[i] = r[i] + r_cm + r[0]
#
#     # get absolute velocities (non-relativistic)
#     vel_abs = np.zeros_like(vel)
#     vel_abs[0] = vel[0] # preserves value across function calls
#     for i in range(1, bodies):
#         vel_abs[i] = vel[i] + vel_abs[0]
#
#     return r_abs, vel_abs

def rk_single(f, t_i, i, bodies_arr, h=0.005):
    y = bodies_arr[i].position
    t = t_i
    step_size = h 

    k_1 = f(t, y, extra1, extra2)
    k_2 = f(t+step_size/2, y+k_1*step_size/2, extra1, extra2)
    k_3 = f(t+step_size/2, y+k_2*step_size/2, extra1, extra2)
    k_4 = f(t+step_size, y+k_3*step_size, extra1, extra2)

    t_next = t + step_size
    y_next = y + step_size / 6 * (k_1 + 2*k_2 + 2*k_3 + k_4)

    return t_next, y_next

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

d.__init__(1280, 720, 64*w, 36*w)

bodies_arr = bodies_init(initial, bodies)
t_curr = 0

def update(dt):
    global t_curr

    if (t_curr > t_final):
        return
    
    d.start_frame()
    d.draw_axes()

    # Switch to relative reference frame
    r_cm = abs_to_rel(bodies_arr)

    # Calculate next time step
    bodies_arr_next = []
    t = 0
    for i in range(bodies):
        t, body_next = rk_single(fg, t_curr, i, bodies_arr)
        bodies_arr_next.append(body_next)

    # Switch back to absolute reference frame
    rel_to_abs(bodies_arr, r_cm)

    # Render next time step
    bodies_arr = bodies_arr_next
    for i in range(bodies):
        d.draw(
            bodies_arr[i].position[0],
            bodies_arr[i].position[1],
            bodies_arr[i].color,
            bodies_arr[i].radius,
        )

    d.end_frame()

    t_curr = t

pg.clock.schedule_interval(update, 1/fps)
d.__run__()
