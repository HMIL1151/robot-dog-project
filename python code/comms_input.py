import asyncio
from hardware_imports import UART, Pin
import struct
import constants
from AxesButtons import Axes, Buttons

class CommsInputDevice():
    def __init__(self, uart_id=0, baudrate=406800, tx_pin=16, rx_pin=17):
        self.uart = UART(0, baudrate=406800, tx=Pin(16), rx=Pin(17))
        self.start_byte = 0xAA
        self.packet_length = 17
        self.current_roll = 0.0
        self.current_pitch = 0.0
        self.current_axes = Axes()
        self.current_buttons = Buttons()

    def read_packet(self):
        sync = False
        while not sync:
            b = self.uart.read(1)
            if not b:
                continue
            if b[0] == self.start_byte:
                sync = True

        data = self.uart.read(self.packet_length - 1)  # Already read 1 byte
        if not data or len(data) < self.packet_length - 1:
            return None

        packet = bytes([self.start_byte]) + data
        # Checksum verification
        checksum = 0
        for i in range(1, 16):
            checksum ^= packet[i]
        if checksum != packet[16]:
            print("Checksum failed.")
            return None
        
        self.unpack_data(packet)
        return True

    def unpack_data(self, packet):
        # Unpack data
        roll = struct.unpack_from('<h', packet, 1)[0] / 100.0
        pitch = struct.unpack_from('<h', packet, 3)[0] / 100.0
        axes = []
        for i in range(4):
            axes.append(struct.unpack_from('<h', packet, 5 + i*2)[0])
        # Buttons
        button_bits = packet[13] | (packet[14] << 8) | (packet[15] << 16)
        buttons = [(button_bits >> i) & 1 for i in range(constants.CONTROLLER_BUTTON_COUNT)]

        self.current_axes.left_horizontal = axes[0]
        self.current_axes.left_vertical = axes[1]
        self.current_axes.right_horizontal = axes[2]
        self.current_axes.right_vertical = axes[3]
        self.current_buttons.square = bool(buttons[0])
        self.current_buttons.cross = bool(buttons[1])
        self.current_buttons.circle = bool(buttons[2])
        self.current_buttons.triangle = bool(buttons[3])
        self.current_buttons.d_up = bool(buttons[4])
        self.current_buttons.d_down = bool(buttons[5])
        self.current_buttons.d_left = bool(buttons[6])
        self.current_buttons.d_right = bool(buttons[7])
        self.current_buttons.l1 = bool(buttons[8])
        self.current_buttons.r1 = bool(buttons[9])
        self.current_buttons.l2 = bool(buttons[10])
        self.current_buttons.r2 = bool(buttons[11])
        self.current_buttons.l3 = bool(buttons[12])
        self.current_buttons.r3 = bool(buttons[13])
        self.current_buttons.share = bool(buttons[14])
        self.current_buttons.options = bool(buttons[15])
        self.current_buttons.ps = bool(buttons[16])
        self.current_buttons.touchpad = bool(buttons[17])

        self.current_roll = roll
        self.current_pitch = pitch
        



    

