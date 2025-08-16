import numpy as np
from . import inverse_kinematics
from .constants import ZERO_X, ZERO_Y, ZERO_Z

class Gait:
    TRIANGULAR = 1
    RECTANGULAR = 2
    BEZIER = 3

    TRIANGULAR_WIDTH = 60
    TRIANGULAR_HEIGHT = 10
    TRIANGLE_BASE_Y = 160

    STEPS_PER_SECOND = 20

    @staticmethod
    def calculate_gait(robot, gait_type, speed):
        if gait_type == Gait.TRIANGULAR:
            path =  Gait.interpolate_triangular_gait(robot, speed)
        elif gait_type == Gait.RECTANGULAR:
            path = Gait.interpolate_rectangular_gait()
        elif gait_type == Gait.BEZIER:
            path = Gait.interpolate_bezier_gait()
        else:
            raise ValueError("Invalid gait type")
        
        try:
            servo_positions = inverse_kinematics.ik_on_path(path)
            return servo_positions
        except Exception as e:
            raise ValueError(f"Error occurred during inverse kinematics: {e}") from e

    @staticmethod
    def interpolate_triangular_gait(robot, speed):
        triangle_vertices = [
            (Gait.TRIANGULAR_WIDTH / 2, Gait.TRIANGLE_BASE_Y, ZERO_Z),
            (-Gait.TRIANGULAR_WIDTH / 2, Gait.TRIANGLE_BASE_Y, ZERO_Z),
            (0, Gait.TRIANGLE_BASE_Y - Gait.TRIANGULAR_HEIGHT, ZERO_Z)
        ]

        num_steps = Gait.STEPS_PER_SECOND * Gait.TRIANGULAR_WIDTH / speed
        points1 = Gait.interpolate_between_points(triangle_vertices[0], triangle_vertices[1], num_steps)
        points2 = Gait.interpolate_between_points(triangle_vertices[1], triangle_vertices[2], num_steps/2)
        points3 = Gait.interpolate_between_points(triangle_vertices[2], triangle_vertices[0], num_steps/2)
        path = np.vstack((points1[:-1], points2[:-1], points3))
        return path

    @staticmethod
    def interpolate_rectangular_gait():
        return np.array([1, 1, 1])

    @staticmethod
    def interpolate_bezier_gait():
        return np.array([0, 0, 1])

    @staticmethod
    def interpolate_between_points(p1, p2, num_points=10):
        return np.array([np.linspace(p1[i], p2[i], int(num_points)) for i in range(3)]).T