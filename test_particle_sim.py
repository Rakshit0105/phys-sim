import numpy as np
import pyglet as pg
import draw as d
import sys

from numba import njit, prange


t_final = 500
TICKS_PER_FRAME = 10

# Simulation settings
bodies = 250
w = 20

TIME_STEP = 0.05
PARTICLE_RADIUS = 5.0
PARTICLE_MASS = 1.0
PARTICLE_SPEED = 120.0

WORLD_WIDTH = 64 * w
WORLD_HEIGHT = 36 * w

BOX_LEFT = -WORLD_WIDTH / 2
BOX_RIGHT = WORLD_WIDTH / 2
BOX_BOTTOM = -WORLD_HEIGHT / 2
BOX_TOP = WORLD_HEIGHT / 2

COLLISION_PASSES = 3

CENTER_WALL_X = 0.0

HEAT_PUMP_HALF_HEIGHT = WORLD_HEIGHT * 0.08
HEAT_PUMP_LEFT_TO_RIGHT_MULT = 1.35
HEAT_PUMP_RIGHT_TO_LEFT_MULT = 0.75

START_NEAR_CORNER = False


@njit(cache=True, fastmath=True, parallel=True)
def drift_positions_parallel(positions, velocities, h):
    for i in prange(positions.shape[0]):
        positions[i, 0] += h * velocities[i, 0]
        positions[i, 1] += h * velocities[i, 1]
        positions[i, 2] += h * velocities[i, 2]


@njit(cache=True, fastmath=True, parallel=True)
def resolve_box_collisions_parallel(
    positions,
    velocities,
    radii,
    box_left,
    box_right,
    box_bottom,
    box_top
):
    for i in prange(positions.shape[0]):
        r = radii[i]

        if positions[i, 0] - r < box_left:
            positions[i, 0] = box_left + r
            if velocities[i, 0] < 0:
                velocities[i, 0] *= -1.0

        if positions[i, 0] + r > box_right:
            positions[i, 0] = box_right - r
            if velocities[i, 0] > 0:
                velocities[i, 0] *= -1.0

        if positions[i, 1] - r < box_bottom:
            positions[i, 1] = box_bottom + r
            if velocities[i, 1] < 0:
                velocities[i, 1] *= -1.0

        if positions[i, 1] + r > box_top:
            positions[i, 1] = box_top - r
            if velocities[i, 1] > 0:
                velocities[i, 1] *= -1.0


@njit(cache=True, fastmath=True, parallel=True)
def resolve_center_wall_and_heat_pump_parallel(
    positions,
    velocities,
    old_positions,
    radii,
    center_wall_x,
    heat_pump_half_height,
    left_to_right_mult,
    right_to_left_mult
):
    for i in prange(positions.shape[0]):
        old_x = old_positions[i, 0]
        new_x = positions[i, 0]
        r = radii[i]

        crossed_left_to_right = old_x < center_wall_x and new_x >= center_wall_x
        crossed_right_to_left = old_x > center_wall_x and new_x <= center_wall_x
        crossed_wall = crossed_left_to_right or crossed_right_to_left

        in_opening = abs(positions[i, 1]) < heat_pump_half_height - r

        # Heat pump opening
        if crossed_wall and in_opening:
            if crossed_left_to_right:
                velocities[i, 0] *= left_to_right_mult
                velocities[i, 1] *= left_to_right_mult
                velocities[i, 2] *= left_to_right_mult

            elif crossed_right_to_left:
                velocities[i, 0] *= right_to_left_mult
                velocities[i, 1] *= right_to_left_mult
                velocities[i, 2] *= right_to_left_mult

            continue

        # Solid center wall
        touching_wall = abs(positions[i, 0] - center_wall_x) < r

        if touching_wall and not in_opening:
            if old_x < center_wall_x:
                positions[i, 0] = center_wall_x - r

                if velocities[i, 0] > 0:
                    velocities[i, 0] *= -1.0

            else:
                positions[i, 0] = center_wall_x + r

                if velocities[i, 0] < 0:
                    velocities[i, 0] *= -1.0


