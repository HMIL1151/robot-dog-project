import inverse_kinematics
from constants import ZERO_X, ZERO_Y, ZERO_Z
import bezier_curve
import math
from units import Direction, Speed


class Gait:
    CRAWL = 0
    TROT = 1

    STEPS_PER_SECOND = 10
    STEP_HEIGHT = 25 
    STEP_CURVE_DELTA = 0.2
    STEP_DISTANCE = 20

    def __init__(self, gait_type):
        self.gait_type = gait_type
        self.direction = None
        self.speed = None
        self.stance_steps = None
        self.swing_steps = None

    def calculate_walk_gait(self, speed: Speed, direction: Direction):
        self.direction = direction
        self.stance_steps = int(Gait.STEPS_PER_SECOND * (Gait.STEP_DISTANCE / speed))

        if self.gait_type == Gait.CRAWL:
            self.swing_steps = int(self.stance_steps / 3)
        elif self.gait_type == Gait.TROT:
            self.swing_steps = int(self.stance_steps)

        if direction == Direction.CLOCKWISE:
            gait_direction = Direction.RIGHT
        elif direction == Direction.COUNTERCLOCKWISE:
            gait_direction = Direction.LEFT
        else:
            gait_direction = direction

        path_points = bezier_curve.calculate_curve(Gait.STEP_DISTANCE, Gait.STEP_HEIGHT, Gait.STEP_CURVE_DELTA, self.stance_steps, self.swing_steps, gait_direction)

        servo_positions = inverse_kinematics.ik_points(path_points)
        return (path_points, servo_positions)

    def calculate_starting_gait(self, speed, direction):
        return self.calculate_walk_gait(speed, direction)
    def calculate_stopping_gait(self, speed, direction):
        return self.calculate_walk_gait(speed, direction)

    def get_start_indices(self):
        if self.gait_type == Gait.CRAWL:
            return [0, 
                    int(self.swing_steps + self.stance_steps/3), 
                    int(self.swing_steps + 2*self.stance_steps/3), 
                    int(self.swing_steps)]
        elif self.gait_type == Gait.TROT:
            return [0, 
                    int(self.swing_steps), 
                    0, 
                    int(self.swing_steps)]
        else:
            raise ValueError("Invalid gait type")