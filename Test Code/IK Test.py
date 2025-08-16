import math
import numpy as np



a = 53.695
d = 85
theta_l = math.radians(102.31)
servo_distance = 46
thigh_length = 40
calf_length = 150

x = 45
y = 150
z = 100

q = d/2 - z




b = -2*a*math.cos(theta_l)
c = math.pow(a, 2) - math.pow(y, 2) - math.pow(q, 2)

roots = np.roots([1, b, c])

positive_roots = roots[roots > 0]
if positive_roots.size == 0:
    raise ValueError("No positive roots found")
y_prime = float(positive_roots[0])
print(f"y_prime: {y_prime:.2f}")

v = math.sqrt(math.pow(y, 2) + math.pow(q, 2))
if z < d/2:
    theta_a_prime = math.atan(y/q)
elif z > d/2:
    theta_a_prime = math.atan((z-d/2)/y) + math.pi/2
else:
    theta_a_prime = math.pi/2
theta_a_prime_prime = math.acos((math.pow(a, 2) + math.pow(v, 2) - math.pow(y_prime, 2)) / (2*a*v))
theta_a = theta_a_prime + theta_a_prime_prime

f = math.sqrt(math.pow(q, 2) + math.pow(a, 2) - 2*a*q*math.cos(theta_a))
theta_h = math.acos((math.pow(y, 2) + math.pow(y_prime, 2) - math.pow(f, 2)) / (2*y*y_prime))

if z > (d/2 + a*math.sin(math.pi - theta_l)):
    theta_h = -theta_h
elif z < (d/2 + a*math.sin(math.pi - theta_l)):
    theta_h = theta_h
else:
    theta_h = 0
    
print(f"theta_h: {math.degrees(theta_h):.2f}")

foot_coords = (x, y_prime)
servo1_coords = (-servo_distance/2, 0)
servo2_coords = (servo_distance/2, 0)

foot_circle = (foot_coords, calf_length)
thigh_circle_1 = (servo1_coords, thigh_length)
thigh_circle_2 = (servo2_coords, thigh_length)

servo1_intersection_coords = intersection_between_circles(foot_circle, thigh_circle_1)
servo2_intersection_coords = intersection_between_circles(foot_circle, thigh_circle_2)

if servo1_intersection_coords and servo2_intersection_coords:

    servo1_intersection_angles = (
        clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[0]),
        clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[1])
    )
    servo2_intersection_angles = (
        clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[0]),
        clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[1])
    )

    if servo1_intersection_angles[0] < 180:
        servo1_intersection_point = servo1_intersection_coords[1]
    else:
        servo1_intersection_point = servo1_intersection_coords[0]

    if servo2_intersection_angles[0] < 180:
        servo2_intersection_point = servo2_intersection_coords[0]
    else:
        servo2_intersection_point = servo2_intersection_coords[1]

    servo1_angle = counterclockwise_angle_between_two_lines(servo2_coords, servo1_intersection_point, servo1_coords)
    servo2_angle = clockwise_angle_between_two_lines(servo1_coords, servo2_intersection_point, servo2_coords)

    print("Servo 1 Angle:", servo1_angle, "Servo 2 Angle:", servo2_angle)