@njit(cache=True, fastmath=True)
def apply_elastic_collision_impulses_serial(
    positions,
    velocities,
    masses,
    radii
):
    n = positions.shape[0]

    for i in range(n):
        for j in range(i + 1, n):
            dx = positions[j, 0] - positions[i, 0]
            dy = positions[j, 1] - positions[i, 1]
            dz = positions[j, 2] - positions[i, 2]

            min_distance = radii[i] + radii[j]
            distance_squared = dx * dx + dy * dy + dz * dz

            if distance_squared < min_distance * min_distance:
                if distance_squared < 1e-20:
                    distance = 0.0
                    nx = 1.0
                    ny = 0.0
                    nz = 0.0
                else:
                    distance = np.sqrt(distance_squared)
                    inv_distance = 1.0 / distance
                    nx = dx * inv_distance
                    ny = dy * inv_distance
                    nz = dz * inv_distance

                overlap = min_distance - distance

                inv_mass_i = 1.0 / masses[i]
                inv_mass_j = 1.0 / masses[j]
                inv_mass_sum = inv_mass_i + inv_mass_j

                correction_amount = overlap / inv_mass_sum

                positions[i, 0] -= nx * correction_amount * inv_mass_i
                positions[i, 1] -= ny * correction_amount * inv_mass_i
                positions[i, 2] -= nz * correction_amount * inv_mass_i

                positions[j, 0] += nx * correction_amount * inv_mass_j
                positions[j, 1] += ny * correction_amount * inv_mass_j
                positions[j, 2] += nz * correction_amount * inv_mass_j

                rvx = velocities[j, 0] - velocities[i, 0]
                rvy = velocities[j, 1] - velocities[i, 1]
                rvz = velocities[j, 2] - velocities[i, 2]

                velocity_along_normal = rvx * nx + rvy * ny + rvz * nz

                if velocity_along_normal > 0:
                    continue

                # Perfect elastic collision: restitution = 1
                impulse_magnitude = -2.0 * velocity_along_normal
                impulse_magnitude /= inv_mass_sum

                impulse_x = impulse_magnitude * nx
                impulse_y = impulse_magnitude * ny
                impulse_z = impulse_magnitude * nz

                velocities[i, 0] -= impulse_x * inv_mass_i
                velocities[i, 1] -= impulse_y * inv_mass_i
                velocities[i, 2] -= impulse_z * inv_mass_i

                velocities[j, 0] += impulse_x * inv_mass_j
                velocities[j, 1] += impulse_y * inv_mass_j
                velocities[j, 2] += impulse_z * inv_mass_j


def make_initial_conditions(n):
    rng = np.random.default_rng()

    positions = np.zeros((n, 3), dtype=np.float64)
    velocities = np.zeros((n, 3), dtype=np.float64)
    masses = np.full(n, PARTICLE_MASS, dtype=np.float64)
    radii = np.full(n, PARTICLE_RADIUS, dtype=np.float64)

    min_spacing = 2.5 * PARTICLE_RADIUS
    min_spacing_squared = min_spacing * min_spacing

    if START_NEAR_CORNER:
        x_min = BOX_LEFT + PARTICLE_RADIUS
        x_max = BOX_LEFT + WORLD_WIDTH * 0.20

        y_min = BOX_BOTTOM + PARTICLE_RADIUS
        y_max = BOX_BOTTOM + WORLD_HEIGHT * 0.20

        angle_min = 0.0
        angle_max = np.pi / 2.0

    else:
        x_min = BOX_LEFT + PARTICLE_RADIUS
        x_max = BOX_RIGHT - PARTICLE_RADIUS

        y_min = BOX_BOTTOM + PARTICLE_RADIUS
        y_max = BOX_TOP - PARTICLE_RADIUS

        angle_min = 0.0
        angle_max = 2.0 * np.pi

    for i in range(n):
        placed = False
        attempts = 0

        while not placed:
            attempts += 1

            x = rng.uniform(x_min, x_max)
            y = rng.uniform(y_min, y_max)

            placed = True

            for j in range(i):
                dx = x - positions[j, 0]
                dy = y - positions[j, 1]

                if dx * dx + dy * dy < min_spacing_squared:
                    placed = False
                    break

            # Safety fallback so the code does not hang if the corner cluster
            # is too crowded for the number/radius of particles.
            if attempts > 10000:
                placed = True

        positions[i, 0] = x
        positions[i, 1] = y
        positions[i, 2] = 0.0

        angle = rng.uniform(angle_min, angle_max)
        speed = rng.uniform(0.5 * PARTICLE_SPEED, 1.5 * PARTICLE_SPEED)

        velocities[i, 0] = speed * np.cos(angle)
        velocities[i, 1] = speed * np.sin(angle)
        velocities[i, 2] = 0.0

    return positions, velocities, masses, radii


