import gc
from lib.robot import Robot
from lib.gait import Gait
from lib.units import Speed, Direction

gc.collect()

koda = Robot()

while not koda.is_robot_zeroed():
    koda.zero_robot()
try:
    koda.set_speed(Speed.in_mm_per_second(50))
    koda.set_direction(Direction.FORWARDS)
    koda.set_gait(Gait.TRIANGULAR)

    koda.go()
except Exception as e:
    print(e)
