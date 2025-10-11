import math
import constants
from units import Position

def ik_points(points):
    return [inverse_kinematics(point) for point in points]

def inverse_kinematics(position: Position):
    x = position.x
    y = position.y
    z = position.z
    theta_h = None
    servo1_angle = None
    servo2_angle = None

    a = constants.LEG_GEOMETRY_A_MM
    hip_seperation_mm = constants.HIP_SEPERATION_MM
    foot_legservo_hipservo_theta = math.radians(constants.LEG_GEOMETRY_THETA_DEG)
    servo_distance = constants.SERVO_DISTANCE_MM
    thigh_length = constants.THIGH_LENGTH_MM
    calf_length = constants.CALF_LENGTH_MM

    foot_to_hip_z_distance_mm = hip_seperation_mm/2 - z

    b = -2*a*math.cos(foot_legservo_hipservo_theta)
    c = math.pow(a, 2) - math.pow(y, 2) - math.pow(foot_to_hip_z_distance_mm, 2)

    # Solve quadratic equation x^2 + b*x + c = 0
    discriminant = b**2 - 4*1*c
    if discriminant < 0:
        raise ValueError("No real roots found")
    root1 = (-b + math.sqrt(discriminant)) / 2
    root2 = (-b - math.sqrt(discriminant)) / 2
    positive_roots = [r for r in (root1, root2) if r > 0]
    if not positive_roots:
        raise ValueError("No positive roots found")
    y_prime = float(positive_roots[0])

    v = math.sqrt(math.pow(y, 2) + math.pow(foot_to_hip_z_distance_mm, 2))
    if z < hip_seperation_mm/2:
        theta_a_prime = math.atan(y/foot_to_hip_z_distance_mm)
    elif z > hip_seperation_mm/2:
        theta_a_prime = math.atan((z-hip_seperation_mm/2)/y) + math.pi/2
    else:
        theta_a_prime = math.pi/2
    theta_a_prime_prime = math.acos((math.pow(a, 2) + math.pow(v, 2) - math.pow(y_prime, 2)) / (2*a*v))
    theta_a = theta_a_prime + theta_a_prime_prime

    f = math.sqrt(math.pow(foot_to_hip_z_distance_mm, 2) + math.pow(a, 2) - 2*a*foot_to_hip_z_distance_mm*math.cos(theta_a))

    if z > constants.ZERO_Z - 0.1 and z < constants.ZERO_Z + 0.1:
        theta_h = 0
    else:
        theta_h = math.acos((math.pow(y, 2) + math.pow(y_prime, 2) - math.pow(f, 2)) / (2*y*y_prime))

    if z > (hip_seperation_mm/2 + a*math.sin(math.pi - foot_legservo_hipservo_theta)):
        theta_h = -theta_h
    elif z < (hip_seperation_mm/2 + a*math.sin(math.pi - foot_legservo_hipservo_theta)):
        theta_h = theta_h
    else:
        theta_h = 0
        
    theta_h = math.degrees(theta_h)

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

    else:
        raise ValueError("No Intersection Points")

    servo_angles = (int(theta_h), int(servo1_angle), int(servo2_angle))

    return servo_angles


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
