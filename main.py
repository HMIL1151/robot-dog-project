import time
import gc
import math
from robot import Robot
from gait import Gait
import helper
from units import Speed, Direction

gc.collect()

koda = Robot()

while not koda.is_robot_zeroed():
    koda.zero_robot()

koda.set_speed(Speed.in_mm_per_second(100))
koda.set_direction(Direction.FORWARDS)
koda.set_gait(Gait.TRIANGULAR)

koda.go()

