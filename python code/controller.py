import constants
import comms_input
import keyboard_input
from AxesButtons import Axes, Buttons

class Controller:
    def __init__(self):

        self.axes = Axes()
        self.buttons = Buttons()
        if constants.EMULATION_MODE:
            self.comms = keyboard_input.keyboardInputDevice()
        else:
            self.comms = comms_input.CommsInputDevice()

    def update(self):
        if self.comms.read_packet():
            self.buttons = self.comms.current_buttons
            self.axes = self.comms.current_axes
            # print("Axes:", self.axes.left_horizontal, self.axes.left_vertical,
            #       self.axes.right_horizontal, self.axes.right_vertical)
        else:
            print("No packet received")

    def get_roll_angle(self):
        return self.comms.current_roll

    def get_pitch_angle(self):
        return self.comms.current_pitch