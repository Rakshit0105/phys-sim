# Currently has no rendering support 

import numpy as np
import matplotlib.pyplot as plt 

# SHO in 1-D
# d^2(x)/dt^2 = -k/m * x
def sho_diff(x_curr, v_curr, m, k, dt):
    v_curr += -k/m * x_curr * dt 
    x_curr += -k/m * x_curr * dt**2

    return x_curr, v_curr

# closed form sol. w/ v_0 = 0, x_0 = 0
def sho_solved(x_curr, v_curr, m, k, t):
    omega = np.sqrt(k/m)

    x = np.cos(omega * t) 
    v = -omega * np.sin(omega * t)

    return x, v

def main():
    x_0 = 0.0 
    v_0 = 0.0
    m = 1
    k = 1
   
    t = np.linspace(0, 100, 10000)
    x_exact, v_exact = sho_solved(x_0, v_0, m, k, t)

    dt = t[1]
    x_diff = [1.0]
    v_diff = [v_0]

    for i in range(len(t)-1):
        x_dt, v_dt = sho_diff(x_diff[-1], v_diff[-1], m, k, dt)
        x_diff.append(x_dt)
        v_diff.append(v_dt)
        # print(f"x: {x_diff[i]}, v: {v_diff[i]}, dt: {dt}")

    # plotting x values 
    
    # exact values
    plt.plot(t, x_exact, label="exact values")
    
    # diff eq values
    plt.plot(t, v_diff, label="diff eq values")

    plt.legend()
    plt.grid()
    plt.savefig("./spring.png")
        

main()
