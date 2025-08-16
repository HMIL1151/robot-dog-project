import json
import os

def load_settings():
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
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
    from servo import Servo, ServoCluster, servo2040, ANGULAR, LINEAR, CONTINUOUS, Calibration