
import time
from leg import Leg
from hardware_imports import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
from gait import Gait
import math
from constants import ZERO_X, ZERO_Y, ZERO_Z, HIP_UP_ANGLE_DEG
from units import Speed, Direction

class Robot:
    FRONT_LEFT_LEG = 0
    FRONT_RIGHT_LEG = 1
    REAR_RIGHT_LEG = 2
    REAR_LEFT_LEG = 3

    def __init__(self):
        self.front_left_leg = Leg(servo2040.SERVO_1, servo2040.SERVO_7, servo2040.SERVO_13)
        self.front_right_leg = Leg(servo2040.SERVO_2, servo2040.SERVO_8, servo2040.SERVO_14)
        self.rear_right_leg = Leg(servo2040.SERVO_3, servo2040.SERVO_9, servo2040.SERVO_15)
        self.rear_left_leg = Leg(servo2040.SERVO_4, servo2040.SERVO_10, servo2040.SERVO_16)
        self.speed = None
        self.direction = None
        self.gait = None
        self.robot_zeroed = False
        self.x = 0
        self.y = 0

    def zero_robot(self):
        self.front_left_leg.zero_position('left')
        self.front_right_leg.zero_position('right')
        self.rear_right_leg.zero_position('right')
        self.rear_left_leg.zero_position('left')
        self.robot_zeroed = True
    
    def is_robot_zeroed(self):
        return self.robot_zeroed

    def test_all(self):
        self.front_left_leg.test_all()
        self.front_right_leg.test_all()
        self.rear_right_leg.test_all()
        self.rear_left_leg.test_all()

    def disable(self):
        self.front_left_leg.disable()
        self.front_right_leg.disable()
        self.rear_right_leg.disable()
        self.rear_left_leg.disable()

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.direction = direction

    def set_gait(self, gait):
        self.gait = Gait(gait)
        #try:
        self.servo_positions = self.gait.calculate_gait(self.speed)
        self.start_indicies = self.gait.get_start_indices()
        #except Exception as e:
           # raise ValueError(f"Error occurred while calculating gait: {e}") from e

    def go(self):
        print("Robot is moving")
        if self.gait:
            num_positions = len(self.servo_positions)

            if (self.direction == Direction.FORWARDS):
                for step in range(num_positions):
                    self.run_legs_through_gait(step, num_positions)
            else:
                for step in reversed(range(num_positions)):
                    self.run_legs_through_gait(step, num_positions)

        else:
            print("No gait set")

    def stop(self):
        print("Robot has stopped")

    def go_to_distance(self, distance):
        print(f"Robot is moving to distance: {distance}")

    def go_for_duration(self, duration):
        print(f"Robot is moving for duration: {duration}")

    def go_for_steps(self, steps):
        for _ in range(steps):
            self.go()
            print(f"Step {_ + 1} of {steps} completed")

    def go_to_position(self, x, y):
        self.direction = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
        print(f"Going to position: ({x}, {y}) in direction: {self.direction}")

    def get_position(self):
        return self.x, self.y

    def manual_servo_control(self, servo_angles):
        self.front_left_leg.manual_servo_control(servo_angles)
        # self.front_right_leg.manual_servo_control(servo_angles)
        # self.rear_left_leg.manual_servo_control(servo_angles)
        # self.rear_right_leg.manual_servo_control(servo_angles)

    def manual_position_control(self, position):
        self.front_left_leg.manual_position_control(position, 'left')
        self.front_right_leg.manual_position_control(position, 'right')
        self.rear_left_leg.manual_position_control(position, 'left')
        self.rear_right_leg.manual_position_control(position, 'right')

    def deactivate_all_hips(self):
        self.front_left_leg.deactivate_hip()
        self.front_right_leg.deactivate_hip()
        self.rear_left_leg.deactivate_hip()
        self.rear_right_leg.deactivate_hip()

    def run_legs_through_gait(self, step, num_positions):

        front_left_positions = self.servo_positions[(self.start_indicies[Robot.FRONT_LEFT_LEG] + step) % num_positions]
        front_right_positions = self.servo_positions[(self.start_indicies[Robot.FRONT_RIGHT_LEG] + step) % num_positions]
        rear_right_positions = self.servo_positions[(self.start_indicies[Robot.REAR_RIGHT_LEG] + step) % num_positions]
        rear_left_positions = self.servo_positions[(self.start_indicies[Robot.REAR_LEFT_LEG] + step) % num_positions]

        self.front_left_leg.set_servo_angles(front_left_positions, 'left')
        self.front_right_leg.set_servo_angles(front_right_positions, 'right')
        self.rear_right_leg.set_servo_angles(rear_right_positions, 'right')
        self.rear_left_leg.set_servo_angles(rear_left_positions, 'left')

        print("Setting servos to ", front_left_positions, front_right_positions, rear_right_positions, rear_left_positions)

        time.sleep(0.05)

    def set_carry_position(self):
        self.front_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 240, 90), 'left')
        self.rear_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 90, 240), 'left')
        self.front_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 240, 90), 'right')
        self.rear_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 90, 240), 'right')

    def stand(self):
        #go from carry position to hip angle 0 over a number of steps
        steps = 10
        angle_step = HIP_UP_ANGLE_DEG / steps
        for step in range(steps):
            self.front_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG - step * angle_step, 240, 90), 'left')
            self.rear_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG - step * angle_step, 90, 240), 'left')
            self.front_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG - step * angle_step, 240, 90), 'right')
            self.rear_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG - step * angle_step, 90, 240), 'right')
            time.sleep(0.1)

        time.sleep(5)

        # interpolate from current servo angles to (0, 180, 180) for all legs over a number of steps
        target_angles = (0, 180, 180)
        interp_steps = 15

        # Get current angles for each leg
        fl_current = (0, 240, 90)
        fr_current = (0, 240, 90)
        rl_current = (0, 90, 240)
        rr_current = (0, 90, 240)

        for step in range(1, interp_steps + 1):
            ratio = step / interp_steps
            fl_interp = tuple(fl_current[i] + (target_angles[i] - fl_current[i]) * ratio for i in range(3))
            fr_interp = tuple(fr_current[i] + (target_angles[i] - fr_current[i]) * ratio for i in range(3))
            rl_interp = tuple(rl_current[i] + (target_angles[i] - rl_current[i]) * ratio for i in range(3))
            rr_interp = tuple(rr_current[i] + (target_angles[i] - rr_current[i]) * ratio for i in range(3))

            self.front_left_leg.set_servo_angles(fl_interp, 'left')
            self.front_right_leg.set_servo_angles(fr_interp, 'right')
            self.rear_left_leg.set_servo_angles(rl_interp, 'left')
            self.rear_right_leg.set_servo_angles(rr_interp, 'right')
            time.sleep(0.1)
        
