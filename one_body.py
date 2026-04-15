import numpy as np
from rk import * 
import pyglet as pg
import draw as d

# d^2/dt^2 (r) = GM/r^2
x_0 = 10
y_0 = 3
vx_0 = 4 
vy_0 = 1 
t_final = 5
G = 1 #6.674e-11
M = 1

fps = 60

x = np.array([x_0, vx_0])
y = np.array([y_0, vy_0])

def f(t, x_old, y_old):
    x_next = np.zeros(2)
    x_next[0] = x_old[1]
    x_next[1] = G*M*x_old[0] / (x_old[0]**2 + y_old[0]**2)**1.5

    return x_next

def fy(t, y_old, x_old):
    y_next = np.zeros(2)
    y_next[0] = y_old[1]
    y_next[1] = G*M*y_old[0] / (y_old[0]**2 + x_old[0]**2)**1.5

    return y_next

def test():
    t_curr = 0
    while (t_curr < t_final):
        t, x_next = rk_single(f, t_curr, x, y)
        t, y_next = rk_single(f, t_curr, y, x)
        t_curr = t # proceed to next step
        
        x_next = np.array(x_next)
        y_next = np.array(y_next)

        # updates the pos and vel to next values
        x = x_next 
        y = y_next
        
        print(f"t: {round(t_curr, 3)};    x: {round(x[0], 4)};    y: {round(y[0], 4)}")

t_curr = 0 
def update(dt):
    global t_curr, x, y
    
    if t_curr >= t_final:
        return

    d.draw(x[0], y[0])

    t, x_next = rk_single(f, t_curr, x, y)
    t, y_next = rk_single(f, t_curr, y, x)
    t_curr = t # proceed to next step
    
    x_next = np.array(x_next)
    y_next = np.array(y_next)

    # updates the pos and vel to next values
    x = x_next 
    y = y_next

pg.clock.schedule_interval(update, 1/fps)
d.__run__()
