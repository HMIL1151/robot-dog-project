import gc
from robot import Robot
import time

gc.collect()

koda = Robot()

while not koda.turn_on:
    koda.controller.update()
    koda.check_on_button()
    time.sleep(0.1)

koda.stand()

while koda.turn_on:
    koda.update_robot()
    time.sleep(0.05)

koda.sleep()