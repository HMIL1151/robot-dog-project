
import time
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
        self.x = 0
        self.y = 0
        self.stand_steps = 20
        self.current_step_index = 0
        self.set_carry_position()
        self.foot_positions = ZERO_POSITION
        self.state = Robot.STOPPED
        

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

                #TODO: Using points here so we can update leg positions directly so we can then print them out
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
                self.current_step_index = 0
                self.direction = None
                self.starting_direction = None
                self.foot_positions = None

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

        print("Foot position:", end=' ')
        for leg in self.legs:
            foot_position = leg.get_foot_position()
            print("[", format(foot_position.x, '.1f'), format(foot_position.y, '.1f'), format(foot_position.z, '.1f'), "] ", end=' ')

        print()

        











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

    def set_gait(self, gait, direction):
        self.gait = Gait(gait)
        self.start_indicies = self.gait.get_start_indices()
        self.gait_set = True

    def go(self):
        print("Robot is moving")
        if self.gait:
            num_positions = len(self.servo_positions)
            if self.current_step_index is None:
                self.current_step_index = 0
            else:
                self.current_step_index = (self.current_step_index + 1) % num_positions
            self.run_legs_through_gait(self.current_step_index, num_positions)
            

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
        self.front_right_leg.manual_servo_control(servo_angles)
        self.rear_left_leg.manual_servo_control(servo_angles)
        self.rear_right_leg.manual_servo_control(servo_angles)

    def manual_position_control(self, positions):
        front_left_position, front_right_position, rear_right_position, rear_left_position = positions
        self.front_left_leg.manual_position_control(front_left_position)
        self.front_right_leg.manual_position_control(front_right_position)
        self.rear_left_leg.manual_position_control(rear_left_position)
        self.rear_right_leg.manual_position_control(rear_right_position)

    def deactivate_all_hips(self):
        self.front_left_leg.deactivate_hip()
        self.front_right_leg.deactivate_hip()
        self.rear_left_leg.deactivate_hip()
        self.rear_right_leg.deactivate_hip()




    def run_legs_through_gait(self, step, num_positions):
        for leg in self.legs:
            foot_position = self.foot_positions[(leg.start_index + step) % num_positions]
            leg.set_foot_position(foot_position)



    def set_carry_position(self):
        self.front_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 240, 90))
        self.rear_left_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 90, 240))
        self.front_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 240, 90))
        self.rear_right_leg.set_servo_angles((HIP_UP_ANGLE_DEG, 90, 240))

    def stand(self):
        time.sleep(2)


        #from hips up to hips level
        print("Standing up")
        front_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 240, 90), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps)
        rear_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 90, 240), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 240, 90), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps)
        rear_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 90, 240), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps)

        for step in range(self.stand_steps):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[step])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[step])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[step])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[step])
            time.sleep(0.05)

        time.sleep(1)

        #move stand up crouched
        print("Moving to crouched position")
        front_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (0, 180, 180), self.stand_steps)
        rear_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (0, 180, 180), self.stand_steps)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (0, 180, 180), self.stand_steps)
        rear_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (0, 180, 180), self.stand_steps)

        for i in range(self.stand_steps + 1):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[i])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[i])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[i])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[i])
            time.sleep(0.05)

        time.sleep(1)

        #stand up straight
        print("Standing up straight")
        front_left_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), inverse_kinematics.inverse_kinematics(ZERO_POSITION), self.stand_steps)
        rear_left_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), inverse_kinematics.inverse_kinematics(ZERO_POSITION), self.stand_steps)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), inverse_kinematics.inverse_kinematics(ZERO_POSITION), self.stand_steps)
        rear_right_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), inverse_kinematics.inverse_kinematics(ZERO_POSITION), self.stand_steps)

        for i in range(self.stand_steps + 1):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[i])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[i])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[i])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[i])
            time.sleep(0.05)

        time.sleep(1)

    def sleep(self):
        self.zero_robot()
        time.sleep(1)

        print("Standing up straight")
        front_left_servo_positions =  misc_functions.interpolate_between_servo_positions(inverse_kinematics.inverse_kinematics(ZERO_POSITION), (0, 180, 180), self.stand_steps)
        rear_left_servo_positions =   misc_functions.interpolate_between_servo_positions(inverse_kinematics.inverse_kinematics(ZERO_POSITION), (0, 180, 180), self.stand_steps)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions(inverse_kinematics.inverse_kinematics(ZERO_POSITION), (0, 180, 180), self.stand_steps)
        rear_right_servo_positions =  misc_functions.interpolate_between_servo_positions(inverse_kinematics.inverse_kinematics(ZERO_POSITION), (0, 180, 180), self.stand_steps)

        for i in range(self.stand_steps + 1):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[i])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[i])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[i])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[i])
            time.sleep(0.05)

        time.sleep(1)

        #move stand up crouched
        print("Moving to crouched position")
        front_left_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps*2)
        rear_left_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps*2)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps*2)
        rear_right_servo_positions = misc_functions.interpolate_between_servo_positions((0, 180, 180), (HIP_UP_ANGLE_DEG, 180, 180), self.stand_steps*2)

        for i in range(self.stand_steps*2 + 1):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[i])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[i])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[i])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[i])
            time.sleep(0.05)

        time.sleep(1)

        #from hips up to hips level
        print("Standing up")
        front_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (HIP_UP_ANGLE_DEG, 240, 90), self.stand_steps)
        rear_left_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (HIP_UP_ANGLE_DEG, 90, 240), self.stand_steps)
        front_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (HIP_UP_ANGLE_DEG, 240, 90), self.stand_steps)
        rear_right_servo_positions = misc_functions.interpolate_between_servo_positions((HIP_UP_ANGLE_DEG, 180, 180), (HIP_UP_ANGLE_DEG, 90, 240), self.stand_steps)

        for step in range(self.stand_steps):
            self.front_left_leg.set_servo_angles(front_left_servo_positions[step])
            self.rear_left_leg.set_servo_angles(rear_left_servo_positions[step])
            self.front_right_leg.set_servo_angles(front_right_servo_positions[step])
            self.rear_right_leg.set_servo_angles(rear_right_servo_positions[step])
            time.sleep(0.05)

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

      