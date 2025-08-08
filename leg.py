from servo import Servo
import helper

class Leg:
    def __init__ (self, hipServoNum, tibiaServoNum, femurServoNum):
        self.femur.length_mm = 100
        self.tibia.length_mm = 100
        self.hip = Servo(hipServoNum)
        self.tibia = Servo(tibiaServoNum)
        self.femur = Servo(femurServoNum)

    def zero_position(self):
        self.hip.angle = 90
        self.tibia.angle = 125
        self.femur.angle = 55

    def enable(self):
        self.hip.enable()
        self.tibia.enable()
        self.femur.enable()

    def disable(self):
        self.hip.disable()
        self.tibia.disable()
        self.femur.disable()

    def stow(self):
        self.hip.angle = 90
        self.tibia.angle = 0
        self.femur.angle = 180
    
    def set_foot_position(self, x, y, z):
        servo_angles = helper.inverse_kinematics(self, x, y, z)
        self.hip.angle = servo_angles.hip
        self.tibia.angle = servo_angles.tibia
        self.femur.angle = servo_angles.femur

    