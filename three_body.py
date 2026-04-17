import numpy as np 
from rk import *
import pyglet as pg 
import draw as d 
import matplotlib.pyplot as plt
from body import Body

# initial conditions for body 1, 2, 3 respectively
n = 10
x_0 = np.array([40*3, 0, 0], dtype=float)
y_0 = np.array([0, 30*3, 0], dtype=float)
vx_0 = np.array([0, 0, 0.1], dtype=float)
vy_0 = np.array([0, 0, 0], dtype=float)
m = np.array([3*n, 4*n, 5*n], dtype=float)
G = 1 # 6.674e-11

# G = 1.0
# m = np.array([10000.0, 10000.0, 10000.0], dtype=float)
# a = 300.0
# R = a / np.sqrt(3.0)         # distance from center
# v = np.sqrt(G * m[0] / a)    # speed
#
# x_0  = np.array([ R,   -R/2,   -R/2 ], dtype=float)
# y_0  = np.array([ 0.0,  a/2,   -a/2  ], dtype=float)
#
# vx_0 = np.array([ 0.0, -np.sqrt(3)/2 * v,  np.sqrt(3)/2 * v ], dtype=float)
# vy_0 = np.array([ v,   -0.5 * v,          -0.5 * v          ], dtype=float)

fps = 60*20
t_final = 1000

def f(t, pos, mass):
    #                       x, vx   y, vy 
    # pos_next = np.array([ [[0, 0], [0, 0]], \ # B1
    #                       [[0, 0], [0, 0]], \ # B2
    #                       [[0, 0], [0, 0]] ]) # B3    

    pos_next = pos.copy().astype(float)

    # in absolute reference frame (not from one of the bodies)
    x1_old, y1_old = pos[0][0], pos[0][1]
    x2_old, y2_old = pos[1][0], pos[1][1]
    x3_old, y3_old = pos[2][0], pos[2][1]

    x12_old = np.zeros(2)
    y12_old = np.zeros(2)

    # reference frame with respect to b1
    x12_old[0] = x2_old[0] - x1_old[0]
    y12_old[0] = y2_old[0] - y1_old[0]

    x12_norm = np.array([x12_old[0], y12_old[0]])
    x12_norm = x12_norm / np.linalg.norm(x12_norm)

    x12_old[1], y12_old[1] = np.dot( \
        np.array([x1_old[1], y1_old[1]]), \
        x12_norm \
    ) * x12_norm

    x13_old = np.zeros(2)
    y13_old = np.zeros(2)

    # reference frame with respect to b1
    x13_old[0] = x3_old[0] - x1_old[0]
    y13_old[0] = y3_old[0] - y1_old[0]
    
    x13_norm = np.array([x13_old[0], y13_old[0]])
    x13_norm = x13_norm / np.linalg.norm(x13_norm)

    x13_old[1], y13_old[1] = np.dot( \
        np.array([x1_old[1], y1_old[1]]), \
        x13_norm \
    ) * x13_norm

    # x12_old[1] = x2_old[1] - x1_old[1]
    # y12_old[1] = y2_old[1] - y1_old[1]
    #
    # x13_old[1] = x3_old[1] - x1_old[1]
    # y13_old[1] = y3_old[1] - y1_old[1]

    # handles cases when x and y are 0, so its not undefined
    x_next = np.zeros(2)
    if ((x12_old[0] <= 1e-2) and (y12_old[0] <= 1e-2)):
        x_next[0] = x12_old[1]
        x_next[1] = 0.0
    elif ((x13_old[0] <= 1e-2) and (y13_old[0] <= 1e-2)):
        x_next[0] = x13_old[1]
        x_next[1] = 0.0
    else: 
        x_next[0] = x12_old[1] + x13_old[1]
        x_next[1] = -G*mass[1]*x12_old[0] / ((x12_old[0]**2 + y12_old[0]**2)**1.5) \
                    + G*mass[2]*x13_old[0] / ((x13_old[0]**2 + y13_old[0]**2)**1.5)
    
    # x_next[0] += x1_old[0]

    y_next = np.zeros(2)
    if ((x12_old[0] <= 1e-2) and (y12_old[0] <= 1e-2)):
        y_next[0] = y12_old[1]
        y_next[1] = 0.0
    elif ((x13_old[0] <= 1e-2) and (y13_old[0] <= 1e-2)):
        y_next[0] = y13_old[1]
        y_next[1] = 0.0
    else: 
        y_next[0] = y12_old[1] + y13_old[1]
        y_next[1] = -G*mass[1]*y12_old[0] / ((y12_old[0]**2 + x12_old[0]**2)**1.5) \
                    + G*mass[2]*y13_old[0] / ((y13_old[0]**2 + x13_old[0]**2)**1.5)

    # y_next[0] += y1_old[0]

    pos_next[0][0] = np.array(x_next)
    pos_next[0][1] = np.array(y_next)

    return pos_next

d.__init__(1280, 720, 64*10, 36*10, trail_length=2)

t_curr = 0 
# array with first row with x pos anc vel for the 3 bodies, and second row with y pos and vel
pos = np.array([ [[x_0[0], vx_0[0]], [y_0[0], vy_0[0]]], \
                 [[x_0[1], vx_0[1]], [y_0[1], vy_0[1]]], \
                 [[x_0[2], vx_0[2]], [y_0[2], vy_0[2]]] ], dtype=float)

bodies = np.array([ \
    Body(x_0=x_0[0], y_0=y_0[0], trail_length=2), \
    Body(x_0=x_0[1], y_0=y_0[1], trail_length=2), \
    Body(x_0=x_0[2], y_0=y_0[2], trail_length=2), \
])

for body in bodies:
    d.add_body(body)

def update(dt):
    global t_curr, pos

    if t_curr >= t_final:
        return

    d.start_frame()
    d.draw_axes()

    real_pos_next = pos.copy()
    for i in range(3):
        this_pos = np.roll(pos, shift=-i, axis=0)
        this_mass = np.roll(m, shift=-i)
        t, pos_next = rk_single(f, t_curr, this_pos, this_mass)
        real_pos_next[i] = np.array(pos_next[0], dtype=float)

        bodies[i].move(pos_next[0][0][0], pos_next[0][1][0])
        d.draw_body(bodies[i], i)
        d.draw_trail(bodies[i], i, shift=1)

        if i == 2:
            t_curr = t

    d.end_frame()

    pos = real_pos_next

pg.clock.schedule_interval(update, 1/fps)
d.__run__()
