class Speed:
    @staticmethod
    def in_mm_per_second(value):
        return value

    @staticmethod
    def in_cm_per_second(value):
        return value / 10

    @staticmethod
    def in_m_per_second(value):
        return value / 1000

class Direction:
    FORWARDS = 0
    BACKWARDS = 1
    LEFT = 2
    RIGHT = 3
    CLOCKWISE = 4
    COUNTERCLOCKWISE = 5

    @staticmethod
    def angle(degrees):
        return degrees
    
class Position:
    def __init__(self, x_mm, y_mm, z_mm):
        self.x = x_mm
        self.y = y_mm
        self.z = z_mm