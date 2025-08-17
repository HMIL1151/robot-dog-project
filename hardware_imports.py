import json
import os
from constants import EMULATION_MODE

if EMULATION_MODE:
    from mock_lib.servo import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
else:
    try:
        from servo import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
    except ImportError:
        raise ImportError("The real 'servo' module is only available on the Pico. Set 'use_mock_hardware' to True in settings.json to use the mock version on your PC.")