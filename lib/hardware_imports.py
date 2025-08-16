import json
import os


def load_settings():
    settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
    try:
        with open(settings_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

settings = load_settings()
USE_MOCK_HARDWARE = settings.get("use_mock_hardware", False)

if USE_MOCK_HARDWARE:
    from mock_lib.servo import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
else:
    try:
        from servo import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration
    except ImportError:
        raise ImportError("The real 'servo' module is only available on the Pico. Set 'use_mock_hardware' to True in settings.json to use the mock version on your PC.")