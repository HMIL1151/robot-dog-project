import math
import numpy as np

def intersection_between_circles(circle1, circle2):
    # Unpack circle1 and circle2
    ((x1, y1), r1) = circle1
    ((x2, y2), r2) = circle2

    # Calculate the distance between the centers
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

    intersection_coords = []

    # Check if circles intersect
    if distance < r1 + r2 and distance > 0:
        # Calculate intersection points (simplified)

        a = (math.pow(r1, 2) - math.pow(r2, 2) + math.pow(distance, 2)) / (2 * distance)
        if (math.pow(r1, 2) - math.pow(a, 2)) < 0:
            return intersection_coords
        h = math.sqrt(math.pow(r1, 2) - math.pow(a, 2))
        x5 = x1 + a/distance * dx
        y5 = y1 + a/distance * dy

        x3 = x5 - h/distance * dy
        y3 = y5 + h/distance * dx
        intersection_coords.append((x3, y3))

        x4 = x5 + h/distance * dy
        y4 = y5 - h/distance * dx
        intersection_coords.append((x4, y4))

    return intersection_coords

def clockwise_angle_between_two_lines(point1, point2, intersection_point):

    x1, y1 = point1
    x2, y2 = point2
    xi, yi = intersection_point

    v1x, v1y = x1 - xi, y1 - yi
    v2x, v2y = x2 - xi, y2 - yi

    theta1 = math.atan2(v1y, v1x)
    theta2 = math.atan2(v2y, v2x)

    delta_cw = theta1 - theta2
    delta_cw = (delta_cw + 2 * math.pi) % (2 * math.pi)
    return math.degrees(delta_cw)

def counterclockwise_angle_between_two_lines(point1, point2, intersection_point):
    x1, y1 = point1
    x2, y2 = point2
    xi, yi = intersection_point

    v1x, v1y = x1 - xi, y1 - yi
    v2x, v2y = x2 - xi, y2 - yi

    theta1 = math.atan2(v1y, v1x)
    theta2 = math.atan2(v2y, v2x)

    delta_ccw = theta2 - theta1
    delta_ccw = (delta_ccw + 2 * math.pi) % (2 * math.pi)
    return math.degrees(delta_ccw)





a = 53.863
d = 85
theta_l = math.radians(100.27)
servo_distance = 46
thigh_length = 30
calf_length = 120

x = 0.0
y = 155.12
z = 57.31

q = d/2 - z




b = -2*a*math.cos(theta_l)
c = math.pow(a, 2) - math.pow(y, 2) - math.pow(q, 2)

roots = np.roots([1, b, c])

positive_roots = roots[roots > 0]
if positive_roots.size == 0:
    raise ValueError("No positive roots found")
y_prime = float(positive_roots[0])
print(f"y_prime: {y_prime:.2f}")

f = math.sqrt(math.pow(q, 2) + math.pow(y, 2))
theta_a = math.acos((math.pow(a, 2) + math.pow(f, 2) - math.pow(y_prime, 2)) / (2*a*f))
theta_q = math.acos((math.pow(q, 2) + math.pow(f, 2) - math.pow(y, 2)) / (2*q*f))
theta_c = 4*math.pi - math.pi/2 - theta_l - theta_a - theta_q
theta_h = math.degrees(2*math.pi - theta_c) - 90
print(f"theta_h: {theta_h:.2f}")

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


    