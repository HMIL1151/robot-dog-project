import numpy as np
from robot import Robot
import helper

class Gait:
    TRIANGULAR = 1
    RECTANGULAR = 2
    BEZIER = 3

    TRIANGULAR_WIDTH = 70
    TRIANGULAR_HEIGHT = 40
    TRIANGLE_BASE_Y = 145

    @staticmethod
    def calculate_gait(robot, gait_type):
        if gait_type == Gait.TRIANGULAR:
            path =  Gait.interpolate_triangular_gait(robot)
        elif gait_type == Gait.RECTANGULAR:
            path = Gait.interpolate_rectangular_gait()
        elif gait_type == Gait.BEZIER:
            path = Gait.interpolate_bezier_gait()
        else:
            raise ValueError("Invalid gait type")
        
        servo_positions = helper.ik_on_path(path)
        return servo_positions

    @staticmethod
    def interpolate_triangular_gait(robot):
        triangle_vertices = [
            (Gait.TRIANGULAR_WIDTH / 2, Gait.TRIANGLE_BASE_Y, robot.ZERO_Z),
            (-Gait.TRIANGULAR_WIDTH / 2, Gait.TRIANGLE_BASE_Y, robot.ZERO_Z),
            (0, Gait.TRIANGLE_BASE_Y - Gait.TRIANGULAR_HEIGHT, robot.ZERO_Z)
        ]
        points1 = Gait.interpolate_between_points(triangle_vertices[0], triangle_vertices[1], 20)
        points2 = Gait.interpolate_between_points(triangle_vertices[1], triangle_vertices[2], 10)
        points3 = Gait.interpolate_between_points(triangle_vertices[2], triangle_vertices[0], 10)
        # Concatenate, but avoid duplicating the connecting points
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
        return np.array([np.linspace(p1[i], p2[i], num_points) for i in range(3)]).T