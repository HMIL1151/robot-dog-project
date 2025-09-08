import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import struct
import time
import orientation
import inverse_kinematics
import constants
from machine import UART, Pin

gc.collect()

# while True:

uart = UART(0, baudrate=406800, tx=Pin(16), rx=Pin(17))

START_BYTE = 0xAA
PACKET_LEN = 17

def read_packet():
    sync = False
    while not sync:
        b = uart.read(1)
        if not b:
            continue
        if b[0] == START_BYTE:
            sync = True

    data = uart.read(PACKET_LEN - 1)  # Already read 1 byte
    if not data or len(data) < PACKET_LEN - 1:
        return None

    packet = bytes([START_BYTE]) + data
    # Checksum verification
    checksum = 0
    for i in range(1, 16):
        checksum ^= packet[i]
    if checksum != packet[16]:
        print("Checksum failed.")
        return None

    # Unpack data
    roll = struct.unpack_from('<h', packet, 1)[0] / 100.0
    pitch = struct.unpack_from('<h', packet, 3)[0] / 100.0
    axes = []
    for i in range(4):
        axes.append(struct.unpack_from('<h', packet, 5 + i*2)[0])
    # Buttons
    button_bits = packet[13] | (packet[14] << 8) | (packet[15] << 16)
    buttons = [(button_bits >> i) & 1 for i in range(22)]

    return {
        "roll": roll,
        "pitch": pitch,
        "axes": axes,     # [LX, LY, RX, RY]
        "buttons": buttons  # List of 22 button states
    }

# Example usage loop
while True:
    pkt = read_packet()
    if pkt:
        print("Roll:", pkt["roll"], "Pitch:", pkt["pitch"], "Axes:", pkt["axes"], "Buttons:", pkt["buttons"])
    time.sleep(0.01)

# koda = Robot()
# koda.stand()

# koda.set_speed(Speed.in_mm_per_second(20))

# koda.set_gait(Gait.TROT, Direction.FORWARDS)
# koda.go_for_steps(10)
# time.sleep(1)

# koda.set_gait(Gait.TROT, Direction.BACKWARDS)
# koda.go_for_steps(10)
# time.sleep(1)

# koda.rotation_test(1)
# koda.translation_test(1)

# koda.sleep()