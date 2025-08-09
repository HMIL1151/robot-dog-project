from servo import Servo
import helper

class Leg:
    def __init__ (self, hipServoNum, tibiaServoNum, femurServoNum):
        self.femur_length_mm = 40
        self.tibia_length_mm = 150
        self.servo_seperation_mm = 46
        self.hip_servo = Servo(hipServoNum)
        self.left_servo = Servo(tibiaServoNum)
        self.right_servo = Servo(femurServoNum)

    def zero_position(self):
        self.hip_servo.value(0)
        self.left_servo.value(70)
        self.right_servo.value(-70)

    def test_all(self):
        self.hip_servo.value(0)
        self.left_servo.value(0)
        self.right_servo.value(0)


    def enable(self):
        self.hip_servo.enable()
        self.left_servo.enable()
        self.right_servo.enable()

    def disable(self):
        self.hip_servo.disable()
        self.left_servo.disable()
        self.right_servo.disable()

    def set_foot_position(self, x, y, z):
        (servo_angles_hip, servo_angles_left, servo_angles_right) = helper.inverse_kinematics(self, x, y, z)
        self.hip_servo.value(servo_angles_hip)
        self.left_servo.value(servo_angles_left)
        self.right_servo.value(servo_angles_right)

    def get_servo_values(self):
        return {
            "hip": self.hip_servo.value(),
            "left": self.left_servo.value(),
            "right": self.right_servo.value()
        }

