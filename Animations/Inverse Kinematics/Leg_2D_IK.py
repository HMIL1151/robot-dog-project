import manim
from manim import *
from manim import config
import math

config["fullscreen"] = True
config["window_monitor"] = 1  # Change this to the monitor number you want to use (starting from 1)

thigh_length = 1
calf_length = 2

thigh_color = BLUE
foot_color = GREEN

class FirstScene(Scene):
    def construct(self):
        servo_1_centre = Dot(color=thigh_color).shift(LEFT * 1).shift(UP * 2)
        servo_2_centre = Dot(color=thigh_color).shift(RIGHT * 1).shift(UP * 2)
        
        foot = Dot(color=foot_color).shift(DOWN * 0.5)
        foot_dashed_circle = self.get_dotted_circle(foot.get_center(), calf_length, foot_color)
        foot_circle = Circle(radius=calf_length, color=foot_color).move_to(foot.get_center())

        thigh_1_dashed_circle = self.get_dotted_circle(servo_1_centre.get_center(), thigh_length, thigh_color)
        thigh_2_dashed_circle = self.get_dotted_circle(servo_2_centre.get_center(), thigh_length, thigh_color)
        thigh_1_circle = Circle(radius=thigh_length, color=thigh_color).move_to(servo_1_centre.get_center())
        thigh_2_circle = Circle(radius=thigh_length, color=thigh_color).move_to(servo_2_centre.get_center())

        self.add(servo_1_centre, servo_2_centre, foot, thigh_1_dashed_circle, thigh_2_dashed_circle, foot_dashed_circle)

        servo_1_intersection_points = self.intersection_between_circles(thigh_1_circle, foot_circle)
        servo_2_intersection_points = self.intersection_between_circles(thigh_2_circle, foot_circle)

        intersection_point_1 = servo_1_intersection_points[0]
        intersection_point_2 = servo_2_intersection_points[1]

        thigh1 = Line(servo_1_centre.get_center(), intersection_point_1.get_center(), color=thigh_color)
        thigh2 = Line(servo_2_centre.get_center(), intersection_point_2.get_center(), color=thigh_color)

        calf1 = Line(foot.get_center(), intersection_point_1, color=foot_color)
        calf2 = Line(foot.get_center(), intersection_point_2, color=foot_color)

        self.add(intersection_point_1, 
                 intersection_point_2, 
                 thigh1, 
                 thigh2, 
                 calf1, 
                 calf2, 
                 servo_1_centre, 
                 servo_2_centre, 
                 foot, 
                 thigh_1_dashed_circle, 
                 thigh_2_dashed_circle, 
                 foot_dashed_circle
                 )
        
        self.wait(2)

        # self.wait(25000)

    def get_thigh_line(self, servo_centre, thigh_angle):
        thigh_end_x = servo_centre.get_x() + thigh_length * math.cos(math.radians(thigh_angle))
        thigh_end_y = servo_centre.get_y() + thigh_length * math.sin(math.radians(thigh_angle))
        thigh_end = np.array([thigh_end_x, thigh_end_y, 0])
        return Line(servo_centre.get_center(), thigh_end, color=thigh_color)

    def get_dotted_circle(self, centre, radius, colour):
        base_circle = Circle(radius=radius, color=colour).move_to(centre)

        dotted_circle = DashedVMobject(
            base_circle,
            num_dashes=30,
            dash_length=0.1,
            dashed_ratio=0.5,
            stroke_width=2,
        )
        return dotted_circle

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
