from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4, Vec3


class App(ShowBase):
    def __init__(self):
        super().__init__()

        # Camera
        self.disableMouse()
        self.camera.setPos(0, -12, 6)
        self.camera.lookAt(0, 0, 0)

        # Load a built-in sphere model
        self.sphere = self.loader.loadModel("models/misc/sphere")
        self.sphere.reparentTo(self.render)
        self.sphere.setScale(1)
        self.sphere.setPos(0, 0, 0)

        # Lighting
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.3, 0.3, 0.3, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(1, 1, 1, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)
        self.render.setLight(sun_np)

        # Per-frame update
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        t = task.time

        # Example fake physics/render update
        self.sphere.setPos(
            3 * __import__("math").sin(t),
            0,
            2 + __import__("math").cos(t),
        )

        return task.cont


app = App()
app.run()
