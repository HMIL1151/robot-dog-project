import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time

gc.collect()

koda = Robot()

koda.stand()

koda.set_speed(Speed.in_mm_per_second(20))
koda.set_direction(Direction.FORWARDS)
koda.set_gait(Gait.CRAWL)

koda.go_for_steps(5)

koda.sit()
koda.disable()
