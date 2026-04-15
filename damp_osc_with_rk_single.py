import numpy as np
import matplotlib.pyplot as plt
from rk import *
import pyglet as pg
import draw as d

fps = 60

ord = 2

x_0 = 18
v_0 = -1

b = 0.2
m = 1
k = 1

xvec = np.array([x_0, v_0])

def f(t, xold, temp):
    xnew = np.zeros(ord)
    xnew[0] = xold[1]
    xnew[1] = -b/m * xold[1] -k/m * xold[0]
    return xnew

# t, y = rk(f, 0, xvec, 20 * 60)

# y = np.array(y)

d.__init__(1280, 720, 64, 36, trail_length=3)

t_curr = 0
t_list = []
y_pos = []

def update(dt):
    global t_curr, xvec 
    
    if t_curr >= 20:
        return
    
    t_list.append(t_curr)
    y_pos.append(xvec[0])
    
    d.start_frame()
    d.draw_axes()
    d.draw_trail(0, xvec[0]) 
    d.draw_trail(xvec[0], 0)
    d.end_frame()

    t, y_next = rk_single(f, t_curr, xvec, 0)
    
    xvec = np.array(y_next)
    t_curr = t 

pg.clock.schedule_interval(update, 1 / fps)
d.__run__()

# plt.plot(t_list, y_pos)
# plt.xlabel("time")
# plt.ylabel("y-pos")
# plt.grid()
# plt.savefig("./dampened_oscillator.png")
