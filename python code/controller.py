import constants
import comms_input

class Axes:
    def __init__(self):
        self.left_horizontal = 0
        self.left_vertical = 0
        self.right_horizontal = 0
        self.right_vertical = 0

        self.thumbstick_min = -512
        self.thumbstick_max = 512

    def normalize(self, value):
        return (value - self.thumbstick_min) / (self.thumbstick_max - self.thumbstick_min) * 2 - 1

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


class Controller:
    def __init__(self):

        self.axes = Axes()
        self.buttons = Buttons()
        self.comms = comms_input.CommsInputDevice()
        

    def update(self):
        if self.comms.read_packet():
            self.axes.left_horizontal = self.comms.current_axes[0]
            self.axes.left_vertical = self.comms.current_axes[1]
            self.axes.right_horizontal = self.comms.current_axes[2]
            self.axes.right_vertical = self.comms.current_axes[3]
            self.buttons.square = bool(self.comms.current_buttons[0])
            self.buttons.cross = bool(self.comms.current_buttons[1])
            self.buttons.circle = bool(self.comms.current_buttons[2])
            self.buttons.triangle = bool(self.comms.current_buttons[3])
            self.buttons.d_up = bool(self.comms.current_buttons[4])
            self.buttons.d_down = bool(self.comms.current_buttons[5])
            self.buttons.d_left = bool(self.comms.current_buttons[6])
            self.buttons.d_right = bool(self.comms.current_buttons[7])
            self.buttons.l1 = bool(self.comms.current_buttons[8])
            self.buttons.r1 = bool(self.comms.current_buttons[9])
            self.buttons.l2 = bool(self.comms.current_buttons[10])
            self.buttons.r2 = bool(self.comms.current_buttons[11])
            self.buttons.l3 = bool(self.comms.current_buttons[12])
            self.buttons.r3 = bool(self.comms.current_buttons[13])
            self.buttons.share = bool(self.comms.current_buttons[14])
            self.buttons.options = bool(self.comms.current_buttons[15])
            self.buttons.ps = bool(self.comms.current_buttons[16])
            self.buttons.touchpad = bool(self.comms.current_buttons[17])
        else:
            print("No packet received")

    def get_roll_angle(self):
        return self.comms.current_roll

    def get_pitch_angle(self):
        return self.comms.current_pitch