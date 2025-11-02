from manim import *

class CuboidAndSphere3D(ThreeDScene):
    def construct(self):
        # Create cuboid (box)
        cuboid = Cube(side_length=2, fill_opacity=0.8, fill_color=BLUE, stroke_width=1)
        cuboid.move_to(ORIGIN)

        # Create sphere behind cuboid (along +Z axis)
        sphere = Sphere(radius=1, fill_opacity=0.8, fill_color=RED, stroke_width=1)
        sphere.move_to(ORIGIN + OUT * 1.5)  # OUT is +Z direction

        # Add objects
        self.add(cuboid, sphere)

        # Set orthographic projection for the camera
        self.renderer.camera.orthographic = True

        # Initial orthogonal view: front face
        self.set_camera_orientation(phi=0 * DEGREES, theta=0 * DEGREES)

        # Wait to show initial view
        self.wait(1)

        # Move camera to right side (still orthogonal)
        self.move_camera(phi=30 * DEGREES, theta=60 * DEGREES, run_time=3)

        # Wait to show final view
        self.wait(2)