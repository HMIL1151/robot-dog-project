class Axes:
    thumbstick_min = -512
    thumbstick_max = 512
    thumbstick_zero = 0
    
    def __init__(self):
        self.left_horizontal = 0
        self.left_vertical = 0
        self.right_horizontal = 0
        self.right_vertical = 0

    @classmethod
    def normalize(cls, value):
        # Normalize to range -1 to 1
        return (value - cls.thumbstick_min) / (cls.thumbstick_max - cls.thumbstick_min) * 2 - 1

class Buttons:
    def __init__(self):
        self.square = False
        self.cross = False
        self.circle = False
        self.triangle = False

        self.d_up = False
        self.d_down = False
        self.d_left = False
        self.d_right = False

        self.l1 = False
        self.r1 = False
        self.l2 = False
        self.r2 = False
        self.l3 = False
        self.r3 = False

        self.share = False
        self.options = False
        self.ps = False
        self.touchpad = False