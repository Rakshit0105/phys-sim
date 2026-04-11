import numpy as np 

t_i = 0 # seconds
t_f = 5 # seconds
y_0 = 10 # m 
x_0 = 0 # m
v_yi = 2 # m/s 
v_xi = 0 # m/s
g = 9.81 # m/s^2

t = np.linspace(t_i, t_f, 10) # change the number of time steps

def x(t):
    return v_xi*t + x_0

def y(t):
    return -0.5*g*t**2 + v_yi*t + y_0

x_pos, y_pos = x(t), y(t)

for i in range(np.size(t)):
    if x_pos[i] < 0:
        x_pos[i] = 0 
    if y_pos[i] < 0:
        y_pos[i] = 0

    print(f"t={round(t[i], 2)}: x={round(x_pos[i], 2)}, y={round(y_pos[i], 2)}")
