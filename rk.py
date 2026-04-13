import numpy as np 
import matplotlib.pyplot as plt 

step_size = 0.01
y_0 = 1.0
t_0 = 0.5 
t_final = 5.0
num_iter = 0 

# dy/dt = y^2 
def f(t, y):
    return y*y 

y = [y_0]
t = [t_0]

while (t[-1] < t_final):
    k_1 = f(t[-1], y[-1])
    k_2 = f(t[-1]+step_size/2, y[-1]+k_1*step_size/2)
    k_3 = f(t[-1]+step_size/2, y[-1]+k_2*step_size/2)
    k_4 = f(t[-1]+step_size, y[-1]+k_3*step_size)

    t_next = t[-1] + step_size
    y_next = y[-1] + step_size / 6 * (k_1 + 2*k_2 + 2*k_3 + k_4)
    print(f"{t_next}, {y_next}")
    t.append(t_next)
    y.append(y_next)

    num_iter += 1 

def y_solved(t):
    return 1.0/(1.5-t)
t_arr = np.array(t)

plt.plot(t, y, label="rk-4")
plt.plot(t_arr, y_solved(t_arr), label="exact", linestyle="dashed")
plt.grid()
plt.legend()
plt.savefig("./rk.png")
