from leg import Leg
import helper
from servo import servo2040

class Robot:
    def __init__(self):
        self.front_left_leg = Leg(servo2040.SERVO_1, servo2040.SERVO_7, servo2040.SERVO_13, helper.LegType.FrontLeft)
        self.front_right_leg = Leg(servo2040.SERVO_2, servo2040.SERVO_8, servo2040.SERVO_14, helper.LegType.FrontRight)
        self.rear_right_leg = Leg(servo2040.SERVO_3, servo2040.SERVO_9, servo2040.SERVO_15, helper.LegType.BackRight)
        self.rear_left_leg = Leg(servo2040.SERVO_4, servo2040.SERVO_10, servo2040.SERVO_16, helper.LegType.BackLeft)

    def zero_robot(self):
        self.front_left_leg.zero_position()
        self.front_right_leg.zero_position()
        self.rear_right_leg.zero_position()
        self.rear_left_leg.zero_position()

