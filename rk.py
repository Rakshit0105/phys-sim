# Implementation of RK4
# Only works for single systems

def rk(f, t_i, y_i, t_f, h=0.1):
    y_0 = y_i
    t_0 = t_i
    t_final = t_f
    step_size = h 

    y = [y_0]
    t = [t_0]

    while (t[-1] < t_final):
        k_1 = f(t[-1], y[-1])
        k_2 = f(t[-1]+step_size/2, y[-1]+k_1*step_size/2)
        k_3 = f(t[-1]+step_size/2, y[-1]+k_2*step_size/2)
        k_4 = f(t[-1]+step_size, y[-1]+k_3*step_size)

        t_next = t[-1] + step_size
        y_next = y[-1] + step_size / 6 * (k_1 + 2*k_2 + 2*k_3 + k_4)
        t.append(t_next)
        y.append(y_next)
    
    return t, y, iter


def rk_single(f, t_i, y_i, t_f, h=0.1)
    y = y_i
    t = t_i
    t_final = t_f
    step_size = h 

    k_1 = f(t, y)
    k_2 = f(t+step_size/2, y+k_1*step_size/2)
    k_3 = f(t+step_size/2, y+k_2*step_size/2)
    k_4 = f(t+step_size, y+k_3*step_size)

    t_next = t + step_size
    y_next = y + step_size / 6 * (k_1 + 2*k_2 + 2*k_3 + k_4)
    
    return t_next, y_next
