import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time
import orientation

gc.collect()

koda = Robot()

koda.stand()

pitch_angle_deg = 0
direction = 1
while True:
   if pitch_angle_deg >= 5:
      direction = -1
   elif pitch_angle_deg <= -5:
      direction = 1

   koda.set_torso_orientation(yaw=0, pitch=pitch_angle_deg, roll=0)
   pitch_angle_deg += 0.5 * direction
   time.sleep(0.05)




# koda.set_speed(Speed.in_mm_per_second(20))
# koda.set_direction(Direction.FORWARDS)
# koda.set_gait(Gait.CRAWL)

# koda.go_for_steps(5)

# koda.sit()
# koda.disable()
