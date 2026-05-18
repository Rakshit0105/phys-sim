import numpy as np

# Body / particle for rendering
# base class for any physical body
class Body:
    def __init__(
        self,
        position=np.zeros(3, dtype=float),
        velocity=np.zeros(3, dtype=float),
        acceleration=np.zeros(3, dtype=float),
        jerk=np.zeros(3, dtype=float),
        mass=0.0,
        color=(255,0,0),
        radius=10.0,
    ):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.jerk = jerk
        self.mass = mass
        self.color = color
        self.radius = radius

