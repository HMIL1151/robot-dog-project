import manim
from manim import *
import math
import numpy as np

thigh_length = 30/23
calf_length = 120/23
hip_height = 0
hip_seperation = 85/23

ZERO_X = 0
ZERO_Y = 150/23
ZERO_Z = 95.5/23

foot_z = 95.5/23
foot_y = -ZERO_Y
foot_x = 0



theta_hips = 100.27*DEGREES
a = 53.863/23

thigh_color = BLUE
foot_color = GREEN
waist_color = RED

class CameraViews:
    def __init__(self, front, side, isometric):
        self.front = front
        self.side = side
        self.isometric = isometric

class LegIK(ThreeDScene):
    def construct(self):
        views = CameraViews(
            front=dict(phi=0, theta=-PI/2),
            side=dict(phi=PI/2, theta=0, gamma=PI/2),
            isometric=dict(phi=PI/4, theta=-PI/4, gamma=0)
        )

        aspect_ratio = 16/9

        self.camera.frame_width = 30
        self.camera.frame_height = self.camera.frame_width / aspect_ratio

        self.set_camera_orientation(**views.front)
        self.set_camera_orientation(**views.side, focal_distance=1000, frame_center=ORIGIN, run_time=3)

        waist = Sphere([0, hip_height, 0], radius=DEFAULT_DOT_RADIUS)
        torso = Sphere([0, hip_height, -hip_seperation/2], radius=DEFAULT_DOT_RADIUS)

        foot_x_tracker = ValueTracker(foot_x)
        foot_y_tracker = ValueTracker(foot_y)
        foot_z_tracker = ValueTracker(foot_z - hip_seperation/2)

        leg = lambda: (foot_x_tracker.get_value(), foot_y_tracker.get_value(), foot_z_tracker.get_value(), waist)

        servo_centre_point = always_redraw(lambda: self.get_leg(leg())[0])
        servo_waist_line =  always_redraw(lambda: self.get_leg(leg())[1])
        foot_servo_line = always_redraw(lambda: self.get_leg(leg())[2])
        foot = always_redraw(lambda: self.get_leg(leg())[3])
        servo1 = always_redraw(lambda: self.get_leg(leg())[4])
        servo2 = always_redraw(lambda: self.get_leg(leg())[5])
        servo_line = always_redraw(lambda: self.get_leg(leg())[6])
        servo1_circle = always_redraw(lambda: self.get_leg(leg())[7])
        servo2_circle = always_redraw(lambda: self.get_leg(leg())[8])
        foot_circle = always_redraw(lambda: self.get_leg(leg())[9])
        calf1_line = always_redraw(lambda: self.get_leg(leg())[10])
        calf2_line = always_redraw(lambda: self.get_leg(leg())[11])
        servo1_line = always_redraw(lambda: self.get_leg(leg())[12])
        servo2_line = always_redraw(lambda: self.get_leg(leg())[13])

        torso_line = Line3D(waist.get_center(), torso.get_center(), color=PURPLE)

        self.add(servo_centre_point, foot, waist, torso, servo1, servo2, foot_servo_line, servo_waist_line, torso_line, servo_line, servo1_circle, servo2_circle, foot_circle, calf1_line, calf2_line, servo1_line, servo2_line)

        #self.play(FadeIn(servo_centre_point), FadeIn(foot), FadeIn(waist), FadeIn(torso), FadeIn(servo1), FadeIn(servo2), FadeIn(foot_servo_line), FadeIn(servo_waist_line), FadeIn(torso_line), FadeIn(servo_line), FadeIn(servo1_circle), FadeIn(servo2_circle), FadeIn(foot_circle), FadeIn(calf1_line), FadeIn(calf2_line), FadeIn(servo1_line), FadeIn(servo2_line))

        #self.wait(2)

        def update_foot_path(mob, alpha):
            radius = 0.5
            angle = alpha * 2 * PI
            foot_y_tracker.set_value(foot_y + radius * math.cos(angle))
            foot_x_tracker.set_value(foot_x + radius * math.sin(angle))

        # self.move_camera(
        #         phi=0, theta=-PI/2, gamma=0, run_time=4,
        #         added_anims=[UpdateFromAlphaFunc(foot, update_foot_path)]
        #     )

        #self.play(UpdateFromAlphaFunc(foot, update_foot_path), run_time=4)

        # self.wait(2)

        self.move_camera(phi=0, theta=-PI/2, gamma=0, run_time=3)
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

    def get_leg(self, leg):
        foot_x = leg[0]
        foot_y = leg[1]
        foot_z = leg[2]
        waist = leg[3]

        y_prime, theta_h = self.get_y_prime_theta_h(foot_y, foot_z)
        servo_centre_point = Sphere([waist.get_center()[0], foot_y + y_prime*math.sin(theta_h), foot_z + y_prime*math.cos(theta_h) - hip_seperation/2], radius=DEFAULT_DOT_RADIUS)

        foot_servo_line = Line3D([foot_x, foot_y, foot_z], servo_centre_point.get_center(), color=YELLOW)
        servo_waist_line = Line3D(servo_centre_point.get_center(), waist.get_center(), color=ORANGE)

        foot = Sphere([foot_x, foot_y, foot_z], radius=DEFAULT_DOT_RADIUS)

        servo1 = Sphere([servo_centre_point.get_center()[0] - hip_seperation/2, servo_centre_point.get_center()[1], servo_centre_point.get_center()[2]], radius=DEFAULT_DOT_RADIUS/2)
        servo2 = Sphere([servo_centre_point.get_center()[0] + hip_seperation/2, servo_centre_point.get_center()[1], servo_centre_point.get_center()[2]], radius=DEFAULT_DOT_RADIUS/2)

        servo_line = Line3D(servo1.get_center(), servo2.get_center(), color=PINK)

        foot_x_y_plane_normal_vector = self.get_plane_normal(foot.get_center(), servo1.get_center(), servo2.get_center())
        servo1_circle = self.circle_parallel_to_plane(servo1.get_center(), foot_x_y_plane_normal_vector, radius=thigh_length, color=thigh_color)
        servo2_circle = self.circle_parallel_to_plane(servo2.get_center(), foot_x_y_plane_normal_vector, radius=thigh_length, color=thigh_color)
        foot_circle = self.circle_parallel_to_plane(foot.get_center(), foot_x_y_plane_normal_vector, radius=calf_length, color=foot_color)

        foot_circle = Circle(radius=calf_length).move_to(foot.get_center())
        servo1_circle = Circle(radius=thigh_length).move_to(servo1.get_center())
        servo2_circle = Circle(radius=thigh_length).move_to(servo2.get_center())

        try:
            inter1 = self.intersection_between_circles_3d(servo1_circle, foot_circle)[1]
            inter2 = self.intersection_between_circles_3d(servo2_circle, foot_circle)[0]
        except ValueError:
            raise ValueError("No intersection points between the circles")

        servo1_line = Line3D(servo1.get_center(), inter1.get_center(), color=BLUE)
        servo2_line = Line3D(servo2.get_center(), inter2.get_center(), color=BLUE)
        calf1_line = Line3D(foot.get_center(), inter1.get_center(), color=GREEN)
        calf2_line = Line3D(foot.get_center(), inter2.get_center(), color=GREEN)


        return servo_centre_point, foot_servo_line, servo_waist_line, foot, servo1, servo2, servo_line, servo1_circle, servo2_circle, foot_circle, calf1_line, calf2_line, servo1_line, servo2_line

    @staticmethod
    def intersection_between_circles_3d(circle1: Circle, circle2: Circle):
        (x0, y0, z0), r0 = circle1.get_center(), circle1.radius
        (x1, y1, z1), r1 = circle2.get_center(), circle2.radius

        d = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2)
        if d > (r0 + r1) or d < abs(r0 - r1):
            raise ValueError("No intersection points between the circles")
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = math.sqrt(r0 ** 2 - a ** 2)
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        z2 = z0 + a * (z1 - z0) / d

        rx = -(y1 - y0) * (h / d)
        ry = (x1 - x0) * (h / d)
        intersection_point_1 = Dot(point=np.array([x2 + rx, y2 + ry, z2]), color=YELLOW)
        intersection_point_2 = Dot(point=np.array([x2 - rx, y2 - ry, z2]), color=YELLOW)
        return (intersection_point_1, intersection_point_2)
    

    @staticmethod
    def solve_quadratic(a, b, c):
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            raise ValueError("No real roots found")
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return root1, root2
    
    @staticmethod
    def get_plane_normal(p1, p2, p3):
        # p1, p2, p3 are 3D points (numpy arrays or lists)
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)  # Normalize
        return normal
    
    @staticmethod
    def circle_parallel_to_plane(center_point, normal_vector, radius=1, color=WHITE):
        circle = Circle(radius=radius, color=color)
        # Default normal is [0, 0, 1] (z-axis)
        default_normal = np.array([0, 0, 1])
        n = np.array(normal_vector) / np.linalg.norm(normal_vector)
        axis = np.cross(default_normal, n)
        angle = np.arccos(np.dot(default_normal, n))
        if np.linalg.norm(axis) > 1e-6:
            circle.rotate(angle, axis=axis)
        circle.move_to(center_point)
        return circle