import pygame as pg

# set width in meters 
def set_world_width(width = 64):
    global WORLD_WIDTH
    WORLD_WIDTH = width

# set height in meters
def set_world_height(height = 36):
    global WORLD_HEIGHT
    WORLD_HEIGHT = height

def set_screen(screen):
    global SCREEN
    SCREEN = screen

# convert from x in meters to x on screen
def pgx(x_pos):
    return SCREEN.get_width() / 2 + x_pos * SCREEN.get_width() / WORLD_WIDTH

# convert from y in meters to y on screen
def pgy(y_pos):
    return SCREEN.get_height() / 2 - y_pos * SCREEN.get_height() / WORLD_HEIGHT

# draw circle at x, y in meters
def draw(x_pos, y_pos):
    pg.draw.circle(SCREEN, "red", pg.Vector2(pgx(x_pos), pgy(y_pos)), 10)

# draw x and y axes
def draw_axes():
    pg.draw.line(SCREEN, "white", pg.Vector2(0, SCREEN.get_height() / 2), pg.Vector2(SCREEN.get_width(), SCREEN.get_height() / 2));
    pg.draw.line(SCREEN, "white", pg.Vector2(SCREEN.get_width() / 2, 0), pg.Vector2(SCREEN.get_width() / 2, SCREEN.get_height()));

