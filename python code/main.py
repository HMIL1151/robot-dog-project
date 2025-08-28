import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time
import orientation
import inverse_kinematics
import constants

gc.collect()

koda = Robot()
koda.stand()

koda.rotation_test(2)
koda.rotation_test(2)

koda.set_speed(Speed.in_mm_per_second(20))
koda.set_direction(Direction.FORWARDS)
koda.set_gait(Gait.CRAWL)

koda.go_for_steps(10)

koda.sleep()