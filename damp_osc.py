import numpy as np
import matplotlib.pyplot as plt
from rk import rk
import pyglet as pg
import draw as d

fps = 60

ord = 2

x_0 = 10
v_0 = 10

b = 0.2
m = 1
k = 1

xvec = np.array([x_0, v_0])

def f(t, xold):
    xnew = np.zeros(ord)
    xnew[0] = xold[1]
    xnew[1] = -b/m * xold[1] -k/m * xold[0]
    return xnew

t, y, iter = rk(f, 0, xvec, 20 * 60)

y = np.array(y)

d.__init__()

i = 0
def update(dt):
    global i
    
    if i >= len(t):
        return

    d.draw(0, y[:, 0][i])
    i += 1

pg.clock.schedule_interval(update, 1 / fps)
d.__run__()

# plt.plot(t, y[:, 0])
# plt.grid()
# plt.savefig("./damp_osc.png")
