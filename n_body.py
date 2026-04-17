import numpy as np 
# from rk import * 
import pyglet as pg 
import draw as d 
from body import Body 

bodies = 3 # number of bodies
# initial conditions: [ [x, y, z], [v_x, v_y, v_z], [m] ] per row 
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ] # initial conditions for center of mass
    [ [x1, y1, z1], [vx1, vy1, vz1], [m1, 0, 0] ], # B1 values, and using 0's for mass values to have homogenous array, or np throws an error
    [ [x2, y2, z2], [vx2, vy2, vz2], [m2, 0, 0] ], # B2   " 
    [ [x3, y3, z3], [vx3, vy3, vz3], [m3, 0, 0] ], # B3   "
]) # Add B-n rows for the Bn-th body
t_final = 100

G = 1 # 6.674e-11
fps = 60

def main():


    # WARNING: put the below in the update loop

    # switch to CM reference
    r_abs = initial[:,0]
    vel_abs = initial[:,1]
    mass = initial[1:,2][:,0] # leave row 0, col 2 of initial since it is acceleration values of CM  
    r, vel, r_cm = to_CM_ref(r_abs, vel_abs, mass)

    initial[:,0] = r
    initial[:,1] = vel


# converts to center of mass reference frame (or computes CM only)
def to_CM_ref(r_abs, vel_abs, mass, CM_only=False):
    bodies = len(r_abs) # number of true bodies + 1 

    # calculate center of mass
    r_cm = np.zeros(3) # [x_cm, y_cm, z_cm]
    for i in range(3):
        r_cm[i] = np.dot(r_abs[:,i+1], mass) / np.sum(mass) # i+1 to leave out CM values

    if CM_only:
        return r_cm 

    # get positions WRT CM
    r = np.zeros(bodies)
    # NOTE: not sure if r[0] should be r_cm or r_abs[0]; and whether r[i] should depend on r_abs[0]
    r[0] = r_abs[0] # preserves position of CM across function calls
    for i in range(1, bodies+1):
        r[i] = r_abs[i] - r_cm

    # get velocities WRT CM (non-relativistic)
    vel = np.zeros(bodies)
    vel[0] = vel_abs[0] # preserves velocity of CM across function calls
    for i in range(1, bodies+1):
        vel[i] = vel_abs[i] - vel[0]

    return r, vel, r_cm

# converts to absolute reference frame (absolute = origin)
def to_abs_ref(r, vel, r_cm):
    bodies = len(r)

    # get absolute positions
    r_abs = np.zeros(bodies)
    r_abs[0] = r[0] # preserves CM position across function calls
    for i in range(1, bodies+1):
        r_abs[i] = r[i] + r_cm + r[0]

    # get absolute velocities (non-relativistic)
    vel_abs = np.zeros(bodies)
    vel_abs[0] = vel[0] # preserves value across function calls
    for i in range(1, bodies+1):
        vel_abs[i] = vel[i] + vel_abs[0]

    return r_abs, vel_abs

# WARNING: Unsure what the best way is to implement rk and fg in this case (with these conditions)

# gravity diff eq in CM reference
def fg(t, conditions, extra):
    conditions_next = conditions.copy()
    r = conditions[1:,0] # positions of the bodies WRT CM (leaving out CM values)
    vel = conditions[1:,1] # velocities of the bodies WRT CM (leaving out CM)
    mass = conditions[1:,2][:,0] # masses of the bodies (leaving out CM acceleration)

   
def rk_custom(f, t_i, conditions, h=0.01):
    conditions_next = conditions.copy()
    r = conditions[1:,0] # positions of the bodies WRT CM (w/o CM values)
    vel = conditions[1:,1] # velocities of the bodies WRT CM (w/o CM)
    mass = conditions[1:,2][:,0] # masses of the bodies (w/o CM acceleration)

    
