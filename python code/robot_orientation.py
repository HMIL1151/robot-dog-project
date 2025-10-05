class RobotOrientation:
    def __init__(self):
        self.roll = 0.0
        self.pitch = 0.0

    def update(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch

    def get_orientation(self):
        return {
            "roll": self.roll,
            "pitch": self.pitch
        }
