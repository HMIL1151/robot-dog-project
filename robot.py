import time
from leg import Leg
from hardware_imports import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
from gait import Gait
import math

class Robot:
    
    ZERO_X = 0
    ZERO_Y = 150
    ZERO_Z = 95.5

    def __init__(self):
        self.front_left_leg = Leg(servo2040.SERVO_1, servo2040.SERVO_7, servo2040.SERVO_13)
        # self.front_right_leg = Leg(servo2040.SERVO_2, servo2040.SERVO_8, servo2040.SERVO_14)
        # self.rear_right_leg = Leg(servo2040.SERVO_3, servo2040.SERVO_9, servo2040.SERVO_15)
        # self.rear_left_leg = Leg(servo2040.SERVO_4, servo2040.SERVO_10, servo2040.SERVO_16)
        self.speed = None
        self.direction = None
        self.gait = None
        self.robot_zeroed = False
        self.x = 0
        self.y = 0

    def zero_robot(self):
        self.front_left_leg.zero_position()
        self.front_right_leg.zero_position()
        self.rear_right_leg.zero_position()
        self.rear_left_leg.zero_position()
        self.robot_zeroed = True
    
    def is_robot_zeroed(self):
        return self.robot_zeroed

    def test_all(self):
        self.front_left_leg.test_all()
        self.front_right_leg.test_all()
        self.rear_right_leg.test_all()
        self.rear_left_leg.test_all()

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.direction = direction

    def set_gait(self, gait):
        self.gait = gait
        try:
            self.servo_positions = Gait.calculate_gait(self, gait, self.speed)
        except Exception as e:
            raise ValueError(f"Error occurred while calculating gait: {e}") from e

    def go(self):
        print("Robot is moving")
        if self.gait:
            for position in self.servo_positions:
                self.front_left_leg.set_servo_angles(position)
                time.sleep(0.1)
        else:
            print("No gait set")

    def stop(self):
        print("Robot has stopped")

    def go_to_distance(self, distance):
        print(f"Robot is moving to distance: {distance}")

    def go_for_duration(self, duration):
        print(f"Robot is moving for duration: {duration}")

    def go_to_position(self, x, y):
        self.direction = math.hypot(x, y)
        print(f"Going to position: ({x}, {y}) in direction: {self.direction}")

    def get_position(self):
        return self.x, self.y