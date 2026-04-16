import numpy as np 
from rk import *
import pyglet as pg 
import draw as d 
import matplotlib.pyplot as plt 

 # initial conditions for body 1, 2, 3 respectively
x_0 = np.array([1, 2, 3])
y_0 = np.array([1, 2, 3]) 
vx_0 = np.array([1, 2, 3])
vy_0 = np.array([1, 2, 3])
t_final = 10
m = np.array([10, 20, 30])

G = 1 # 6.674e-11

def f(t, pos, mass):
    # pos has row 0 = x and v_x
    #         row 1 = y and v_y
    # mass is 1-D with masses of 
    #                        B1      B2      B3 
    # pos_next = np.array([[ [0, 0], [0, 0], [0, 0] ], \
    #                      [ [0, 0], [0, 0], [0, 0] ]])
    #                       x, vx   y, vy 
    pos_next = np.array([ [[0, 0], [0, 0]], \ # B1
                          [[0, 0], [0, 0]] ]) # B2
    
    # in absolute reference frame (not from one of the bodies)
    x1_old, y1_old = pos[0][0], pos[0][1]
    x2_old, y2_old = pos[1][0], pos[1][1]

    x_old = np.abs(x1_old - x2_old)
    y_old = np.abs(y1_old - y2_old)

    # handles cases when x and y are 0, so its not undefined
    if (x_old[0] == 0) and (y_old[0] == 0):
        x_next[0] = x_old[1]
        x_next[1] = 0.0
    else: 
        x_next[0] = x_old[1]
        x_next[1] = -G*M*x_old[0] / ((x_old[0]**2 + y_old[0]**2)**1.5)
    

    return x_next

d.__init__(1280, 720, 64*10, 36*10, trail_length=2)

t_curr = 0 
# array with first row with x pos anc vel for the 3 bodies, and second row with y pos and vel
pos = np.array([[ [x_0[0], vx_0[0]], [x_0[1], vx_0[1]], [x_0[2], vx_0[2]] ], \
                [ [y_0[0], vy_0[0]], [y_0[1], vy_0[1]], [y_0[2], vy_0[2]] ]])

def update(dt):
    global t_curr, pos
    
