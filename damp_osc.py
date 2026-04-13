import numpy as np
import matplotlib.pyplot as plt
from rk import rk

ord = 2

x_0 = 1
v_0 = 1

b = 0.2
m = 1
k = 1

xvec = np.array([x_0, v_0])

def f(t, xold):
    xnew = np.zeros(ord)
    xnew[0] = xold[1]
    xnew[1] = -b/m * xold[1] -k/m * xold[0]
    return xnew

t, y, iter = rk(f, 0, xvec, 100)

y = np.array(y)
plt.plot(t, y[:, 0])
plt.grid()
plt.savefig("./damp_osc.png")
