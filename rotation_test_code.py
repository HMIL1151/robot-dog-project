import math

import matplotlib
from matplotlib.widgets import Slider

# --- Pure Python matrix/vector helpers ---
def matmul3(a, b):
    return [
        [sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]

def matvecmul3(m, v):
    return [sum(m[i][j]*v[j] for j in range(3)) for i in range(3)]

def transpose3(m):
    return [[m[j][i] for j in range(3)] for i in range(3)]

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]

def vec_add(a, b):
    return [a[i] + b[i] for i in range(3)]

import numpy as np

leg_x_seperation_mm = 221.0
foot_y_seperation_mm = 95.5*2
torso_zero_height_mm = 135.0

left_front_foot_coords_WORLD = (leg_x_seperation_mm / 2, foot_y_seperation_mm/2, 0)
right_front_foot_coords_WORLD = (leg_x_seperation_mm / 2, -foot_y_seperation_mm/2, 0)
left_back_foot_coords_WORLD = (-leg_x_seperation_mm / 2, foot_y_seperation_mm/2, 0)
right_back_foot_coords_WORLD = (-leg_x_seperation_mm / 2, -foot_y_seperation_mm/2, 0)

torso_origin_coords_WORLD = (0, 0, torso_zero_height_mm)

torso_width_y_mm = 85.0
torso_height_z_mm = 48.0
torso_length_x_mm = 367.4

yaw_angle_deg = 0.0
pitch_angle_deg = 0.0
roll_angle_deg = 0.0


yaw_rotation_matrix = np.array([
    [np.cos(np.radians(yaw_angle_deg)), -np.sin(np.radians(yaw_angle_deg)), 0],
    [np.sin(np.radians(yaw_angle_deg)), np.cos(np.radians(yaw_angle_deg)), 0],
    [0, 0, 1]
])

pitch_rotation_matrix = np.array([
    [np.cos(np.radians(pitch_angle_deg)), 0, np.sin(np.radians(pitch_angle_deg))],
    [0, 1, 0],
    [-np.sin(np.radians(pitch_angle_deg)), 0, np.cos(np.radians(pitch_angle_deg))]
])

roll_rotation_matrix = np.array([
    [1, 0, 0],
    [0, np.cos(np.radians(roll_angle_deg)), -np.sin(np.radians(roll_angle_deg))],
    [0, np.sin(np.radians(roll_angle_deg)), np.cos(np.radians(roll_angle_deg))]
])

rotation_matrix = yaw_rotation_matrix @ pitch_rotation_matrix @ roll_rotation_matrix

left_front_foot_coords_TORSO = rotation_matrix.T @ (np.array(left_front_foot_coords_WORLD) - np.array(torso_origin_coords_WORLD))
right_front_foot_coords_TORSO = rotation_matrix.T @ (np.array(right_front_foot_coords_WORLD) - np.array(torso_origin_coords_WORLD))
left_back_foot_coords_TORSO = rotation_matrix.T @ (np.array(left_back_foot_coords_WORLD) - np.array(torso_origin_coords_WORLD))
right_back_foot_coords_TORSO = rotation_matrix.T @ (np.array(right_back_foot_coords_WORLD) - np.array(torso_origin_coords_WORLD))

# --- 3D Plotting of Robot Feet and Torso ---

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- Helper for cuboid vertices ---
def get_cuboid_vertices(center, dims, rot):
    l, w, h = dims
    dx = l/2
    dy = w/2
    dz = h/2
    corners = [
        [ dx,  dy,  dz],
        [ dx, -dy,  dz],
        [-dx, -dy,  dz],
        [-dx,  dy,  dz],
        [ dx,  dy, -dz],
        [ dx, -dy, -dz],
        [-dx, -dy, -dz],
        [-dx,  dy, -dz],
    ]
    rotated = [vec_add(matvecmul3(rot, c), center) for c in corners]
    return rotated

foot_points = np.array([
    left_front_foot_coords_WORLD,
    right_front_foot_coords_WORLD,
    left_back_foot_coords_WORLD,
    right_back_foot_coords_WORLD
])
torso_point = np.array(torso_origin_coords_WORLD)
torso_dims = (torso_length_x_mm, torso_width_y_mm, torso_height_z_mm)
edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]

# --- Interactive plot with sliders ---
from matplotlib.widgets import Slider

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0.1, bottom=0.25)

# Initial plot
sc_feet = ax.scatter(foot_points[:,0], foot_points[:,1], foot_points[:,2], c='b', label='Feet')
sc_torso = ax.scatter([torso_point[0]], [torso_point[1]], [torso_point[2]], c='r', label='Torso', s=60)

