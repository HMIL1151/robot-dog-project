import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction

gc.collect()

koda = Robot()
koda.deactivate_all_hips()

#try:
koda.set_speed(Speed.in_mm_per_second(10))
koda.set_direction(Direction.FORWARDS)
koda.set_gait(Gait.CRAWL)


koda.go_for_steps(5)
koda.disable()
#except Exception as e:
   #print(e)
