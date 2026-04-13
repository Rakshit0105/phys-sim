import pygame
import pyglet as pg

def __init__(window_width=1280, window_height=720, world_width=64, world_height=36):
    # globals
    global WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT 
    WINDOW_WIDTH = window_width*2
    WINDOW_HEIGHT = window_height*2
    WORLD_WIDTH = world_width
    WORLD_HEIGHT = world_height

    # initialize pyglet
    global window
    window = pg.window.Window(width=WINDOW_WIDTH/2, height=WINDOW_HEIGHT/2)

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

# draw circle at x, y in meters
def draw(x_pos, y_pos):
    # print(world_to_screen_x(x_pos), world_to_screen_y(y_pos), window.width, window.height)
    circle = pg.shapes.Circle(
        x=world_to_screen_x(x_pos),
        y=world_to_screen_y(y_pos),
        radius=10,
        color=(255,0,0),
        batch=batch
    )
    shapes.clear()
    shapes.append(circle)
    # pygame.draw.circle(SCREEN, "red", pygame.Vector2(pygamex(x_pos), pygamey(y_pos)), 10)

# draw x and y axes
# def draw_axes():
#     pygame.draw.line(SCREEN, "white", pygame.Vector2(0, SCREEN.get_height() / 2), pygame.Vector2(SCREEN.get_width(), SCREEN.get_height() / 2));
#     pygame.draw.line(SCREEN, "white", pygame.Vector2(SCREEN.get_width() / 2, 0), pygame.Vector2(SCREEN.get_width() / 2, SCREEN.get_height()));