lines = []
# Initial green dots for feet in torso frame
foot_points_torso = np.array([
    left_front_foot_coords_TORSO,
    right_front_foot_coords_TORSO,
    left_back_foot_coords_TORSO,
    right_back_foot_coords_TORSO
])
sc_feet_torso = ax.scatter(foot_points_torso[:,0], foot_points_torso[:,1], foot_points_torso[:,2], c='g', label='Feet (Torso Frame)', marker='o')

def world_foot_coords_to_leg_foot_coords(coords, side, face):
    x_world, y_world, z_world = coords

    if face == 'front':
        x_leg = (leg_x_seperation_mm / 2) - x_world
    else:
        x_leg = -(leg_x_seperation_mm / 2) - x_world
    y_leg = torso_height_z_mm - z_world + 87.0
    z_leg = abs(y_world)

    return (x_leg, y_leg, z_leg)

def get_rotation_matrix(yaw, pitch, roll):
    yaw_matrix = np.array([
        [np.cos(np.radians(yaw)), -np.sin(np.radians(yaw)), 0],
        [np.sin(np.radians(yaw)), np.cos(np.radians(yaw)), 0],
        [0, 0, 1]
    ])
    pitch_matrix = np.array([
        [np.cos(np.radians(pitch)), 0, np.sin(np.radians(pitch))],
        [0, 1, 0],
        [-np.sin(np.radians(pitch)), 0, np.cos(np.radians(pitch))]
    ])
    roll_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(np.radians(roll)), -np.sin(np.radians(roll))],
        [0, np.sin(np.radians(roll)), np.cos(np.radians(roll))]
    ])
    return yaw_matrix @ pitch_matrix @ roll_matrix

def draw_cuboid(ax, vertices, edges, lines):
    # Remove old lines
    for l in lines:
        l.remove()
    lines.clear()
    # Draw new lines
    for i,j in edges:
        l, = ax.plot(*zip(vertices[i], vertices[j]), color='k')
        lines.append(l)

# Initial cuboid
init_vertices = get_cuboid_vertices(torso_point, torso_dims, get_rotation_matrix(yaw_angle_deg, pitch_angle_deg, roll_angle_deg))
draw_cuboid(ax, init_vertices, edges, lines)

ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.legend()
ax.set_title('Robot Feet and Torso in World Frame')

# Sliders for yaw, pitch, roll
axcolor = 'lightgoldenrodyellow'
ax_yaw = plt.axes([0.1, 0.18, 0.8, 0.03], facecolor=axcolor)
ax_pitch = plt.axes([0.1, 0.13, 0.8, 0.03], facecolor=axcolor)
ax_roll = plt.axes([0.1, 0.08, 0.8, 0.03], facecolor=axcolor)

slider_yaw = Slider(ax_yaw, 'Yaw (deg)', -10, 10, valinit=yaw_angle_deg, valstep=1)
slider_pitch = Slider(ax_pitch, 'Pitch (deg)', -10, 10, valinit=pitch_angle_deg, valstep=1)
slider_roll = Slider(ax_roll, 'Roll (deg)', -10, 10, valinit=roll_angle_deg, valstep=1)

def update(val):

    yaw = slider_yaw.val
    pitch = slider_pitch.val
    roll = slider_roll.val
    rot = get_rotation_matrix(yaw, pitch, roll)
    verts = get_cuboid_vertices(torso_point, torso_dims, rot)
    draw_cuboid(ax, verts, edges, lines)
    # Update green dots for feet in torso frame, plotted in world frame
    foot_points_torso = (rot.T @ (foot_points - torso_point).T).T
    foot_points_torso_world = foot_points_torso + torso_point  # offset to world frame
    sc_feet_torso._offsets3d = (
        foot_points_torso_world[:,0],
        foot_points_torso_world[:,1],
        foot_points_torso_world[:,2]
    )
    fig.canvas.draw_idle()

    def fmt(coords):
        return f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f})"

    front_left_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[0], 'left', 'front')
    front_right_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[1], 'right', 'front')
    back_left_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[2], 'left', 'back')
    back_right_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[3], 'right', 'back')

    print(f"Front Left: {fmt(front_left_leg_coords)}, Front Right: {fmt(front_right_leg_coords)}, Back Left: {fmt(back_left_leg_coords)}, Back Right: {fmt(back_right_leg_coords)}")

slider_yaw.on_changed(update)
slider_pitch.on_changed(update)
slider_roll.on_changed(update)

plt.show()
