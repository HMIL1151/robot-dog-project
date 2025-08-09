import time
import math
from servo import Servo, servo2040

"""
Demonstrates how to create a Servo object and control it.
"""

# Create a servo on pin 0
s = Servo(servo2040.SERVO_1)

# Enable the servo (this puts it at the middle)
s.enable()
time.sleep(2)

value = -90

while True:
    s.value(value)
    value += 40
    if value > 180:
        value = -90
    time.sleep(1)