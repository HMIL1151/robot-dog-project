import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time

time.sleep(5)

gc.collect()

koda = Robot()

start_time = time.time()
while time.time() - start_time < 5:
   koda.set_carry_position()

koda.stand()

koda.set_speed(Speed.in_mm_per_second(20))
koda.set_direction(Direction.FORWARDS)
koda.set_gait(Gait.CRAWL)

koda.go_for_steps(20)
koda.disable()
