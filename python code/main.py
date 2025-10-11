import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import struct
import time
import orientation
import inverse_kinematics
import constants

gc.collect()

koda = Robot()

while not koda.turn_on:
    koda.check_on_button()
    time.sleep(0.1)

koda.stand()

while koda.turn_on:
    koda.update_robot()
    time.sleep(0.05)

koda.sleep()