import inverse_kinematics
from constants import ZERO_X, ZERO_Y, ZERO_Z
import bezier_curve
import math


class Gait:
    CRAWL = 0
    TROT = 1

    STEPS_PER_SECOND = 10
    STEP_HEIGHT = 20
    STEP_CURVE_DELTA = 0.2
    STEP_DISTANCE = 50

    def __init__(self, gait_type):
        self.gait_type = gait_type
        self.speed = None
        self.stance_steps = None
        self.swing_steps = None

    def calculate_gait(self, speed):
        self.stance_steps = int(Gait.STEPS_PER_SECOND * (Gait.STEP_DISTANCE / speed))
        self.swing_steps = int(self.stance_steps / 3)
        path_points = bezier_curve.calculate_curve(Gait.STEP_DISTANCE, Gait.STEP_HEIGHT, Gait.STEP_CURVE_DELTA, self.stance_steps, self.swing_steps)
        print("Path points:", path_points)
        try:
            servo_positions = inverse_kinematics.ik_points(path_points)
            return servo_positions
        except Exception as e:
            raise ValueError("Error occurred during inverse kinematics: {}".format(e))

    def get_start_indices(self):
        if self.gait_type == Gait.CRAWL:
            return [0, 
                    int(self.swing_steps + self.stance_steps/3), 
                    int(self.swing_steps + 2*self.stance_steps/3), 
                    int(self.swing_steps)]
        elif self.gait_type == Gait.TROT:
            return [0, 0, 0, 0]
        else:
            raise ValueError("Invalid gait type")