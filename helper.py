import math


def inverse_kinematics(leg, x, y, z):
    # Implement inverse kinematics calculations here
    pass

def intersection_between_circles(circle1, circle2):
    # Unpack circle1 and circle2
    ((x1, y1), r1) = circle1
    ((x2, y2), r2) = circle2

    # Calculate the distance between the centers
    dx = x2 - x1
    dy = y2 - y1
    distance = math.hypot(dx, dy)

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
