from manim import *
import numpy as np

class ServoMovement(Scene):
    def construct(self):
        dot = Dot(ORIGIN, 0.1).move_to(ORIGIN+RIGHT)
        servoRadius = 1
      
        circle = Circle(radius=servoRadius).move_to(dot.get_center())
        servoStartAngle = np.deg2rad(-45)
        servoEndAngle = np.deg2rad(225)

        servoAngleTracker = ValueTracker(servoStartAngle)
        servoArrow = always_redraw(lambda: Arrow(dot.get_center(), 
                        dot.get_center() + 
                        RIGHT*servoRadius*np.cos(servoAngleTracker.get_value()) + 
                        UP*servoRadius*np.sin(servoAngleTracker.get_value()), 
                        buff=0))
        
        axes1 = Axes(
            x_range = [0, 6, 1],
            y_range = [0, 6, 1],
            axis_config={"color": WHITE},
        )

        thetaLabel = MathTex(f"\theta")

        axes1.add(axes1.get_axis_labels(x_label="t", y_label=thetaLabel))
        axes1.scale(0.5)

        
        
        self.add(dot, servoArrow, axes1)
        self.wait(2)
        self.play(servoAngleTracker.animate.set_value(servoEndAngle), run_time = 2, rate_func=linear)
        self.play(servoAngleTracker.animate.set_value(servoStartAngle), run_time = 2, rate_func=linear)
        self.wait(2)
        