from collections import deque

class Body:
    # base class for any physical body

    def __init__(
        self,
        trail_length=100,
        color=(255,0,0),
        radius=10,
        x_0=0,
        y_0=0,
    ):
        self.x = x_0
        self.y = y_0
        self.color = color
        self.radius = radius
        self.trail = deque(maxlen=trail_length)

        while len(self.trail) < trail_length:
            self.trail.append((self.x, self.y))

    def move(self, x, y):
        self.x = x
        self.y = y
        self.trail.append((x, y))

    def set_trail_length(self, trail_length):
        old = list(self.trail)
        self.trail = deque(old[-n:], maxlen=n)

