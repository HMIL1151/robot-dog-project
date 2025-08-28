# Python code to compute foot targets in hip frames for a quadruped and provide an interactive 3D matplotlib visualization
# - Defines torso (body) frame in world, hips in base/body frame, and feet in world frame
# - Applies torso rotation (yaw, pitch, roll in that order) and translation
# - Computes each stance foot target expressed in the corresponding hip frame after the body transform
# - Prints targets to stdout and updates a 3D plot with sliders for yaw,pitch,roll, dx,dy,dz
#
# Run in a Jupyter environment. This cell will display an interactive matplotlib figure with sliders.
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D
import math

# ---- Helper math utilities ----
def rot_z(yaw):
    c = math.cos(yaw); s = math.sin(yaw)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]])

def rot_y(pitch):
    c = math.cos(pitch); s = math.sin(pitch)
    return np.array([[ c, 0, s],
                     [ 0, 1, 0],
                     [-s, 0, c]])

def rot_x(roll):
    c = math.cos(roll); s = math.sin(roll)
    return np.array([[1, 0,  0],
                     [0, c, -s],
                     [0, s,  c]])

def transform_from_rpyt_xyz(yaw, pitch, roll, tx, ty, tz):
    # Rotation applied in order yaw (Z), pitch (Y), roll (X)
    R = rot_z(yaw) @ rot_y(pitch) @ rot_x(roll)
    T = np.eye(4)
    T[:3,:3] = R
    T[:3,3] = np.array([tx, ty, tz])
    return T

def inv_transform(T):
    R = T[:3,:3]; p = T[:3,3]
    Tinv = np.eye(4)
    Tinv[:3,:3] = R.T
    Tinv[:3,3] = -R.T @ p
    return Tinv

def euler_from_matrix_z_y_x(R):
    # Extract yaw (z), pitch (y), roll (x) from R = Rz(yaw) Ry(pitch) Rx(roll)
    # This matches our rotation composition order.
    # Handle numerical issues/clamping.
    sy = -R[2,0]  # -sin(pitch)
    sy = max(min(sy, 1.0), -1.0)
    pitch = math.asin(sy)
    # if cos(pitch) > 0:
    cy = math.cos(pitch)
    if abs(cy) > 1e-6:
        yaw = math.atan2(R[1,0], R[0,0])
        roll = math.atan2(R[2,1], R[2,2])
    else:
        # Gimbal-ish, fallback
        yaw = math.atan2(-R[0,1], R[1,1])
        roll = 0.0
    return yaw, pitch, roll

# ---- Quadruped definition ----
# Hips in body/base frame (meters). We'll define them as:
# [front_left, front_right, rear_left, rear_right]
hip_positions_base = {
    'FL': np.array([ 0.15,  0.12, 0.0]),  # front-left (x forward, y right, z up) -- choose convention: x forward, y right
    'FR': np.array([ 0.15, -0.12, 0.0]),
    'RL': np.array([-0.15,  0.12, 0.0]),
    'RR': np.array([-0.15, -0.12, 0.0])
}

# Feet in world frame (assume initial body at origin, feet on ground z = -0.20)
feet_world = {
    'FL': np.array([ 0.25,  0.12, -0.20]),
    'FR': np.array([ 0.25, -0.12, -0.20]),
    'RL': np.array([-0.25,  0.12, -0.20]),
    'RR': np.array([-0.25, -0.12, -0.20])
}

hip_names = ['FL','FR','RL','RR']

# Initial torso pose in world: identity at origin
T_WB_default = np.eye(4)

# ---- Core function: compute foot targets in hip frames after body transform ----
def compute_foot_targets(yaw_deg=0, pitch_deg=0, roll_deg=0, dx=0.0, dy=0.0, dz=0.0):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    roll = math.radians(roll_deg)
    T_WB = transform_from_rpyt_xyz(yaw, pitch, roll, dx, dy, dz)  # new body pose in world
    results = {}
    for name in hip_names:
        p_BH = hip_positions_base[name]  # hip in body frame
        T_BH = np.eye(4)
        T_BH[:3,3] = p_BH
        # New hip in world after body transform
        T_WH = T_WB @ T_BH
        # Foot transform in world (point foot => homogeneous with identity rotation)
        T_WF = np.eye(4)
        T_WF[:3,3] = feet_world[name]
        # Target expressed in new hip frame = inv(T_WH) * T_WF
        T_HF = inv_transform(T_WH) @ T_WF
        pos = T_HF[:3,3]
        R = T_HF[:3,:3]
        yaw_f, pitch_f, roll_f = euler_from_matrix_z_y_x(R)
        results[name] = {
            'T_WH': T_WH,
            'T_HF': T_HF,
            'pos_in_hip': pos,
            'orient_in_hip_rpy_deg': (math.degrees(yaw_f), math.degrees(pitch_f), math.degrees(roll_f))
        }
    return T_WB, results