def make_wall_points():
    wall_points = []
    pump_points = []

    spacing = 20.0

    x_values = np.arange(BOX_LEFT, BOX_RIGHT + spacing, spacing)
    y_values = np.arange(BOX_BOTTOM, BOX_TOP + spacing, spacing)

    # Outer box
    for x in x_values:
        wall_points.append((x, BOX_BOTTOM, 0.0))
        wall_points.append((x, BOX_TOP, 0.0))

    for y in y_values:
        wall_points.append((BOX_LEFT, y, 0.0))
        wall_points.append((BOX_RIGHT, y, 0.0))

    # Center wall with a gap
    for y in y_values:
        if abs(y) >= HEAT_PUMP_HALF_HEIGHT:
            wall_points.append((CENTER_WALL_X, y, 0.0))

    # Heat pump marker
    pump_y_values = np.arange(
        -HEAT_PUMP_HALF_HEIGHT,
        HEAT_PUMP_HALF_HEIGHT + spacing,
        spacing
    )

    for y in pump_y_values:
        pump_points.append((CENTER_WALL_X, y, 0.0))

    return np.array(wall_points), np.array(pump_points)


def draw_box():
    wall_color = (180, 180, 180)
    pump_color = (255, 120, 80)

    wall_radius = 2.0
    pump_radius = 4.0

    for p in wall_points:
        d.draw(
            x_pos=p[0],
            y_pos=p[1],
            z_pos=p[2],
            color=wall_color,
            radius=wall_radius,
        )

    for p in pump_points:
        d.draw(
            x_pos=p[0],
            y_pos=p[1],
            z_pos=p[2],
            color=pump_color,
            radius=pump_radius,
        )


def calculate_position_verlet(t_i):
    global positions, velocities, old_positions

    old_positions[:, :] = positions[:, :]

    # Velocity Verlet style with no continuous acceleration:
    # x_new = x_old + v * dt
    drift_positions_parallel(positions, velocities, TIME_STEP)

    resolve_box_collisions_parallel(
        positions,
        velocities,
        radii,
        BOX_LEFT,
        BOX_RIGHT,
        BOX_BOTTOM,
        BOX_TOP
    )

    resolve_center_wall_and_heat_pump_parallel(
        positions,
        velocities,
        old_positions,
        radii,
        CENTER_WALL_X,
        HEAT_PUMP_HALF_HEIGHT,
        HEAT_PUMP_LEFT_TO_RIGHT_MULT,
        HEAT_PUMP_RIGHT_TO_LEFT_MULT
    )

    for _ in range(COLLISION_PASSES):
        apply_elastic_collision_impulses_serial(
            positions,
            velocities,
            masses,
            radii
        )

        resolve_box_collisions_parallel(
            positions,
            velocities,
            radii,
            BOX_LEFT,
            BOX_RIGHT,
            BOX_BOTTOM,
            BOX_TOP
        )

        resolve_center_wall_and_heat_pump_parallel(
            positions,
            velocities,
            old_positions,
            radii,
            CENTER_WALL_X,
            HEAT_PUMP_HALF_HEIGHT,
            HEAT_PUMP_LEFT_TO_RIGHT_MULT,
            HEAT_PUMP_RIGHT_TO_LEFT_MULT
        )

    return t_i + TIME_STEP


def warm_up_numba():
    # First Numba call compiles the functions, which can cause one visible pause.
    # This runs one fake step on copied arrays before the window starts.
    p = positions.copy()
    v = velocities.copy()
    old = old_positions.copy()
    m = masses.copy()
    r = radii.copy()

    old[:, :] = p[:, :]

    drift_positions_parallel(p, v, TIME_STEP)

    resolve_box_collisions_parallel(
        p,
        v,
        r,
        BOX_LEFT,
        BOX_RIGHT,
        BOX_BOTTOM,
        BOX_TOP
    )

    resolve_center_wall_and_heat_pump_parallel(
        p,
        v,
        old,
        r,
        CENTER_WALL_X,
        HEAT_PUMP_HALF_HEIGHT,
        HEAT_PUMP_LEFT_TO_RIGHT_MULT,
        HEAT_PUMP_RIGHT_TO_LEFT_MULT
    )

    apply_elastic_collision_impulses_serial(p, v, m, r)


# Initialize particles
t_curr = 0.0

positions, velocities, masses, radii = make_initial_conditions(bodies)
old_positions = positions.copy()

colors = np.random.randint(100, 256, size=(bodies, 3))

wall_points, pump_points = make_wall_points()

warm_up_numba()


def update(dt):
    global t_curr

    if t_curr > t_final:
        sys.exit(0)

    d.start_frame()

    t_curr = calculate_position_verlet(t_curr)

    draw_box()

    for i in range(bodies):
        d.draw(
            x_pos=positions[i, 0],
            y_pos=positions[i, 1],
            z_pos=positions[i, 2],
            color=tuple(colors[i]),
            radius=radii[i],
        )

    d.end_frame()


def panda_update(dt):
    for _ in range(TICKS_PER_FRAME):
        update(dt)


if __name__ == "__main__":
    d.init(1920, 1080, WORLD_WIDTH, WORLD_HEIGHT)
    d.__run__(panda_update)
