import numpy as np
from rk import * 
import pyglet as pg
import draw as d
import matplotlib.pyplot as plt

# d^2/dt^2 (r) = GM/r^2
x_0 = 30 
y_0 = 60
vx_0 = -0.5 
vy_0 = -0.3
t_final = 100000
G = 1 # 6.674e-11
M = 20

fps = 60*10

x = np.array([x_0, vx_0])
y = np.array([y_0, vy_0])

def f(t, x_old, y_old):
    x_next = np.zeros(2)
    
    # handles cases when x and y are 0, so its not undefined
    if (x_old[0] == 0) and (y_old[0] == 0):
        x_next[0] = x_old[1]
        x_next[1] = 0.0

        print(x_next)
        return x_next 

    x_next[0] = x_old[1]
    x_next[1] = -G*M*x_old[0] / ((x_old[0]**2 + y_old[0]**2)**1.5)

    # print(x_old, x_next)

    return x_next

d.__init__(1280, 720, 64*10, 36*10)

t_curr = 0
x_pos = []
y_pos = [] 
t_list = []
def update(dt):
    global t_curr, x, y
    
    if t_curr >= t_final:
        return
    
    d.start_frame()
    d.draw_axes()

    d.draw_trail(x[0], y[0])
    # d.draw(x[0], y[0])

    d.end_frame()

    # for plotting only
    x_pos.append(x[0])
    y_pos.append(y[0])
    t_list.append(t_curr)

    # print(f"t: {round(t_curr, 3)};    x: {round(x[0], 4)};    y: {round(y[0], 4)};    v_x: {round(x[1], 4)};    v_y: {round(y[1], 4)}")
    
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

plt.plot(x_pos, y_pos)
plt.grid()
plt.savefig("./one_body.png")
