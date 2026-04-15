import pygame
import pyglet as pg

def __init__(window_width=1280, window_height=720, world_width=64, world_height=36):
    # globals
    global WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT 
    WINDOW_WIDTH = window_width
    WINDOW_HEIGHT = window_height
    WORLD_WIDTH = world_width
    WORLD_HEIGHT = world_height

    # initialize pyglet
    global window
    window = pg.window.Window(width=int(WINDOW_WIDTH), height=int(WINDOW_HEIGHT))

    global batch
    batch = pg.graphics.Batch()

    global shapes
    shapes = []

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
def draw(x_pos, y_pos):
    circle = pg.shapes.Circle(
        x=world_to_screen_x(x_pos),
        y=world_to_screen_y(y_pos),
        radius=10,
        color=(255,0,0),
        batch=batch
    )
    shapes.append(circle)

# draw x and y axes
def draw_axes():
    x_axis = pg.shapes.Line(
        x=world_to_screen_x(-WORLD_WIDTH),
        y=world_to_screen_y(0),
        x2=world_to_screen_x(WORLD_WIDTH),
        y2=world_to_screen_y(0),
        thickness=4,
        color=(255,255,255),
        batch=batch
    )

    y_axis = pg.shapes.Line(
        x=world_to_screen_x(0),
        y=world_to_screen_y(-WORLD_HEIGHT),
        x2=world_to_screen_x(0),
        y2=world_to_screen_y(WORLD_HEIGHT),
        thickness=4,
        color=(255,255,255),
        batch=batch
    )

    shapes.append(x_axis)
    shapes.append(y_axis)

