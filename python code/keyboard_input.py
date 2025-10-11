import struct
import constants
from pynput import keyboard
from pynput.keyboard import Key
from AxesButtons import Axes, Buttons

class keyboardInputDevice():
    def __init__(self):
        self.current_roll = 0.0
        self.current_pitch = 0.0
        self.current_axes = Axes()
        self.current_buttons = Buttons()
        self._pressed_keys = set()
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def _on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                self._pressed_keys.add(key.char.lower())
            elif hasattr(key, 'name') and key.name is not None:
                self._pressed_keys.add(key.name.lower())
        except Exception:
            pass

    def _on_release(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                self._pressed_keys.discard(key.char.lower())
            elif hasattr(key, 'name') and key.name is not None:
                self._pressed_keys.discard(key.name.lower())
        except Exception:
            pass

    def _is_pressed(self, key_name):
        return key_name.lower() in self._pressed_keys

    def read_packet(self):
        self.unpack_data()
        return True

    def unpack_data(self):
        # Left vertical axis (W/S)
        if self._is_pressed('w'):
            self.current_axes.left_vertical = Axes.normalize(self.current_axes.thumbstick_max)
        elif self._is_pressed('s'):
            self.current_axes.left_vertical = Axes.normalize(self.current_axes.thumbstick_min)
        else:
            self.current_axes.left_vertical = Axes.normalize(self.current_axes.thumbstick_zero)

        # Left horizontal axis (A/D)
        if self._is_pressed('a'):
            self.current_axes.left_horizontal = Axes.normalize(self.current_axes.thumbstick_min)
        elif self._is_pressed('d'):
            self.current_axes.left_horizontal = Axes.normalize(self.current_axes.thumbstick_max)
        else:
            self.current_axes.left_horizontal = Axes.normalize(self.current_axes.thumbstick_zero)

        # Right vertical axis (I/K)
        if self._is_pressed('i'):
            self.current_axes.right_vertical = Axes.normalize(self.current_axes.thumbstick_max)
        elif self._is_pressed('k'):
            self.current_axes.right_vertical = Axes.normalize(self.current_axes.thumbstick_min)
        else:
            self.current_axes.right_vertical = Axes.normalize(self.current_axes.thumbstick_zero)

        # Right horizontal axis (J/L)
        if self._is_pressed('j'):
            self.current_axes.right_horizontal = Axes.normalize(self.current_axes.thumbstick_min)
        elif self._is_pressed('l'):
            self.current_axes.right_horizontal = Axes.normalize(self.current_axes.thumbstick_max)
        else:
            self.current_axes.right_horizontal = Axes.normalize(self.current_axes.thumbstick_zero)

        # D-Pad Buttons (1,2,3,4)
        self.current_buttons.d_up = self._is_pressed('1')
        self.current_buttons.d_down = self._is_pressed('2')
        self.current_buttons.d_left = self._is_pressed('3')
        self.current_buttons.d_right = self._is_pressed('4')

        # Shape Buttons (7, 8, 9, 0)
        self.current_buttons.triangle = self._is_pressed('7')
        self.current_buttons.square = self._is_pressed('8')
        self.current_buttons.circle = self._is_pressed('9')
        self.current_buttons.cross = self._is_pressed('0')

        # Shoulder Buttons (insert, left, pageup, right)
        self.current_buttons.l2 = self._is_pressed('insert')
        self.current_buttons.l1 = self._is_pressed('left')
        self.current_buttons.r2 = self._is_pressed('page_up')
        self.current_buttons.r1 = self._is_pressed('right')

        # Misc Buttons (enter, backspace, home, end)
        self.current_buttons.options = self._is_pressed('enter')
        self.current_buttons.share = self._is_pressed('backspace')
        self.current_buttons.ps = self._is_pressed('space')
        self.current_buttons.touchpad = self._is_pressed('end')




    

