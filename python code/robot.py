
import time
import constants
from leg import Leg
from hardware_imports import servo2040
from gait import Gait
from constants import LEFT, RIGHT, FRONT, REAR, ZERO_POSITION
from units import Direction, Position, Speed
import misc_functions
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
        for leg in self.legs:
            leg.zero_position()
        
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

        self.print_foot_positions()

    def check_on_button(self):
        if self.controller.buttons.ps:
            if self.state == Robot.STOPPED:
                self.turn_on = not self.turn_on

    def set_direction(self, direction: Direction):
        if self.direction is None:
            self.direction = direction
        elif self.direction != direction:
            self.direction = None
        else:
            self.direction = direction

    def print_foot_positions(self):
        print("Foot position:", end=' ')
        for leg in self.legs:
            foot_position = leg.get_foot_position()
            print("[", format(foot_position.x, '.1f'), format(foot_position.y, '.1f'), format(foot_position.z, '.1f'), "] ", end=' ')
        print()
    
    def handle_direction_controller_input(self):
        if self.controller.axes.left_vertical == 1.0:
            self.set_direction(Direction.FORWARDS)

        elif self.controller.axes.left_vertical == -1.0:
            self.set_direction(Direction.BACKWARDS) 

        elif self.controller.axes.left_horizontal == 1.0:
            self.set_direction(Direction.RIGHT)

        elif self.controller.axes.left_horizontal == -1.0:
            self.set_direction(Direction.LEFT)
        
        else:
            self.direction = None

    def read_controller(self):
        self.controller.update()

        self.handle_direction_controller_input()
        self.check_on_button()

    def run_legs_through_gait(self, step: int, num_positions: int):
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


    def move_between_positions(self, start_pos: Position, end_pos: Position, steps: int):
        interpolated_foot_positions = misc_functions.interpolate_between_positions(start_pos, end_pos, steps)
        for step in range(steps):
            for leg in self.legs:
                leg.set_foot_position(interpolated_foot_positions[step])
            time.sleep(constants.SERVO_COMMAND_DELAY)
        time.sleep(1)

    def stand(self):
        print("Standing up")
        time.sleep(2)

        self.move_between_positions(constants.CARRY_POSITION, constants.BELLY_DOWN_POSITION, self.stand_steps)
        self.move_between_positions(constants.BELLY_DOWN_POSITION, constants.CROUCHED_POSITION, self.stand_steps)
        self.move_between_positions(constants.CROUCHED_POSITION, constants.ZERO_POSITION, self.stand_steps)

    def sleep(self):
        print("Lying down")
        if not self.robot_zeroed:
            print("Zeroing robot first")
            self.zero_robot()
            time.sleep(1)

        self.move_between_positions(constants.ZERO_POSITION, constants.CROUCHED_POSITION, self.stand_steps)
        self.move_between_positions(constants.CROUCHED_POSITION, constants.BELLY_DOWN_POSITION, self.stand_steps)
        self.move_between_positions(constants.BELLY_DOWN_POSITION, constants.ZERO_POSITION, self.stand_steps)

        self.disable()

    def set_translation_orientation(self, translation, rotation):

        (front_left_leg_coords, front_right_leg_coords, back_right_leg_coords, back_left_leg_coords) = orientation.set_translation_orientation(translation, rotation)

        self.front_left_leg.manual_position_control(front_left_leg_coords)
        self.front_right_leg.manual_position_control(front_right_leg_coords)
        self.rear_left_leg.manual_position_control(back_left_leg_coords)
        self.rear_right_leg.manual_position_control(back_right_leg_coords)

    