# ---- Print helper ----
def print_targets(results):
    print("Foot targets expressed in each hip frame:")
    for name in hip_names:
        r = results[name]
        pos = r['pos_in_hip']
        rpy = r['orient_in_hip_rpy_deg']
        print(f" {name}: pos (m) = [{pos[0]:+.3f}, {pos[1]:+.3f}, {pos[2]:+.3f}]  |  rpy (deg, yaw,pitch,roll) = [{rpy[0]:+.2f}, {rpy[1]:+.2f}, {rpy[2]:+.2f}]")
    print("-"*60)

# ---- Visualization ----
fig = plt.figure(figsize=(9,7))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0.15, bottom=0.35)  # room for sliders

# Plot elements to update:
# world feet scatter, hip scatter (transformed), torso origin, lines hip->foot, and text labels
world_feet_scatter = ax.scatter([], [], [], s=40)
hip_scatter = ax.scatter([], [], [], s=30)
lines = [ax.plot([], [], [], linewidth=1.0)[0] for _ in hip_names]
labels = [ax.text(0,0,0,'') for _ in hip_names]
torso_marker = ax.scatter([], [], [], s=60)

ax.set_xlim(-0.5, 0.5)
ax.set_ylim(-0.5, 0.5)
ax.set_zlim(-0.4, 0.3)
ax.set_xlabel('X (forward)')
ax.set_ylabel('Y (right)')
ax.set_zlabel('Z (up)')
ax.set_title('Quadruped: world feet (fixed) and hip frames after torso transform\n(Adjust sliders to change torso pose)')

# Sliders
axcolor = 'lightgoldenrodyellow'
ax_yaw = plt.axes([0.15, 0.26, 0.7, 0.03])
ax_pitch = plt.axes([0.15, 0.22, 0.7, 0.03])
ax_roll = plt.axes([0.15, 0.18, 0.7, 0.03])
ax_dx = plt.axes([0.15, 0.14, 0.7, 0.03])
ax_dy = plt.axes([0.15, 0.10, 0.7, 0.03])
ax_dz = plt.axes([0.15, 0.06, 0.7, 0.03])

s_yaw = Slider(ax_yaw, 'Yaw (deg)', -45.0, 45.0, valinit=0.0, valstep=0.5)
s_pitch = Slider(ax_pitch, 'Pitch (deg)', -45.0, 45.0, valinit=0.0, valstep=0.5)
s_roll = Slider(ax_roll, 'Roll (deg)', -45.0, 45.0, valinit=0.0, valstep=0.5)
s_dx = Slider(ax_dx, 'dx (m)', -0.25, 0.25, valinit=0.0, valstep=0.01)
s_dy = Slider(ax_dy, 'dy (m)', -0.25, 0.25, valinit=0.0, valstep=0.01)
s_dz = Slider(ax_dz, 'dz (m)', -0.25, 0.25, valinit=0.0, valstep=0.01)

# Button to print current targets
but_ax = plt.axes([0.02, 0.02, 0.1, 0.05])
btn = Button(but_ax, 'Print targets')

def update_plot(val=None):
    yaw = s_yaw.val; pitch = s_pitch.val; roll = s_roll.val
    dx = s_dx.val; dy = s_dy.val; dz = s_dz.val
    T_WB, results = compute_foot_targets(yaw, pitch, roll, dx, dy, dz)
    # world feet positions
    wf = np.array([feet_world[n] for n in hip_names])
    world_feet_scatter._offsets3d = (wf[:,0], wf[:,1], wf[:,2])
    # hips in world
    hips_world = np.array([results[n]['T_WH'][:3,3] for n in hip_names])
    hip_scatter._offsets3d = (hips_world[:,0], hips_world[:,1], hips_world[:,2])
    # torso origin marker
    torso_origin = T_WB[:3,3]
    torso_marker._offsets3d = ([torso_origin[0]], [torso_origin[1]], [torso_origin[2]])
    # lines from hip to foot and labels, also update label text to show pos_in_hip
    for i, name in enumerate(hip_names):
        foot_w = feet_world[name]
        hip_w = hips_world[i]
        xs = [hip_w[0], foot_w[0]]
        ys = [hip_w[1], foot_w[1]]
        zs = [hip_w[2], foot_w[2]]
        lines[i].set_data(xs, ys)
        lines[i].set_3d_properties(zs)
        # label near hip with pos_in_hip printed succinctly
        p_in_hip = results[name]['pos_in_hip']
        labels[i].set_position((hip_w[0], hip_w[1]))
        labels[i].set_3d_properties(hip_w[2])
        labels[i].set_text(f"{name}\n[{p_in_hip[0]:+.2f},{p_in_hip[1]:+.2f},{p_in_hip[2]:+.2f}]")
    fig.canvas.draw_idle()
    # print to stdout as requested
    print_targets(results)

def on_button(event):
    _, results = compute_foot_targets(s_yaw.val, s_pitch.val, s_roll.val, s_dx.val, s_dy.val, s_dz.val)
    print_targets(results)

# connect sliders
s_yaw.on_changed(update_plot)
s_pitch.on_changed(update_plot)
s_roll.on_changed(update_plot)
s_dx.on_changed(update_plot)
s_dy.on_changed(update_plot)
s_dz.on_changed(update_plot)
btn.on_clicked(on_button)

# initial draw
update_plot(None)

plt.show()
