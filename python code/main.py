import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time
import orientation
import inverse_kinematics
import constants
from machine import UART, Pin

gc.collect()

uart1 = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))

koda = Robot()
koda.stand()

koda.set_speed(Speed.in_mm_per_second(20))

koda.set_gait(Gait.TROT, Direction.FORWARDS)
koda.go_for_steps(10)
time.sleep(1)

koda.set_gait(Gait.TROT, Direction.BACKWARDS)
koda.go_for_steps(10)
time.sleep(1)

koda.rotation_test(1)
koda.translation_test(1)

koda.sleep()