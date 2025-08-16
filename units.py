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
    BACKWARDS = 180
    LEFT = 90
    RIGHT = 270

    @staticmethod
    def angle(degrees):
        return degrees