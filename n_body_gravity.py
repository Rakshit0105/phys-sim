import numpy as np 
import pyglet as pg 
import draw as d
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import sys
import copy

t_final = 1000
G = 1 # 6.674e-11
TICKS_PER_FRAME = 100 
t = []
e = []
p = []

# initial conditions: [ [x,y,z], [vx,vy,vz], [m, 0, 0] ] per row 

# The Montgomery-Chenciner Figure-8 Orbit
bodies = 3 
w = 5 # width of screen
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
    [ [97.000436, -24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B1
    [ [-97.000436, 24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B2
    [ [0.0, 0.0, 0.0], [-0.93240737, -0.86473146, 0], [100, 0, 0] ],               # B3
]) # Add B-n rows for the Bn-th body

# w = 25
# bodies = 11
# initial = np.array([
#     [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ],  # CM
#
#     # Central star, slightly offset so total position/momentum are near centered
#     [ [0.263386, -0.711634, 0], [0.006759, -0.042767, 0], [20000, 0, 0] ],  # B1 Star
#
#     # Inner planet + moon
#     [ [160.000000, 0.000000, 0], [0.000000, 11.180340, 0], [30, 0, 0] ],    # B2 Inner Planet
#     [ [172.000000, 0.000000, 0], [0.000000, 12.761479, 0], [1, 0, 0] ],     # B3 Inner Moon
#
#     # Gas giant + two moons
#     [ [340.000000, 0.000000, 0], [0.000000, 7.669650, 0], [120, 0, 0] ],    # B4 Gas Giant
#     [ [368.000000, 0.000000, 0], [0.000000, 9.739847, 0], [2, 0, 0] ],      # B5 Inner Giant Moon
#     [ [385.000000, 0.000000, 0], [0.000000, 9.302643, 0], [0.3, 0, 0] ],    # B6 Outer Giant Moon
#
#     # Gas giant Trojans near L4/L5
#     [ [170.000000, 294.448637, 0], [-6.642112, 3.834825, 0], [0.5, 0, 0] ], # B7 L4 Trojan
#     [ [170.000000, -294.448637, 0], [6.642112, 3.834825, 0], [0.5, 0, 0] ], # B8 L5 Trojan
#
#     # Outer planet + moon, placed at an angle for visual variety
#     [ [-610.800204, 222.313093, 0], [-1.897186, -5.212477, 0], [80, 0, 0] ], # B9 Outer Planet
#     [ [-631.473441, 229.837536, 0], [-2.549393, -7.004400, 0], [1.5, 0, 0] ],# B10 Outer Moon
#
#     # Distant ice body
#     [ [-450.000000, -779.422863, 0], [4.082483, -2.357023, 0], [5, 0, 0] ],  # B11 Ice Body
# ])

# bodies = 27 
# w = 300
#
# initial = np.array([
#     [ [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0] ],  # CM
#
#     # Sun
#     [ [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [333000.0, 0, 0] ], # B1 Sun
#
#     # Mercury (No moons)
#     [ [193.5, 0.0, 0.0], [0.0, 41.48, 0.0], [0.055, 0, 0] ], # B2 Mercury
#
#     # Venus (No moons)
#     [ [0.0, 361.5, 0.0], [-30.35, 0.0, 0.0], [0.815, 0, 0] ], # B3 Venus
#
#     # Earth + 1 moon
#     [ [-500.0, 0.0, 0.0], [0.0, -25.807, 0.0], [1.0, 0, 0] ], # B4 Earth
#     [ [-496.0, 0.0, 0.0], [0.0, -25.307, 0.0], [0.012, 0, 0] ], # B5 Moon
#
#     # Mars + 2 moons
#     [ [0.0, -762.0, 0.0], [20.90, 0.0, 0.0], [0.107, 0, 0] ], # B6 Mars
#     [ [0.0, -759.0, 0.0], [20.711, 0.0, 0.0], [0.000018, 0, 0] ], # B7 Phobos
#     [ [0.0, -767.0, 0.0], [21.046, 0.0, 0.0], [0.000024, 0, 0] ], # B8 Deimos
#
#     # Jupiter + 4 moons
#     [ [2602.0, 0.0, 0.0], [0.0, 11.31, 0.0], [318.0, 0, 0] ], # B9 Jupiter
#     [ [2620.0, 0.0, 0.0], [0.0, 15.51, 0.0], [0.015, 0, 0] ], # B10 Io
#     [ [2578.0, 0.0, 0.0], [0.0, 7.67, 0.0], [0.008, 0, 0] ], # B11 Europa
#     [ [2602.0, 32.0, 0.0], [-3.15, 11.31, 0.0], [0.025, 0, 0] ], # B12 Ganymede
#     [ [2602.0, -42.0, 0.0], [2.75, 11.31, 0.0], [0.018, 0, 0] ], # B13 Callisto
#     #
#     # Saturn + 5 moons
#     [ [0.0, 4791.0, 0.0], [-8.33, 0.0, 0.0], [95.0, 0, 0] ], # B14 Saturn
#     [ [12.0, 4791.0, 0.0], [-8.33, 2.81, 0.0], [0.000006, 0, 0] ], # B15 Mimas
#     [ [-16.0, 4791.0, 0.0], [-8.33, -2.43, 0.0], [0.000018, 0, 0] ], # B16 Enceladus
#     [ [0.0, 4811.0, 0.0], [-10.51, 0.0, 0.0], [0.0001, 0, 0] ], # B17 Tethys
#     [ [0.0, 4767.0, 0.0], [-6.34, 0.0, 0.0], [0.00018, 0, 0] ], # B18 Dione
#     [ [35.0, 4791.0, 0.0], [-8.33, 1.64, 0.0], [0.0225, 0, 0] ], # B19 Titan
#
#     # Uranus + 5 moons
#     [ [-9600.0, 0.0, 0.0], [0.0, -5.89, 0.0], [14.5, 0, 0] ], # B20 Uranus
#     [ [-9593.0, 0.0, 0.0], [0.0, -4.45, 0.0], [0.000011, 0, 0] ], # B21 Miranda
#     [ [-9610.0, 0.0, 0.0], [0.0, -7.09, 0.0], [0.00022, 0, 0] ], # B22 Ariel
#     [ [-9600.0, 13.0, 0.0], [-1.05, -5.89, 0.0], [0.00021, 0, 0] ], # B23 Umbriel
#     [ [-9600.0, -18.0, 0.0], [0.89, -5.89, 0.0], [0.00059, 0, 0] ], # B24 Titania
#     [ [-9576.0, 0.0, 0.0], [0.0, -5.12, 0.0], [0.0005, 0, 0] ], # B25 Oberon
#
#     # Neptune + 1 moon
#     [ [0.0, -15025.0, 0.0], [4.70, 0.0, 0.0], [17.1, 0, 0] ], # B26 Neptune
#     [ [0.0, -15011.0, 0.0], [5.80, 0.0, 0.0], [0.0035, 0, 0] ], # B27 Triton (retrograde)
# ])

# switch to CM reference frame
def to_CM_ref(body_objects, CM_object, only_compute_CM=False):
    r_abs = body_objects['position'] # pos WRT abs ref frame
    mass = body_objects['mass']

    # calculate center of mass 
    r_cm = np.zeros(3) # [x_cm, y_cm, z_cm] 
    for i in range(3):
        r_cm[i] = np.dot(r_abs[:, i], mass) / np.sum(mass) 

    CM_object['position'] += r_cm 

    if only_compute_CM:
        return CM_object['position']

    # body is in abs ref frame before this 
    for body in body_objects:
        # r_abs to r_cm
        body['position'] -= r_cm

        # v_abs to v_cm 
        body['velocity'] -= CM_object['velocity']

# switch to absolute ref frame (absolute = origin)
def to_abs_ref(body_objects, CM_object):
    # body is in CM ref frame before this 
    for body in body_objects:
        # r_cm to r_abs 
        body['position'] += CM_object['position']

        # v_cm to v_abs 
        body['velocity'] += CM_object['velocity']

# returns magnitude of vector
def vec_mag(vec):
    sum = 0
    for e in vec:
        sum += e**2
    return np.sqrt(sum)


def acceleration(body_objects, body_index):
    a = np.zeros(3) # [ax, ay, az]
    for i in range(len(body_objects)):
        if i != body_index:
            delta_r = body_objects[i]['position'] - body_objects[body_index]['position']

            # handle collision
            if (vec_mag(delta_r) < body_objects[i]['radius'] + body_objects[body_index]['radius']):
                # e_i = ENERGY
                # e_f = total_kinetic_energy(body_objects) + total_potential_energy(body_objects)
                # p_i = MOMENTUM
                # p_f = total_momentum(body_objects)
                #
                # # DEBUG: 
                # print(f"p_i: {p_i};    p_curr: {p_f}")
                # print(f"e_i: {e_i};    e_curr: {e_f}")
                continue
            a += G*body_objects[i]['mass']*delta_r / vec_mag(delta_r)**3 

    return a 

def calculate_position_verlet(body_objects, t_i, h=0.005):
    body_objects_next = copy.deepcopy(body_objects)
    t_next = 0
    for body_index in range(len(body_objects_next)):
        body = body_objects_next[body_index]
        body['velocity'] += h/2 * acceleration(body_objects_next, body_index) # half step

    for body_index in range(len(body_objects_next)):
        body = body_objects_next[body_index]
        body['position'] = body['position'] + h * body['velocity'] 

    for body_index in range(len(body_objects_next)):
        body = body_objects_next[body_index]
        body['velocity'] += h/2 * acceleration(body_objects_next, body_index) # full step

    t_next = t_i + h

    return t_next, body_objects_next


# struct datatype
dt = np.dtype([('position', np.float64, (3,)), 
               ('velocity', np.float64, (3,)), 
               ('acceleration', np.float64, (3,)),
               ('jerk', np.float64, (3,)),
               ('mass', np.float64),
               ('radius', np.float64),
               ('color', np.uint8, (3,)),
               ])

# initialize bodies 
def calculate_radius(mass):
    if mass <= 0:
        return 1.0

    r = (mass ** (1/3)) * 2.0
    
    # Clamp between 1.0 and 30.0
    return max(1.0, min(30.0, r))

t_curr = 0
body_objects_list = []

CM_object = np.array((initial[0,0], initial[0,0], [0,0,0], [0,0,0], 0, 0, [0,0,0]), dtype=dt)
for i in range(bodies):
    color = np.random.randint(100, 256, 3)
    mass = initial[i+1, 2][0]
    body = np.array((initial[i+1, 0],
                initial[i+1, 1],
                [0,0,0],
                [0,0,0],
                mass,
                # radius=min((initial[i+1,2][0]**0.3333 * 4), 25),
                calculate_radius(mass),
                color),
                dtype=dt
                )
    # print(body.radius)
    body_objects_list.append(body)

body_objects_list = np.array(body_objects_list)

to_CM_ref(body_objects_list, CM_object)

def update(dt):
    global body_objects_list, CM_object, t_curr

    if (t_curr > t_final):
        sys.exit(0)

    d.start_frame()
    # print("FRAME", t_curr, "dt =", dt)
    # compute next position
    # t_next, body_objects_next = calculate_position_rk(body_objects_list, t_curr)
    t_next, body_objects_next = calculate_position_verlet(body_objects_list, t_curr)

    # prep for next loop 
    t_curr = t_next
    body_objects_list = copy.deepcopy(body_objects_next)

    to_abs_ref(body_objects_next, CM_object)

    # draw bodies in abs ref frame 
    for body in body_objects_next:
        d.draw(
            x_pos=body['position'][0],
            y_pos=body['position'][1],
            z_pos=body['position'][2],
            color=tuple(body['color']),
            radius=body['radius'],
        )
        # print(body.position)

    d.end_frame()

def panda_update(dt):
    for _ in range(TICKS_PER_FRAME):
        update(dt)

if __name__ == "__main__":
    d.init(1920, 1080, 64*w, 36*w)
    d.__run__(panda_update)
