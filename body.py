class Body:
    # base class for any physical body

    def __init__(
        self,
        body,
        color=(255,0,0),
        radius=10,
    ):
        self.color = color
        self.radius = radius
        self.body = body

