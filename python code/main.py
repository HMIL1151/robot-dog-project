import gc
from robot import Robot
from gait import Gait
from units import Speed, Direction
import time
import orientation
import inverse_kinematics
import constants

x_min = -30
x_max = -x_min
y_min = -20
y_max = -y_min
z_min = -40
z_max = -z_min

# --- Servo2040 Potentiometer Input Reading ---
from machine import Pin
from pimoroni import Analog, AnalogMux, Button
from servo import servo2040

user_sw = Button(servo2040.USER_SW)

def read_potentiometers():
    """
    Reads analog voltages from potentiometers connected to inputs 1, 2, and 3 on the Servo2040 board.
    Returns a tuple of voltages (pot1, pot2, pot3).
    """
    # Set up the shared analog input
    sen_adc = Analog(servo2040.SHARED_ADC)
    # Set up the analog multiplexer
    mux = AnalogMux(servo2040.ADC_ADDR_0, servo2040.ADC_ADDR_1, servo2040.ADC_ADDR_2,
                    muxed_pin=Pin(servo2040.SHARED_ADC))
    # Sensor addresses for inputs 1, 2, 3
    sensor_addrs = [servo2040.SENSOR_1_ADDR, servo2040.SENSOR_2_ADDR, servo2040.SENSOR_3_ADDR]
    # Read voltages
    voltages = []
    for addr in sensor_addrs:
        mux.select(addr)
        voltages.append(sen_adc.read_voltage())

    
    return tuple(voltages)



def conver_position_inputs(inputs):
    pot1, pot2, pot3 = read_potentiometers()
    pot_max_voltage = 3.3  # Maximum voltage for the potentiometers
    pot_min_voltage = 0.0  # Minimum voltage for the potentiometers
    x = constants.ZERO_X + x_min + (pot1 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * (x_max - x_min)
    y = constants.ZERO_Y + y_min + (pot2 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * (y_max - y_min)
    z = constants.ZERO_Z + z_min + (pot3 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * (z_max - z_min)
    return x, y, z

def convert_angular_inputs(inputs):
    pot1, pot2, pot3 = read_potentiometers()
    pot_max_voltage = 3.3  # Maximum voltage for the potentiometers
    pot_min_voltage = 0.0  # Minimum voltage for the potentiometers
    roll = (pot1 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * 180 - 90
    pitch = (pot2 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * 180 - 90
    yaw = (pot3 - pot_min_voltage) / (pot_max_voltage - pot_min_voltage) * 180 - 90
    return roll, pitch, yaw

gc.collect()

koda = Robot()


def pot_ik():
    inputs = conver_position_inputs(read_potentiometers())
    #print("Converted Inputs (x, y, z):", inputs)
    position = (inputs, inputs, inputs, inputs)
    try:
        koda.manual_position_control(position)
    except Exception as e:
        print("Error in manual_position_control:", e)

def pot_fk():
    orientation = convert_angular_inputs(read_potentiometers())
    #print("Converted Inputs (roll, pitch, yaw):", inputs)
    try:
        koda.manual_servo_control(orientation)
    except Exception as e:
        print("Error in manual_orientation_control:", e)


# --- Toggle IK/FK mode on button press ---
ik_mode = True  # Start in IK mode by default
last_button_state = user_sw.raw()

while True:
    current_button_state = user_sw.raw()
    if current_button_state and not last_button_state:
        ik_mode = not ik_mode  # Toggle mode on button press
        if ik_mode:
            print("Switched to IK Mode")
        else:
            print("Switched to FK Mode")
    last_button_state = current_button_state

    if ik_mode:
        pot_ik()
    else:
        pot_fk()
    time.sleep(0.05)  # Debounce delay

koda.stand()

koda.set_speed(Speed.in_mm_per_second(20))

for x in range (5):

    koda.set_gait(Gait.TROT, Direction.FORWARDS)
    koda.go_for_steps(10)
    time.sleep(1)

    koda.set_gait(Gait.TROT, Direction.BACKWARDS)
    koda.go_for_steps(10)
    time.sleep(1)

# koda.rotation_test(1)
# koda.translation_test(1)

koda.sleep()