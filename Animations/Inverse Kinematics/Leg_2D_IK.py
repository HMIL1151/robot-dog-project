import manim
from manim import *
import math

thigh_length = 30/23
calf_length = 120/23
hip_seperation = 46/23
hip_height = 2
hip_seperation = 3

thigh_color = BLUE
foot_color = GREEN
waist_color = RED

class FirstScene(ThreeDScene):
    def construct(self):
        
        axes = ThreeDAxes()
        self.add(axes)
        self.set_camera_orientation(phi=0, theta=-PI/2)
        self.wait(1)

        aspect_ratio = 16/9

        self.camera.frame_width = 20
        self.camera.frame_height = self.camera.frame_width / aspect_ratio
        
        hip1 = Sphere([-hip_seperation/2, hip_height, 0], radius=DEFAULT_DOT_RADIUS)
        hip1.set_color(thigh_color)
        hip2 = Sphere([hip_seperation/2, hip_height, 0], radius=DEFAULT_DOT_RADIUS)
        hip2.set_color(thigh_color)
        
     
        foot = Sphere([0, -3, 0], radius=DEFAULT_DOT_RADIUS)
        foot.set_color(foot_color)
        path = self.get_path()
        
        foot_circle = Circle(radius=calf_length, color=foot_color).move_to(foot.get_center())
        thigh_1_circle = Circle(radius=thigh_length, color=thigh_color).move_to(hip1.get_center())
        thigh_2_circle = Circle(radius=thigh_length, color=thigh_color).move_to(hip2.get_center()).flip()
        
        thigh1 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[0])
        thigh2 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[1])
        calf1 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[2])
        calf2 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[3])
        inter1 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[4])
        inter2 = always_redraw(lambda: self.get_leg_parts(foot, hip1, hip2)[5])

        # self.play(FadeIn(hip1), FadeIn(hip2))
        # self.play(Create(thigh1), Create(thigh2))
        # self.play(Rotate(thigh1, angle=2*PI, about_point=hip1.get_center(), rate_func=smooth),
        #           Create(thigh_1_circle.rotate(thigh1.get_angle()), rate_func=smooth),
        #           Rotate(thigh2, angle=-2*PI, about_point=hip2.get_center(), rate_func=smooth),
        #           Create(thigh_2_circle.rotate(PI + thigh2.get_angle()), rate_func=smooth),
        #           run_time=2)
        
        # self.play(FadeIn(inter1), FadeIn(inter2))
        
        # self.play(FadeIn(foot))
        # self.play(Create(foot_circle))
       
        # self.play(Create(calf1), Create(calf2))

        # self.play(FadeOut(foot_circle, thigh_1_circle, thigh_2_circle))

        # self.play(foot.animate.move_to(path.get_start()))
        # self.play(MoveAlongPath(foot, path), run_time=2, rate_func=linear)

        self.move_camera(phi=PI/2, theta=0, gamma=PI/2, focal_distance=1000, frame_center=ORIGIN, run_time=3)
        waist_midpoint = Sphere([0, hip_height, -4], radius=DEFAULT_DOT_RADIUS)
        waist = Sphere([0, hip_height, -4 + hip_seperation], radius=DEFAULT_DOT_RADIUS)
        waist.set_color(waist_color)
        line1 = Line3D(waist.get_center(), waist_midpoint.get_center())
        theta = PI/4
        theta_l = 2*PI/3
        theta_b = theta_l - PI/2 + theta
        b = 6
        a = 0.5
        hip_x = Sphere([waist.get_center()[0], waist.get_center()[1] - a*math.cos(theta), 0], radius=DEFAULT_DOT_RADIUS)
        foot = Sphere([hip_x.get_center()[0], hip_x.get_centre()[1] - b*math.sin(theta_b)])
        line2 = Line3D(waist.get_center(), hip_x.get_center())
        self.play(FadeIn(waist), FadeIn(waist_midpoint), FadeIn(hip_x), FadeIn(line1), FadeIn(line2))

        

        self.wait(5)


    def get_path(self):
        x_range = (-1.5, 1.5)
        y_range = (-3, -2)
        num_points = np.random.randint(2, 3)

        def random_point(x_range, y_range):
            x = np.random.uniform(*x_range)
            y = np.random.uniform(*y_range)
            return np.array([x, y, 0])

        points = [random_point(x_range, y_range) for _ in range(num_points)]

        path = VMobject()
        path.set_points_smoothly(points)

        return path


    def get_leg_parts(self, foot:Dot, hip1:Dot, hip2:Dot):
        foot_circle = Circle(radius=calf_length).move_to(foot.get_center())
        thigh1_circle = Circle(radius=thigh_length).move_to(hip1.get_center())
        thigh2_circle = Circle(radius=thigh_length).move_to(hip2.get_center())

        # Find intersection points
        try:
            inter1 = self.intersection_between_circles(thigh1_circle, foot_circle)[0]
            inter2 = self.intersection_between_circles(thigh2_circle, foot_circle)[1]
        except ValueError:
            inter1 = Dot(ORIGIN, color=YELLOW)
            inter2 = Dot(ORIGIN, color=YELLOW)

        # Lines
        thigh1_line = Line(hip1.get_center(), inter1.get_center(), color=BLUE)
        thigh2_line = Line(hip2.get_center(), inter2.get_center(), color=BLUE)
        calf1_line = Line(foot.get_center(), inter1.get_center(), color=GREEN)
        calf2_line = Line(foot.get_center(), inter2.get_center(), color=GREEN)

        return thigh1_line, thigh2_line, calf1_line, calf2_line, inter1, inter2



    def deg_to_rad(self, degrees):
        return degrees * (math.pi / 180)


    def get_thigh_line(self, servo_centre, thigh_angle):
        thigh_end_x = servo_centre.get_x() + thigh_length * math.cos(math.radians(thigh_angle))
        thigh_end_y = servo_centre.get_y() + thigh_length * math.sin(math.radians(thigh_angle))
        thigh_end = np.array([thigh_end_x, thigh_end_y, 0])
        return Line(servo_centre.get_center(), thigh_end, color=thigh_color)

    def intersection_between_circles(self, circle1: Circle, circle2: Circle):
        (x0, y0), r0 = circle1.get_center()[:2], circle1.radius
        (x1, y1), r1 = circle2.get_center()[:2], circle2.radius

        d = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

        if d > (r0 + r1) or d < abs(r0 - r1):
            raise ValueError("No intersection points between the circles")
        
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = math.sqrt(r0 ** 2 - a ** 2)

        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d

        x_a = x2 + h * (y1 - y0) / d
        x_b = x2 - h * (y1 - y0) / d

        y_a = y2 - h * (x1 - x0) / d
        y_b = y2 + h * (x1 - x0) / d

        intersection_point_1 = Dot(point=np.array([x_a, y_a, 0]), color=YELLOW)
        intersection_point_2 = Dot(point=np.array([x_b, y_b, 0]), color=YELLOW)

        return (intersection_point_1, intersection_point_2)
