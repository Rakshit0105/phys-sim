# renderer_panda.py

from math import sin, cos, pi

from panda3d.core import (
    loadPrcFileData,
    OrthographicLens,
    LineSegs,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    Vec4,
    AmbientLight,
    DirectionalLight,
    ClockObject,
)

from direct.showbase.ShowBase import ShowBase


_renderer = None


def _color255_to_vec4(color):
    r, g, b = color[:3]
    a = color[3] if len(color) > 3 else 255
    return Vec4(r / 255.0, g / 255.0, b / 255.0, a / 255.0)


class PandaPhysicsRenderer(ShowBase):
    def __init__(
        self,
        window_width=1280,
        window_height=720,
        world_width=64,
        world_height=36,
        world_depth=64,
        radius_mode="pixels",
    ):
        # Must happen before ShowBase initializes the window.
        loadPrcFileData("", f"win-size {int(window_width)} {int(window_height)}")
        loadPrcFileData("", "window-title Physics Sim 3D")

        super().__init__()

        self.WINDOW_WIDTH = window_width
        self.WINDOW_HEIGHT = window_height
        self.WORLD_WIDTH = world_width
        self.WORLD_HEIGHT = world_height
        self.WORLD_DEPTH = world_depth



        # Cap the internal render scale to prevent singular matrix errors
        self.render_scale = 1000.0 / world_width if world_width > 1000 else 1.0

        self.WINDOW_WIDTH = window_width
        self.WINDOW_HEIGHT = window_height
        
        # Store original dimensions for legacy pixel conversions
        self.ORIG_WORLD_WIDTH = world_width
        self.ORIG_WORLD_HEIGHT = world_height

        # Scale down the bounds handed to Panda3D
        self.WORLD_WIDTH = world_width * self.render_scale
        self.WORLD_HEIGHT = world_height * self.render_scale
        self.WORLD_DEPTH = world_depth * self.render_scale



        # "pixels" keeps your old radius=10 behavior roughly similar.
        # "world" means radius is measured directly in simulation units/meters.
        self.radius_mode = radius_mode

        self.disableMouse()
        self.setBackgroundColor(0.03, 0.03, 0.04, 1)

        self.root = self.render.attachNewNode("physics_world")

        self._setup_camera()
        self._setup_lights()

        self._sphere_template = self._make_unit_sphere()
        self._sphere_pool = []
        self._used_spheres = 0

        self.axes_np = None
        self._rebuild_axes()

    def _setup_camera(self):
        # Orthographic camera preserves your old 2D world scale.
        # Visible region is roughly:
        # x in [-WORLD_WIDTH/2, WORLD_WIDTH/2]
        # y in [-WORLD_HEIGHT/2, WORLD_HEIGHT/2]
        lens = OrthographicLens()
        lens.setFilmSize(self.WORLD_WIDTH, self.WORLD_HEIGHT)

        self.cam.node().setLens(lens)

        # Panda3D's vertical axis is Z.
        # We map your old 2D world as:
        #   old x -> Panda X
        #   old y -> Panda Z
        #   new z/depth -> Panda Y
        self.camera.setPos(0, -100, 0)
        self.camera.lookAt(0, 0, 0)

    def _setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.45, 0.45, 0.45, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)

        key = DirectionalLight("key")
        key.setColor(Vec4(0.8, 0.8, 0.8, 1))
        key_np = self.render.attachNewNode(key)
        key_np.setHpr(45, -60, 0)
        self.render.setLight(key_np)

    def _to_panda_pos(self, x, y, z):
        # Preserve your old x/y plane.
        # Old y becomes vertical height.
        # return x, z, y
        return x * self.render_scale, z * self.render_scale, y * self.render_scale

    def _radius_to_world(self, radius):
        if self.radius_mode == "world":
            return radius

        # Approximate old pyglet pixel-radius behavior.
        # With 1280px window and 64m world width:
        # radius=10px -> 0.5 world units.
        return radius * self.WORLD_WIDTH / self.WINDOW_WIDTH

    def _make_unit_sphere(self, stacks=12, slices=24):
        fmt = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData("unit_sphere", fmt, Geom.UHStatic)

        vertices = GeomVertexWriter(vdata, "vertex")
        normals = GeomVertexWriter(vdata, "normal")

        for i in range(stacks + 1):
            theta = pi * i / stacks
            z = cos(theta)
            r = sin(theta)

            for j in range(slices + 1):
                phi = 2 * pi * j / slices
                x = r * cos(phi)
                y = r * sin(phi)

                vertices.addData3f(x, y, z)
                normals.addData3f(x, y, z)

        tris = GeomTriangles(Geom.UHStatic)

        for i in range(stacks):
            for j in range(slices):
                a = i * (slices + 1) + j
                b = a + slices + 1

                tris.addVertices(a, b, a + 1)
                tris.addVertices(a + 1, b, b + 1)

        tris.closePrimitive()

        geom = Geom(vdata)
        geom.addPrimitive(tris)

        node = GeomNode("unit_sphere")
        node.addGeom(geom)

        return NodePath(node)

    def _rebuild_axes(self):
        if self.axes_np is not None:
            self.axes_np.removeNode()

        lines = LineSegs("axes")
        lines.setThickness(3.0)
        lines.setColor(1, 1, 1, 1)

        # X axis: left/right
        lines.moveTo(-self.WORLD_WIDTH / 2, 0, 0)
        lines.drawTo(self.WORLD_WIDTH / 2, 0, 0)

        # Y axis from your old 2D sim: vertical
        lines.moveTo(0, 0, -self.WORLD_HEIGHT / 2)
        lines.drawTo(0, 0, self.WORLD_HEIGHT / 2)

        # Z/depth axis: into/out of screen
        lines.moveTo(0, -self.WORLD_DEPTH / 2, 0)
        lines.drawTo(0, self.WORLD_DEPTH / 2, 0)

        self.axes_np = self.root.attachNewNode(lines.create())
        self.axes_np.setLightOff()
        self.axes_np.hide()

    def set_world_width(self, width=64):
        # self.WORLD_WIDTH = width
        self.ORIG_WORLD_WIDTH = width
        self.render_scale = 1000.0 / width if width > 1000 else 1.0
        self.WORLD_WIDTH = width * self.render_scale


        self._setup_camera()
        self._rebuild_axes()

    def set_world_height(self, height=36):
        # self.WORLD_HEIGHT = height
        self.ORIG_WORLD_HEIGHT = height
        self.WORLD_HEIGHT = height * self.render_scale


        self._setup_camera()
        self._rebuild_axes()

    def start_frame(self):
        self._used_spheres = 0
        self.axes_np.hide()

    def end_frame(self):
        # Hide any pooled spheres not used this frame.
        for sphere in self._sphere_pool[self._used_spheres:]:
            sphere.hide()

    def draw(self, x_pos, y_pos, color=(255, 0, 0), radius=10.0, *, z_pos=0.0):
        if self._used_spheres == len(self._sphere_pool):
            sphere = self._sphere_template.copyTo(self.root)
            self._sphere_pool.append(sphere)

        sphere = self._sphere_pool[self._used_spheres]
        self._used_spheres += 1

        sphere.show()
        sphere.setPos(*self._to_panda_pos(x_pos, y_pos, z_pos))
        sphere.setScale(self._radius_to_world(radius))
        sphere.setColor(_color255_to_vec4(color))

    def draw3d(self, x_pos, y_pos, z_pos, color=(255, 0, 0), radius=10.0):
        self.draw(x_pos, y_pos, color=color, radius=radius, z_pos=z_pos)

    def draw_axes(self):
        self.axes_np.show()

    # Legacy helpers. In Panda3D, rendering does not need these.
    def world_to_screen_x(self, x_pos):
        # return self.WINDOW_WIDTH / 2 + x_pos * self.WINDOW_WIDTH / self.WORLD_WIDTH
        return self.WINDOW_WIDTH / 2 + x_pos * self.WINDOW_WIDTH / self.ORIG_WORLD_WIDTH

    def world_to_screen_y(self, y_pos):
        # return self.WINDOW_HEIGHT / 2 + y_pos * self.WINDOW_HEIGHT / self.WORLD_HEIGHT
        return self.WINDOW_HEIGHT / 2 + y_pos * self.WINDOW_HEIGHT / self.ORIG_WORLD_HEIGHT

    def run_with_update(self, update_func=None):
        if update_func is not None:
            def task_wrapper(task):
                dt = ClockObject.getGlobalClock().getDt()
                update_func(dt)
                return task.cont

            self.taskMgr.add(task_wrapper, "physics-update")

        self.run()


