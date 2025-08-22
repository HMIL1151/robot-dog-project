from hardware_imports import Servo
import inverse_kinematics
from constants import ZERO_X, ZERO_Y, ZERO_Z


class Leg:
    def __init__ (self, hipServoNum, frontServoNum, rearServoNum):
        self.hip_servo = Servo(hipServoNum)
        self.left_servo = Servo(frontServoNum)
        self.right_servo = Servo(rearServoNum)
        self.left_servo_direction = 1
        self.right_servo_direction = -1
        self.servo_offset = 180
        self.enable()

    def zero_position(self):
        zero_angles = inverse_kinematics.inverse_kinematics((ZERO_X, ZERO_Y, ZERO_Z))
        self.hip_servo.value(zero_angles[0])
        self.left_servo.value(zero_angles[1])
        self.right_servo.value(zero_angles[2])

    def enable(self):
        self.hip_servo.enable()
        self.left_servo.enable()
        self.right_servo.enable()

    def disable(self):
        self.hip_servo.disable()
        self.left_servo.disable()
        self.right_servo.disable()

    def set_servo_angles(self, servo_angles, side):
        if side == 'left':
            #self.hip_servo.value(servo_angles[0])
            self.left_servo.value((servo_angles[2] - self.servo_offset) * self.left_servo_direction)
            self.right_servo.value((servo_angles[1] - self.servo_offset) * self.right_servo_direction)
        else:
            #self.hip_servo.value(servo_angles[0])
            self.left_servo.value((servo_angles[2] - self.servo_offset) * -self.left_servo_direction)
            self.right_servo.value((servo_angles[1] - self.servo_offset) * -self.right_servo_direction)

    def get_servo_values(self):
        return {
            "hip": self.hip_servo.value(),
            "left": self.left_servo.value(),
            "right": self.right_servo.value()
        }

    def manual_servo_control(self, servo_angles):
        #self.hip_servo.value(servo_angles[0])
        self.left_servo.value(servo_angles[1])
        self.right_servo.value(servo_angles[2])

        servo_set_angles = self.get_servo_values()
        print("Manually setting servos to ", servo_set_angles["hip"], servo_set_angles["left"], servo_set_angles["right"])

    def deactivate_hip(self):
        self.hip_servo.disable()
