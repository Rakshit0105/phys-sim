import numpy as np 
import pyglet as pg 
import draw as d 
from body import Body 
import copy

t_final = 10000
G = 1 # 6.674e-11
tick = 60*10 # fps / tick rate 

# initial conditions: [ [x,y,z], [vx,vy,vz], [m, 0, 0] ] per row 

# The Montgomery-Chenciner Figure-8 Orbit
bodies = 3
# w = 5 # width of screen
# initial = np.array([
#     [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
#     [ [97.000436, -24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B1
#     [ [-97.000436, 24.308753, 0], [0.466203685, 0.432365730, 0], [100, 0, 0] ], # B2
#     [ [0.0, 0.0, 0.0], [-0.93240737, -0.86473146, 0], [100, 0, 0] ],               # B3
# ]) # Add B-n rows for the Bn-th body

### 3-body  test with 1 collision and 1 in orbit
# w = 5
# initial = np.array([
#     [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM
#     [ [97, 29, 0], [0.35, -0.8,  0], [1000, 0, 0] ], # B1
#     [ [192, -84, 0], [-0.3, 0.2, 0], [1000, 0, 0] ], # B2
#     [ [0.0, 0.0, 0.0], [-0.3, -1.8, 0], [100, 0, 0] ],               # B3
# ])
###

### Stable-ish hierarchical system with Trojans and moons.
# w = 25
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
###

###
# Collision into stable planet orbit
# Two equal chunks collide near x=300.
# After merging, they behave like one m=100 planet with v ~= sqrt(10000 / 300) = 5.7735.
bodies = 3
w = 15
initial = np.array([
    [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ], # CM

    [ [0, 0, 0], [0, -0.057735, 0], [10000, 0, 0] ], # Star

    [ [300, -120, 0], [0, 11.7735, 0], [50, 0, 0] ], # Planet chunk 1
    [ [300,  120, 0], [0, -0.2265, 0], [50, 0, 0] ], # Planet chunk 2
])
###

def to_CM_ref(body_objects, CM_object, only_compute_CM=False):
    r_abs = [] # pos WRT abs ref frame
    mass = []

    for body in body_objects:
        r_abs.append(body.position)
        mass.append(body.mass)

    r_abs = np.array(r_abs)
    mass = np.array(mass)

    # calculate center of mass 
    r_cm = np.zeros(3) # [x_cm, y_cm, z_cm] 
    for i in range(3):
        r_cm[i] = np.dot(r_abs[:, i], mass) / np.sum(mass) 

    CM_object.position = r_cm 

    if only_compute_CM:
        return r_cm

    # body is in abs ref frame before this 
    for body in body_objects:
        # r_abs to r_cm
        body.position -= r_cm

        # v_abs to v_cm 
        body.velocity -= CM_object.velocity

    return body_objects, CM_object

# converts to absolute ref frame (absolute = origin)
def to_abs_ref(body_objects, CM_object):
    # body is in CM ref frame before this 
    for body in body_objects:
        # r_cm to r_abs 
        body.position += CM_object.position

        # v_cm to v_abs 
        body.velocity += CM_object.velocity

    return body_objects

# returns magnitude of vector
def vec_mag(vec):
    sum = 0
    for e in vec:
        sum += e**2
    return np.sqrt(sum)

# returns potential energy of bodies in CM ref frame 
def total_potential_energy(body_objects):
    # body is (assumed to be) in CM ref frame 
    potential = 0
    for i in range(len(body_objects)):
        for j in range(i + 1, len(body_objects)):
            delta_r = vec_mag(body_objects[i].position - body_objects[j].position)

            # if bodies have collided, potential b/w those is 0
            if (delta_r < (body_objects[i].radius + body_objects[j].radius)):
                continue

            potential += -G * body_objects[i].mass * body_objects[j].mass / delta_r 

    return potential

# returns potential energy of a single body in CM ref frame (copied from above)
def potential_energy_single(body_objects, body_index):
    i = body_index
    potential = 0
    for j in range(len(body_objects)):
        if i != j:
            delta_r = vec_mag(body_objects[i].position - body_objects[j].position)

            # if bodies have collided, potential b/w those is 0
            if (delta_r < (body_objects[i].radius + body_objects[j].radius)):
                continue

            potential += -G * body_objects[i].mass * body_objects[j].mass / delta_r 

    return potential

# returns kinetric energy in CM ref frame 
def total_kinetic_energy(body_objects):
    # body is (assumed to be) in CM ref frame 
    kinetic = 0
    for body in body_objects:
        kinetic += 0.5 * body.mass * (vec_mag(body.velocity))**2

    return kinetic 

# kinetic energy of a single body in CM ref frame 
def kinetic_energy_single(body_objects, body_index):
    i = body_index
    return 0.5 * body_objects[i].mass * (vec_mag(body_objects[i].velocity))**2

# total momentum in CM ref frame 
def total_momentum(body_objects):
    momentum = np.zeros(3) # [px, py, pz]
    for body in body_objects:
        momentum += body.mass * body.velocity

    return momentum

# gravity diff eq in CM reference
def fg(t, body_objects, body, body_index):
    # body whose positin velocity are being updated 
    body_new = copy.deepcopy(body)

    # order reduction
    body_new.position = body.velocity.copy()
    body_new.velocity = np.zeros(3)

    for i in range(len(body_objects)):
        if i != body_index:
            delta_r = body.position - body_objects[i].position
            delta_r_mag = vec_mag(delta_r)

            # handles collision
            if (delta_r_mag < (body.radius + body_objects[i].radius)):
                # create handle collision function
                # body_new.position
                body_new.velocity += body_objects[i].velocity
                collide = True
                continue

            body_new.velocity += -G*body_objects[i].mass*delta_r / (delta_r_mag)**3

    return body_new

