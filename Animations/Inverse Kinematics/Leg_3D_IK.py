import manim
from manim import *
import math

thigh_length = 30/23
calf_length = 120/23
hip_height = 0
hip_seperation = 85/23

foot_z = 95.5/23
foot_y = -135/23
foot_x = 0

ZERO_X = 0
ZERO_Y = 135/23
ZERO_Z = 95.5/23

theta_hips = 100.27*DEGREES
a = 53.863/23

thigh_color = BLUE
foot_color = GREEN
waist_color = RED

class LegIK(ThreeDScene):
    def construct(self):
        aspect_ratio = 16/9

        self.camera.frame_width = 30
        self.camera.frame_height = self.camera.frame_width / aspect_ratio

        #front on view
        self.set_camera_orientation(phi=0, theta=-PI/2)
        self.set_camera_orientation(phi=PI/2, theta=0, gamma=PI/2, focal_distance=1000, frame_center=ORIGIN, run_time=3)

        # axes = ThreeDAxes()
        # axes.add(
        #     axes.get_x_axis_label(("x")),
        #     axes.get_y_axis_label(("y")),
        #     axes.get_z_axis_label(("z"))
        # )
        # self.add(axes)

        waist = Sphere([0, hip_height, 0], radius=DEFAULT_DOT_RADIUS)
        torso = Sphere([0, hip_height, -hip_seperation/2], radius=DEFAULT_DOT_RADIUS)

        foot_x_tracker = ValueTracker(foot_x)
        foot_y_tracker = ValueTracker(foot_y)
        foot_z_tracker = ValueTracker(foot_z - hip_seperation/2)

        servo_centre_point = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[0])
        servo_waist_line = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[1])
        foot_servo_line = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[2])
        foot = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[3])
        servo1 = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[4])
        servo2 = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[5])
        servo_line = always_redraw(lambda: self.get_leg(foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)[6])

        torso_line = Line3D(waist.get_center(), torso.get_center(), color=PURPLE)

        self.play(FadeIn(servo_centre_point), FadeIn(foot), FadeIn(waist), FadeIn(torso), FadeIn(servo1), FadeIn(servo2), FadeIn(foot_servo_line), FadeIn(servo_waist_line), FadeIn(torso_line), FadeIn(servo_line))

        self.wait(2)

        def update_foot_path(mob, alpha):
            radius = 1.5
            angle = alpha * 2 * PI
            foot_y_tracker.set_value(foot_y + radius * math.cos(angle))
            foot_z_tracker.set_value(foot_z - hip_seperation/2 + radius * math.sin(angle))

        self.move_camera(
                phi=0, theta=-PI/2, gamma=0, run_time=4,
                added_anims=[UpdateFromAlphaFunc(foot, update_foot_path)]
            )

        self.play(UpdateFromAlphaFunc(foot, update_foot_path), run_time=4)

        # self.wait(2)

        # self.move_camera(phi=0, theta=-PI/2, gamma=0, run_time=3)
        self.wait(2)


    def get_y_prime_theta_h(self, foot_y: float, foot_z: float):
        q = foot_z - hip_seperation/2
        f = math.sqrt(q**2  + foot_y**2)

        quad_a = 1.0
        quad_b = -2*a*math.cos(theta_hips)
        quad_c = a**2 - q**2 - foot_y**2

        roots = self.solve_quadratic(quad_a, quad_b, quad_c)
        y_prime = [r for r in roots if r > 0]
        if not y_prime:
            raise ValueError("No positive roots found")

        theta_c = math.acos((a**2 - y_prime[0]**2 -f**2)/(-2*y_prime[0]*f))
        theta_d = math.acos((foot_y**2 - f**2 - q**2)/(-2*f*q))
        theta_h = PI-theta_c - theta_d
        return y_prime[0], theta_h

    def get_leg(self, foot_x, foot_y, foot_z, waist):
        y_prime, theta_h = self.get_y_prime_theta_h(foot_y, foot_z)
        servo_centre_point = Sphere([foot_x, foot_y + y_prime*math.sin(theta_h), foot_z + y_prime*math.cos(theta_h) - hip_seperation/2], radius=DEFAULT_DOT_RADIUS)

        foot_servo_line = Line3D([foot_x, foot_y, foot_z], servo_centre_point.get_center(), color=YELLOW)
        servo_waist_line = Line3D(servo_centre_point.get_center(), waist.get_center(), color=ORANGE)

        foot = Sphere([foot_x, foot_y, foot_z], radius=DEFAULT_DOT_RADIUS)

        servo1 = Sphere([servo_centre_point.get_center()[0] - hip_seperation/2, servo_centre_point.get_center()[1], servo_centre_point.get_center()[2]], radius=DEFAULT_DOT_RADIUS/2)
        servo2 = Sphere([servo_centre_point.get_center()[0] + hip_seperation/2, servo_centre_point.get_center()[1], servo_centre_point.get_center()[2]], radius=DEFAULT_DOT_RADIUS/2)

        servo_line = Line3D(servo1.get_center(), servo2.get_center(), color=PINK)

        return servo_centre_point, foot_servo_line, servo_waist_line, foot, servo1, servo2, servo_line


    def solve_quadratic(self, a, b, c):
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            raise ValueError("No real roots found")
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return root1, root2