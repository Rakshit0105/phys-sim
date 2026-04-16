import pygame
import pyglet as pg
from body import Body

def __init__(
    window_width=1280,
    window_height=720,
    world_width=64,
    world_height=36,
    circle_radius=10,
    trail_length=100
):
    # globals
    global WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, CIRCLE_RADIUS, TRAIL_LENGTH
    WINDOW_WIDTH = window_width
    WINDOW_HEIGHT = window_height
    WORLD_WIDTH = world_width
    WORLD_HEIGHT = world_height
    CIRCLE_RADIUS = circle_radius
    TRAIL_LENGTH = trail_length

    # initialize pyglet
    global window
    window = pg.window.Window(width=int(WINDOW_WIDTH), height=int(WINDOW_HEIGHT))

    global batch
    batch = pg.graphics.Batch()

    global shapes
    shapes = []

    global x_axis
    x_axis = pg.shapes.Line(
        x=world_to_screen_x(-WORLD_WIDTH),
        y=world_to_screen_y(0),
        x2=world_to_screen_x(WORLD_WIDTH),
        y2=world_to_screen_y(0),
        thickness=4,
        color=(255,255,255),
        batch=batch
    )

    global y_axis
    y_axis = pg.shapes.Line(
        x=world_to_screen_x(0),
        y=world_to_screen_y(-WORLD_HEIGHT),
        x2=world_to_screen_x(0),
        y2=world_to_screen_y(WORLD_HEIGHT),
        thickness=4,
        color=(255,255,255),
        batch=batch
    )

    global trails
    trails = []

    global bodies
    bodies = []

    global shifts
    shifts = []

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

def __run__():
    pg.app.run()

# set width in meters 
def set_world_width(width = 64):
    WORLD_WIDTH = width

# set height in meters
def set_world_height(height = 36):
    WORLD_HEIGHT = height

# convert from x in meters to x on screen
def world_to_screen_x(x_pos):
    return WINDOW_WIDTH / 2 + x_pos * WINDOW_WIDTH / WORLD_WIDTH

# convert from y in meters to y on screen
def world_to_screen_y(y_pos):
    return WINDOW_HEIGHT / 2 + y_pos * WINDOW_HEIGHT / WORLD_HEIGHT

def start_frame():
    shapes.clear()

def end_frame():
    pass

# draw circle at x, y in meters
def draw(x_pos, y_pos, color=(255,0,0), radius=10):
    circle = pg.shapes.Circle(
        x=world_to_screen_x(x_pos),
        y=world_to_screen_y(y_pos),
        radius=radius,
        color=color,
        batch=batch
    )
    shapes.append(circle)

def add_body(body):
    circle = pg.shapes.Circle(
        x=world_to_screen_x(body.x),
        y=world_to_screen_y(body.y),
        color=body.color,
        radius=body.radius,
        batch=batch
    )

    bodies.append(circle)
    trails.append([])
    shifts.append(0)

    for i in range(TRAIL_LENGTH):
        x, y = body.trail[i]
        circle = pg.shapes.Circle(
            x=world_to_screen_x(x),
            y=world_to_screen_y(y),
            radius=body.radius // 2,
            color=body.color,
            batch=batch
        )
        trails[-1].append(circle)

def draw_trail(body, index, shift=0):
    for i in range(shift):
        x, y = body.trail[i - shift]
        j = (i + shifts[index]) % TRAIL_LENGTH
        trails[index][j].x=world_to_screen_x(x)
        trails[index][j].y=world_to_screen_y(y)

    shifts[index] = (shifts[index] + shift) % TRAIL_LENGTH


def draw_body(body, index):
    bodies[index].x=world_to_screen_x(body.x)
    bodies[index].y=world_to_screen_y(body.y)

"""
def draw_trail(x_pos, y_pos):
    circle = pg.shapes.Circle(
        x=world_to_screen_x(x_pos),
        y=world_to_screen_y(y_pos),
        radius=CIRCLE_RADIUS,
        color=(255,0,0),
        batch=batch
    )

    while len(trail) < TRAIL_LENGTH:
        trail.append(circle)

    trail.pop(0)
    trail.append(circle)

    for i in range(TRAIL_LENGTH):
        trail[i].radius = i / TRAIL_LENGTH * CIRCLE_RADIUS
        shapes.append(trail[i])
"""

# draw x and y axes
def draw_axes():
    shapes.append(x_axis)
    shapes.append(y_axis)

