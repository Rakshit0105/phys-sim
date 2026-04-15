import numpy as np
import matplotlib.pyplot as plt
from rk import *
import pyglet as pg
import draw as d

fps = 60

ord = 2

x_0 = 10
v_0 = -10

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

d.__init__()

t_curr = 0 
def update(dt):
    global t_curr, xvec 
    
    if t_curr >= 20:
        return

    d.draw(0, xvec[0])

    t, y_next = rk_single(f, t_curr, xvec, 0)

    xvec = np.array(y_next)

    
    # print(y[:,1][i])

pg.clock.schedule_interval(update, 1 / fps)
d.__run__()

# plt.plot(t, y[:, 0])
# plt.grid()
# plt.savefig("./damp_osc.png")
