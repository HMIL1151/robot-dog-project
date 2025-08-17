import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction

gc.collect()

koda = Robot()
koda.deactivate_all_hips()

try:
    koda.set_speed(Speed.in_mm_per_second(200))
    koda.set_direction(Direction.FORWARDS)
    koda.set_gait(Gait.TRIANGULAR)

    koda.go_for_steps(20)
    koda.disable()
except Exception as e:
    print(e)
