import asyncio
from hardware_imports import UART, Pin
import struct
import constants

class CommsInputDevice():
    def __init__(self, uart_id=0, baudrate=406800, tx_pin=16, rx_pin=17):
        self.uart = UART(0, baudrate=406800, tx=Pin(16), rx=Pin(17))
        self.start_byte = 0xAA
        self.packet_length = 17
        self.button_count = 22
        self.current_roll = 0.0
        self.current_pitch = 0.0
        self.current_axes = [0, 0, 0, 0]
        self.current_buttons = [0] * self.button_count  # 22 buttons

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

        self.current_roll = roll
        self.current_pitch = pitch
        self.current_axes = axes
        self.current_buttons = buttons



    

