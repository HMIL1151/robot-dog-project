from hardware_imports import Servo
import inverse_kinematics
from constants import ZERO_X, ZERO_Y, ZERO_Z, SERVO_OFFSET_DEG


class Leg:
    def __init__ (self, hipServoNum, frontServoNum, rearServoNum, side, face):
        self.hip_servo = Servo(hipServoNum)
        self.left_servo = Servo(frontServoNum)
        self.right_servo = Servo(rearServoNum)
        self.side = side
        self.face = face
        self.enable()

    def zero_position(self):
        self.manual_position_control((ZERO_X, ZERO_Y, ZERO_Z))

    def enable(self):
        self.hip_servo.enable()
        self.left_servo.enable()
        self.right_servo.enable()

    def disable(self):
        self.hip_servo.disable()
        self.left_servo.disable()
        self.right_servo.disable()

    def set_servo_angles(self, servo_angles):
        servo_commands = self.kinematic_angles_to_servo_angles(servo_angles)

        self.hip_servo.value(servo_commands[0])
        self.left_servo.value(servo_commands[1])
        self.right_servo.value(servo_commands[2])

    def get_servo_values(self):
        return {
            "hip": self.hip_servo.value(),
            "left": self.left_servo.value(),
            "right": self.right_servo.value()
        }

    def manual_servo_control(self, servo_angles):
        self.hip_servo.value(servo_angles[0])
        self.left_servo.value(servo_angles[1])
        self.right_servo.value(servo_angles[2])

    def manual_position_control(self, position):
        servo_angles = inverse_kinematics.inverse_kinematics(position)
        servo_commands = self.kinematic_angles_to_servo_angles(servo_angles)

        print(servo_commands)

        self.hip_servo.value(servo_commands[0])
        self.left_servo.value(servo_commands[1])
        self.right_servo.value(servo_commands[2])

    def deactivate_hip(self):
        self.hip_servo.disable()

    def kinematic_angles_to_servo_angles(self, kinematic_angles):
        hip_angle, left_angle, right_angle = kinematic_angles

        left_servo = (right_angle - SERVO_OFFSET_DEG) * self.side
        right_servo = (left_angle - SERVO_OFFSET_DEG) * -self.side

        if (self.side * self.face < 0):
            hip_servo = -hip_angle
        else:
            hip_servo = hip_angle

        return (hip_servo, left_servo, right_servo)