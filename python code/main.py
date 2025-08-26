import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time
import orientation
import inverse_kinematics

gc.collect()

koda = Robot()
koda.stand()

left_front = (0.0, 135.0, 57.43)
right_front = (0.0, 135.0, 127.06)
right_rear = (0.0, 135.0, 127.06)
left_rear = (0.0, 135.0, 57.43)

time_start = time.time()
while time.time() - time_start < 60:

    koda.manual_position_control((left_front, right_front, right_rear, left_rear))
# time_start = time.time()
# while time.time() - time_start < 30:
#     koda.set_translation_orientation((0, 0, 0), (0, 0, 7.5))



koda.sleep()

# koda.set_speed(Speed.in_mm_per_second(20))
# koda.set_direction(Direction.FORWARDS)
# koda.set_gait(Gait.CRAWL)

# koda.go_for_steps(5)

# koda.sit()
# koda.disable()