def rk_single(f, t, body_objects, body_index, h=0.005):
    body_0 = copy.deepcopy(body_objects[body_index])

    # k_1 ... k_4 are body objects 
    k_1 = f(t, body_objects, body_0, body_index)

    body = copy.deepcopy(body_0)
    body.position = body_0.position + k_1.position*h/2
    body.velocity = body_0.velocity + k_1.velocity*h/2 
    k_2 = f(t+h/2, body_objects, body, body_index)

    body = copy.deepcopy(body_0)
    body.position = body_0.position + k_2.position*h/2
    body.velocity = body_0.velocity + k_2.velocity*h/2
    k_3 = f(t+h/2, body_objects, body, body_index)

    body = copy.deepcopy(body_0)
    body.position = body_0.position + k_3.position*h
    body.velocity = body_0.velocity + k_3.velocity*h
    k_4 = f(t+h, body_objects, body, body_index)

    t_next = t + h
    body_next = copy.deepcopy(body_objects[body_index])
    body_next.position = body_0.position + h / 6 * (k_1.position + 2*k_2.position + 2*k_3.position + k_4.position)
    body_next.velocity = body_0.velocity + h / 6 * (k_1.velocity + 2*k_2.velocity + 2*k_3.velocity + k_4.velocity)

    return t_next, body_next
# rescales velocities to conserve total energy
def correct_energy(body_objects, ENERGY, MOMENTUM):
    potential = total_potential_energy(body_objects)

    total_mass = 0
    for body in body_objects:
        total_mass += body.mass

    v_cm = MOMENTUM / total_mass

    kinetic_cm = 0.5 * total_mass * vec_mag(v_cm)**2
    kinetic_relative = 0

    for body in body_objects:
        v_rel = body.velocity - v_cm
        kinetic_relative += 0.5 * body.mass * vec_mag(v_rel)**2

    kinetic_relative_target = ENERGY - potential - kinetic_cm

    # If target kinetic is impossible, skip correction.
    # This can happen if the timestep is too large or bodies get too close.
    if kinetic_relative <= 0:
        return body_objects

    if kinetic_relative_target <= 0:
        return body_objects

    scale = np.sqrt(kinetic_relative_target / kinetic_relative)

    for body in body_objects:
        v_rel = body.velocity - v_cm
        body.velocity = v_cm + scale * v_rel

    return body_objects

# calculates next position based on 
def calculate_position(body_objects, t_i, ENERGY, MOMENTUM):
    # U_old >= U_new
    # U_old - U_new = K_new - K_old 
    # sqrt(2/m * U_old - U_new) = v_new
    body_objects_next = []
    t_next = -1
    p_i = MOMENTUM

    for body_index in range(len(body_objects)):
        t_next, body_next = rk_single(fg, t_i, body_objects, body_index)
        body_objects_next.append(body_next)

    body_objects_next = np.array(body_objects_next)
    p_f = total_momentum(body_objects_next)

    # rescale all vectors with the momentum ratio for conservation of momentum
    # NOTE: do not use |p_i| / |p_f| here; for zero-momentum systems this zeros all velocities
    total_mass = 0
    for body in body_objects_next:
        total_mass += body.mass

    p_error = p_f - p_i
    for body in body_objects_next:
        body.velocity -= p_error / total_mass

    if not collide:
        body_objects_next = correct_energy(body_objects_next, ENERGY, MOMENTUM)

    p_f = total_momentum(body_objects_next)

    e_i = ENERGY
    e_f = total_kinetic_energy(body_objects_next) + total_potential_energy(body_objects_next)
    # DEBUG: 
    print(f"p_i: {p_i};    p_curr: {p_f}")
    print(f"e_i: {e_i};    e_curr: {e_f}")

    return t_next, body_objects_next, ENERGY, MOMENTUM

# d.__init__(1280, 720, 64*w, 36*w)
d.__init__(720, 720, 36*w, 36*w)

# initialize bodies 
t_curr = 0
body_objects = []

CM_object = Body(position=initial[0,0], velocity=initial[0,1])
for i in range(bodies):
    color = np.random.randint(0, 256, 3)
    color = tuple(color)
    body = Body(
        position=initial[i+1, 0],
        velocity=initial[i+1, 1],
        mass=initial[i+1, 2][0],
        color=color,
        radius=max(2, initial[i+1, 2][0] ** 0.33333333333 * 5),
    )
    # print(type(body.position), type(CM_object.position))
    body_objects.append(body)

body_objects = np.array(body_objects)
# print(type(body_objects[1].position), type(initial[1, 0]))
ENERGY = total_kinetic_energy(body_objects) + total_potential_energy(body_objects)
MOMENTUM = total_momentum(body_objects)

body_objects, CM_object = to_CM_ref(body_objects, CM_object)

def update(dt):
    global MOMENTUM, ENERGY, body_objects, t_curr, collide

    if (t_curr > t_final):
        return

    d.start_frame()

    collide = False
    t_next, body_objects_next, ENERGY, MOMENTUM = calculate_position(body_objects, t_curr, ENERGY, MOMENTUM)
    t_curr, body_objects = t_next, body_objects_next

    # ABSOLUTE REFERENCE BODY OBJECTS
    absolute_objects = to_abs_ref(copy.deepcopy(body_objects), CM_object)
    for body in absolute_objects:
        d.draw(
            x_pos=body.position[0],
            y_pos=body.position[1],
            color=body.color,
            radius=body.radius
        )

    d.end_frame()

# pg.clock.schedule_interval(update, 1/tick)
# d.__run__()
if __name__ == "__main__":
    pg.clock.schedule_interval(update, 1/tick)
    d.__run__()
