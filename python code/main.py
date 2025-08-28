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

# koda.rotation_test(2)
# koda.rotation_test(2)

koda.set_speed(Speed.in_mm_per_second(10))

#GOOD
# koda.set_gait(Gait.TROT, Direction.FORWARDS)
# koda.go_for_steps(10)
# time.sleep(1)

#Z Moves are all in the same direction!
koda.set_gait(Gait.TROT, Direction.BACKWARDS)
koda.go_for_steps(10)
time.sleep(1)

#Good but slow
# koda.set_gait(Gait.TROT, Direction.LEFT)
# koda.go_for_steps(100)
# time.sleep(1)

koda.set_gait(Gait.TROT, Direction.RIGHT)
koda.go_for_steps(10)
time.sleep(1)

koda.set_gait(Gait.TROT, Direction.CLOCKWISE)
koda.go_for_steps(10)
time.sleep(1)

koda.set_gait(Gait.TROT, Direction.COUNTERCLOCKWISE)
koda.go_for_steps(10)
time.sleep(1)

koda.sleep()