# Module-level compatibility API

def init(
    window_width=1280,
    window_height=720,
    world_width=64,
    world_height=36,
    world_depth=64,
):
    global _renderer
    
    # if _renderer is not None:
    #     return _renderer
    _renderer = PandaPhysicsRenderer(
        window_width=window_width,
        window_height=window_height,
        world_width=world_width,
        world_height=world_height,
        world_depth=world_depth,
    )
    return _renderer


def _require_renderer():
    if _renderer is None:
        raise RuntimeError("Renderer not initialized. Call __init__(...) first.")
    return _renderer


def __run__(update_func=None):
    _require_renderer().run_with_update(update_func)


def set_world_width(width=64):
    _require_renderer().set_world_width(width)


def set_world_height(height=36):
    _require_renderer().set_world_height(height)


def world_to_screen_x(x_pos):
    return _require_renderer().world_to_screen_x(x_pos)


def world_to_screen_y(y_pos):
    return _require_renderer().world_to_screen_y(y_pos)


def start_frame():
    _require_renderer().start_frame()


def end_frame():
    _require_renderer().end_frame()


def draw(x_pos, y_pos, color=(255, 0, 0), radius=10.0, *, z_pos=0.0):
    _require_renderer().draw(x_pos, y_pos, color=color, radius=radius, z_pos=z_pos)


def draw3d(x_pos, y_pos, z_pos, color=(255, 0, 0), radius=10.0):
    _require_renderer().draw3d(x_pos, y_pos, z_pos, color=color, radius=radius)


def draw_axes():
    _require_renderer().draw_axes()
