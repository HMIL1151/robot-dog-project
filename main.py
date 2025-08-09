import time
import gc
import math
from robot import Robot

gc.collect()

koda = Robot()

while True:
    koda.test_all()