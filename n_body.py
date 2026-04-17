import numpy as np 
from rk import * 
import pyglet as pg 
import draw as d 
from body import Body 

bodies = 3 # number of bodies
# initial conditions: [ [x, y, z], [v_x, v_y, v_z], [m] ] per row 
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
    [ [97.000436, -24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B1
    [ [-97.000436, 24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B2
    [ [0.0, 0.0, 0.0], [-0.93240737, -0.86473146, 0], [100, 0, 0] ]               # B3
]) # Add B-n rows for the Bn-th body
t_final = 10000

G = 1 # 6.674e-11
fps = 60*200

def to_CM_ref(r_abs, vel_abs, mass, CM_only=False):
    bodies = len(r_abs) # number of true bodies + 1 

    # calculate center of mass
    r_cm = np.zeros(3) # [x_cm, y_cm, z_cm]
    for i in range(3):
        r_cm[i] = np.dot(r_abs[1:,i], mass) / np.sum(mass) # i+1 to leave out CM values

    if CM_only:
        return r_cm 

    # get positions WRT CM
    r = np.array([])
    # NOTE: not sure if r[0] should be r_cm or r_abs[0]; and whether r[i] should depend on r_abs[0]
    r = np.zeros_like(r_abs) 
    r[0] = r_abs[0] # preserves position of CM across function calls
    for i in range(1, bodies):
        r[i] = r_abs[i] - r_cm # Fill the rows directly

    # get velocities WRT CM (non-relativistic)
    vel = np.zeros_like(vel_abs)
    vel[0] = vel_abs[0] # preserves velocity of CM across function calls
    for i in range(1, bodies):
        vel[i] = vel_abs[i] - vel_abs[0] # Fill the rows directly

    return r, vel, r_cm

# converts to absolute reference frame (absolute = origin)
def to_abs_ref(r, vel, r_cm):
    bodies = len(r)

    # get absolute positions
    r_abs = np.zeros_like(r)
    r_abs[0] = r[0] # preserves CM position across function calls
    for i in range(1, bodies):
        r_abs[i] = r[i] + r_cm + r[0]

    # get absolute velocities (non-relativistic)
    vel_abs = np.zeros_like(vel)
    vel_abs[0] = vel[0] # preserves value across function calls
    for i in range(1, bodies):
        vel_abs[i] = vel[i] + vel_abs[0]

    return r_abs, vel_abs

# gravity diff eq in CM reference
def fg(t, b1_old, bn_vals, mass):
    # b1_old = [ [x1, y1, z1], #these are the ones that will be modified
    #             [vx1, vy1, vz1] ]
    # bn_vals = [ [x2, y2, z2],   #B2
    #             [xn, yn, zn], ] #Bn
    # mass = [m1, m2, m3, ..., mn]

    def mag(vec): # returns magnitude of vec 
        sum = 0
        for e in vec:
            sum += e**2
        return np.sqrt(sum)

    #NOTE: Implement cases for when r = 0, so there is no divide by 0 error

    b1_next = np.zeros((2,3))

    b1_next[0] = b1_old[1]
    for i in range(len(mass)):
        b1_next[1] += -G*mass[i]*(b1_old[0] - bn_vals[i]) / (mag(b1_old[0] - bn_vals[i]))**3

    return b1_next

### def main():
d.__init__(1280, 720, 64*10, 36*10, trail_length=2)

initial_cm = initial.copy()
pos_next = np.zeros((bodies, 2, 3))
t_curr = 0
body_objects = []

for i in range(bodies):
    body = Body(x_0=initial[i+1, 0][0], y_0=initial[i+1, 0][1], trail_length=2)
    body_objects = np.append(body_objects, body)
    d.add_body(body)

def update(dt):
    global initial_cm, pos_next, t_curr

    if (t_curr > t_final):
        return

    d.start_frame()
    d.draw_axes()

    # switch to CM reference (update after movement)
    r_abs = initial[:,0]
    vel_abs = initial[:,1]
    mass = initial[1:,2][:,0] # leave row 0, col 2 of initial since it is acceleration values of CM  
    r, vel, r_cm = to_CM_ref(r_abs, vel_abs, mass)

    # NOTE: initial_cm still has un-changed initial[0] corresponding to CM_0 values WRT absolute reference frame
    initial_cm[:,0] = r
    initial_cm[:,1] = vel

    n = len(initial_cm) - 1 # number of bodies
    t = 0 
    for i in range(n):
        counter = 0

        # format data in the way fg() expects 
        b1_old = np.zeros((2,3))
        b1_old[0] = initial_cm[i+1, 0] # position of i-th body
        b1_old[1] = initial_cm[i+1, 1] # velocity of i-th body
        bn_mass = np.zeros(n-1)
        bn_vals = np.zeros((n-1,3))

        for j in range(n):
            if (i != j):
                bn_vals[counter] = initial_cm[j+1, 0]
                bn_mass[counter] = mass[j]
                counter += 1 

        # call rk to evaluate next pos for b1 (outside j-loop)
        t, b1_next = rk_single(fg, t_curr, b1_old, bn_vals, bn_mass)
        pos_next[i] = b1_next #1st column contains positions, and 2nd contains velocities

        # draw objects
        # print(pos_next[i, 0, 0], pos_next[i, 0, 1]) # DEBUG
        body_objects[i].move(pos_next[i, 0, 0], pos_next[i, 0, 1])
        d.draw_body(body_objects[i], i)
        d.draw_trail(body_objects[i], i, shift=1)

    d.end_frame()

    initial_cm[1:,0] = pos_next[:,0]
    initial_cm[1:,1] = pos_next[:,1]

    # switch to absolute reference frame
    r = initial_cm[:,0]
    vel = initial_cm[:,1]
    r_abs, vel_abs = to_abs_ref(r, vel, r_cm)

    # update initial with new values for next time step
    t_curr = t 
    initial[:,0] = r_abs
    initial[:,1] = vel_abs

pg.clock.schedule_interval(update, 1/fps)
d.__run__()
###
