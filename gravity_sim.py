import numpy as np
import pygame
import draw as d

t_i = 0 # seconds
t_f = 10 # seconds
y_0 = 10 # m 
x_0 = 0 # m
v_yi = 10 # m/s 
v_xi = 3 # m/s
g = 9.81 # m/s^2
fps = 60

t = np.linspace(t_i, t_f, t_f * fps) # change the number of time steps

def x(t):
    return v_xi*t + x_0

def y(t):
    return -0.5*g*t**2 + v_yi*t + y_0

x_pos, y_pos = x(t), y(t)

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

d.set_world_width()
d.set_world_height()
d.set_screen(screen)

i = 0
last_x = 0

while running:
    if i >= np.size(t):
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill("black")

    # render here
    
    # height is 36m, width is 64m
    if (y_pos[i] < 0):
        y_pos[i] = 0
        if (last_x != 0):
            x_pos[i] = last_x
    else:
        last_x = x_pos[i]

    d.draw(x_pos[i], y_pos[i])
    d.draw_axes()

    i += 1

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
