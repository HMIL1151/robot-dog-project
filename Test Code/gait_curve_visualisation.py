import sys
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bezier_curve
from gait import Gait
from constants import ZERO_X, ZERO_Y, ZERO_Z
import inverse_kinematics


# Parameters for the test

STEP_DISTANCE = 50
STEP_HEIGHT = 20
STEP_CURVE_DELTA = 0.2
STEPS_PER_SECOND = 20
speed = 20
stance_steps = int(STEPS_PER_SECOND * (STEP_DISTANCE / speed))
swing_steps = int(stance_steps / 3)



# Get bezier curve points as a list of (x, y, z)
path_points = bezier_curve.calculate_curve(STEP_DISTANCE, STEP_HEIGHT, STEP_CURVE_DELTA, stance_steps, swing_steps)

servo_angles = inverse_kinematics.ik_points(path_points)

# Convert points to lists so they are mutable
path_points = [list(pt) for pt in path_points]
for pt in path_points:
	pt[1] = ZERO_Y + (ZERO_Y - pt[1])
	
#reverse path_points
path_points.reverse()

# Extract x and y (robotics: x horizontal, y vertical, +y is down)
x_vals = [pt[0] for pt in path_points]
y_vals = [pt[1] for pt in path_points]


fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x_vals, y_vals, label='Bezier Foot Path', color='k')
ax.scatter(x_vals, y_vals, color='k', s=10)

# Calculate start indices as in Gait.get_start_indices
gait_type = Gait.CRAWL
gait = Gait(gait_type)
gait.stance_steps = stance_steps
gait.swing_steps = swing_steps
start_indices = gait.get_start_indices()
print(start_indices)

leg_labels = ['Front Left', 'Front Right', 'Rear Right', 'Rear Left']
leg_colors = ['r', 'g', 'b', 'm']

# Animate the four leg points moving through the path
points = [ax.scatter([], [], color=color, s=80, label=f'{label} Foot') for color, label in zip(leg_colors, leg_labels)]

ax.set_title('Bezier Curve Foot Trajectory with Animated Feet')
ax.set_xlabel('X Position (horizontal)')
ax.set_ylabel('Y Position (vertical, +ve down)')
ax.grid(True)
ax.axis('equal')
ax.legend()

num_steps = len(path_points)

def init():
	for point in points:
		point.set_offsets(np.empty((0, 2)))
	return points

def animate(frame):
	for i, point in enumerate(points):
		idx = (start_indices[i] + frame) % num_steps
		x, y, _ = path_points[idx]
		point.set_offsets([[x, y]])
	return points

ani = animation.FuncAnimation(fig, animate, frames=num_steps, init_func=init, blit=True, interval=50, repeat=True)
plt.show()
