
import time
import constants
from leg import Leg
from hardware_imports import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
from gait import Gait
import math
from constants import ZERO_X, ZERO_Y, ZERO_Z, HIP_UP_ANGLE_DEG, LEFT, RIGHT, FRONT, REAR, ZERO_POSITION
from units import Direction, Speed
import misc_functions
import inverse_kinematics
import orientation
import robot_orientation
import controller

class Robot:
    FRONT_LEFT_LEG = 0
    FRONT_RIGHT_LEG = 1
    REAR_RIGHT_LEG = 2
    REAR_LEFT_LEG = 3

    STOPPED = 0
    SETTING_OFF = 1
    MOVING = 2
    STOPPING = 3

    def __init__(self):
        self.front_left_leg = Leg(servo2040.SERVO_1, servo2040.SERVO_7, servo2040.SERVO_13, LEFT, FRONT)
        self.front_right_leg = Leg(servo2040.SERVO_2, servo2040.SERVO_8, servo2040.SERVO_14, RIGHT, FRONT)
        self.rear_right_leg = Leg(servo2040.SERVO_3, servo2040.SERVO_9, servo2040.SERVO_15, RIGHT, REAR)
        self.rear_left_leg = Leg(servo2040.SERVO_4, servo2040.SERVO_10, servo2040.SERVO_12, LEFT, REAR)
        self.legs = [self.front_left_leg, self.front_right_leg, self.rear_right_leg, self.rear_left_leg]
        self.orientation = robot_orientation.RobotOrientation()
        self.controller = controller.Controller()

        self.speed = Speed.in_mm_per_second(20)
        self.direction = None
        self.starting_direction = None
        self.gait = Gait(Gait.TROT)
        self.robot_zeroed = False

        self.stand_steps = 20
        self.current_step_index = 0
        self.set_carry_position()
        self.foot_positions = ZERO_POSITION
        self.state = Robot.STOPPED

        self.turn_on = False
        

    def zero_robot(self):
        self.front_left_leg.zero_position()
        self.front_right_leg.zero_position()
        self.rear_right_leg.zero_position()
        self.rear_left_leg.zero_position()
        self.robot_zeroed = True

    def update_robot(self):
        self.read_controller()

        if self.state == Robot.STOPPED:
            if self.gait is None or self.speed is None or self.direction is None:
                self.foot_positions = [ZERO_POSITION]
                self.run_legs_through_gait(self.current_step_index, len(self.foot_positions))
                return
            self.state = Robot.SETTING_OFF
            self.robot_zeroed = False
            self.starting_direction = self.direction
            self.foot_positions = self.gait.calculate_starting_gait(self.speed, self.direction)
            start_indices = self.gait.get_start_indices()

            for i in range(len(self.legs)):
                self.legs[i].start_index = start_indices[i]

            self.current_step_index = 0
        
        if self.state == Robot.SETTING_OFF:
            if self.current_step_index < len(self.foot_positions):
                self.run_legs_through_gait(self.current_step_index, len(self.foot_positions))
                self.current_step_index += 1
            else:
                self.state = Robot.MOVING

                self.foot_positions = self.gait.calculate_walk_gait(self.speed, self.starting_direction)
                start_indices = self.gait.get_start_indices()

                for i in range(len(self.legs)):
                    self.legs[i].start_index = start_indices[i]

                self.current_step_index = 0

        if self.state == Robot.MOVING:
            if self.current_step_index < len(self.foot_positions):
                self.run_legs_through_gait(self.current_step_index, len(self.foot_positions))
                self.current_step_index += 1
            elif self.direction is not None:
                self.current_step_index = 0
            else:
                self.state = Robot.STOPPING
                self.foot_positions = self.gait.calculate_stopping_gait(self.speed, self.starting_direction)
                start_indices = self.gait.get_start_indices()

                for i in range(len(self.legs)):
                    self.legs[i].start_index = start_indices[i]

                self.current_step_index = 0
        
        if self.state == Robot.STOPPING:
            if self.current_step_index < len(self.foot_positions):
                self.run_legs_through_gait(self.current_step_index, len(self.foot_positions))
                self.current_step_index += 1
            else:
                self.state = Robot.STOPPED
                self.robot_zeroed = True
                self.current_step_index = 0
                self.direction = None
                self.starting_direction = None
                self.foot_positions = None

    def check_on_button(self):
        self.controller.update()
        if self.controller.buttons.ps:
            self.turn_on = not self.turn_on

    def read_controller(self):
        self.controller.update()

        if self.controller.axes.left_vertical == 1.0:
            if self.direction is None:
                self.direction = Direction.FORWARDS
            elif self.direction != Direction.FORWARDS:
                self.direction = None
            else:
                self.direction = Direction.FORWARDS

        elif self.controller.axes.left_vertical == -1.0:
            if self.direction is None:
                self.direction = Direction.BACKWARDS
            elif self.direction != Direction.BACKWARDS:
                self.direction = None
            else:
                self.direction = Direction.BACKWARDS

        elif self.controller.axes.left_horizontal == 1.0:
            if self.direction is None:
                self.direction = Direction.RIGHT
            elif self.direction != Direction.RIGHT:
                self.direction = None
            else:
                self.direction = Direction.RIGHT

        elif self.controller.axes.left_horizontal == -1.0:
            if self.direction is None:
                self.direction = Direction.LEFT
            elif self.direction != Direction.LEFT:
                self.direction = None
            else:
                self.direction = Direction.LEFT
        
        else:
            self.direction = None

        if self.controller.buttons.ps:
            if self.state == Robot.STOPPED:
                self.turn_on = not self.turn_on

        print("Foot position:", end=' ')
        for leg in self.legs:
            foot_position = leg.get_foot_position()
            print("[", format(foot_position.x, '.1f'), format(foot_position.y, '.1f'), format(foot_position.z, '.1f'), "] ", end=' ')

        print()

    def run_legs_through_gait(self, step, num_positions):
        for leg in self.legs:
            foot_position = self.foot_positions[(leg.start_index + step) % num_positions]
            leg.set_foot_position(foot_position)
        



    def disable(self):
        self.front_left_leg.disable()
        self.front_right_leg.disable()
        self.rear_right_leg.disable()
        self.rear_left_leg.disable()

    def set_carry_position(self):
        for leg in self.legs:
            leg.set_foot_position(constants.CARRY_POSITION)





    def stand(self):
        print("Standing up")
        time.sleep(2)

        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.CARRY_POSITION, constants.BELLY_DOWN_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)
        
        time.sleep(1)

        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.BELLY_DOWN_POSITION, constants.CROUCHED_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)

        time.sleep(1)

        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.CROUCHED_POSITION, constants.ZERO_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)

        
        time.sleep(1)






    def sleep(self):
        print("Lying down")
        if not self.robot_zeroed:
            print("Zeroing robot first")
            self.zero_robot()
            time.sleep(1)

        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.ZERO_POSITION, constants.CROUCHED_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)
        
        time.sleep(1)
        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.CROUCHED_POSITION, constants.BELLY_DOWN_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)

        time.sleep(1)
        interpolated_foot_positions = misc_functions.interpolate_between_positions(constants.BELLY_DOWN_POSITION, constants.CARRY_POSITION, self.stand_steps)
        for step in range(self.stand_steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)

        time.sleep(1)

        self.disable()






    def set_translation_orientation(self, translation, rotation):

        (front_left_leg_coords, front_right_leg_coords, back_right_leg_coords, back_left_leg_coords) = orientation.set_translation_orientation(translation, rotation)

        self.front_left_leg.manual_position_control(front_left_leg_coords)
        self.front_right_leg.manual_position_control(front_right_leg_coords)
        self.rear_left_leg.manual_position_control(back_left_leg_coords)
        self.rear_right_leg.manual_position_control(back_right_leg_coords)

    def rotation_test(self, iterations):

        angle_max = 15
        count = 0
        count_max = 3
        increment = 1
        direction = 1
        angle = 0

        for i in range (iterations):

            while count < count_max:
                self.set_translation_orientation((0, 0, 0), (angle, 0, 0))
                angle += increment * direction
                if angle > angle_max or angle < -angle_max:
                    direction *= -1
                    angle = max(min(angle, angle_max), -angle_max)
                    count += 1

            # Interpolate angle back to zero
            while abs(angle) > 0.01:  # Use a small threshold to avoid floating point issues
                angle -= increment * (1 if angle > 0 else -1)
                # Clamp to zero if we overshoot
                if (angle > 0 and angle - increment < 0) or (angle < 0 and angle + increment > 0):
                    angle = 0
                self.set_translation_orientation((0, 0, 0), (angle, 0, 0))
            count = 0

            angle_max = angle_max / 2



            while count < count_max:
                self.set_translation_orientation((0, 0, 0), (0, angle, 0))
                angle += increment * direction
                if angle > angle_max or angle < -angle_max:
                    direction *= -1
                    angle = max(min(angle, angle_max), -angle_max)
                    count += 1

            # Interpolate angle back to zero
            while abs(angle) > 0.01:  # Use a small threshold to avoid floating point issues
                angle -= increment * (1 if angle > 0 else -1)
                # Clamp to zero if we overshoot
                if (angle > 0 and angle - increment < 0) or (angle < 0 and angle + increment > 0):
                    angle = 0
                self.set_translation_orientation((0, 0, 0), (0, angle, 0))
            count = 0

            angle_max = angle_max * 2


            while count < count_max:
                self.set_translation_orientation((0, 0, 0), (0, 0, angle))
                angle += increment * direction
                if angle > angle_max or angle < -angle_max:
                    direction *= -1
                    angle = max(min(angle, angle_max), -angle_max)
                    count += 1

            # Interpolate angle back to zero
            while abs(angle) > 0.01:  # Use a small threshold to avoid floating point issues
                angle -= increment * (1 if angle > 0 else -1)
                # Clamp to zero if we overshoot
                if (angle > 0 and angle - increment < 0) or (angle < 0 and angle + increment > 0):
                    angle = 0
                self.set_translation_orientation((0, 0, 0), (0, 0, angle))


    def translation_test(self, iterations):

        translation_max = 20
        count = 0
        count_max = 3
        increment = 1
        direction = 1
        translation = 0

        for i in range (iterations):

            while count < count_max:
                self.set_translation_orientation((translation, 0, 0), (0, 0, 0))
                translation += increment * direction
                if translation > translation_max or translation < -translation_max:
                    direction *= -1
                    translation = max(min(translation, translation_max), -translation_max)
                    count += 1

            # Interpolate translation back to zero
            while abs(translation) > 0.01:  # Use a small threshold to avoid floating point issues
                translation -= increment * (1 if translation > 0 else -1)
                # Clamp to zero if we overshoot
                if (translation > 0 and translation - increment < 0) or (translation < 0 and translation + increment > 0):
                    translation = 0
                self.set_translation_orientation((translation, 0, 0), (0, 0, 0))
            count = 0

            translation_max = translation_max / 2



            while count < count_max:
                self.set_translation_orientation((0, translation, 0), (0, 0, 0))
                translation += increment * direction
                if translation > translation_max or translation < -translation_max:
                    direction *= -1
                    translation = max(min(translation, translation_max), -translation_max)
                    count += 1

            # Interpolate translation back to zero
            while abs(translation) > 0.01:  # Use a small threshold to avoid floating point issues
                translation -= increment * (1 if translation > 0 else -1)
                # Clamp to zero if we overshoot
                if (translation > 0 and translation - increment < 0) or (translation < 0 and translation + increment > 0):
                    translation = 0
                self.set_translation_orientation((0, translation, 0), (0, 0, 0))
            count = 0

            translation_max = translation_max * 2


            while count < count_max:
                self.set_translation_orientation((0, 0, translation), (0, 0, 0))
                translation += increment * direction
                if translation > translation_max or translation < -translation_max:
                    direction *= -1
                    translation = max(min(translation, translation_max), -translation_max)
                    count += 1

            # Interpolate translation back to zero
            while abs(translation) > 0.01:  # Use a small threshold to avoid floating point issues
                translation -= increment * (1 if translation > 0 else -1)
                # Clamp to zero if we overshoot
                if (translation > 0 and translation - increment < 0) or (translation < 0 and translation + increment > 0):
                    translation = 0
                self.set_translation_orientation((0, 0, translation), (0, 0, 0))

      