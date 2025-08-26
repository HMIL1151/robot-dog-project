import numpy as np

# ---------- Utility functions ----------
def rot_yaw_pitch_roll(yaw, pitch, roll):
    """Return 3x3 rotation matrix for yaw (Z), pitch (Y), roll (X)."""
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)

    # Rotation matrices
    Rz = np.array([[cy, -sy, 0],
                   [sy,  cy, 0],
                   [ 0,   0, 1]])

    Ry = np.array([[cp, 0, sp],
                   [ 0, 1,  0],
                   [-sp, 0, cp]])

    Rx = np.array([[1,  0,   0],
                   [0, cr, -sr],
                   [0, sr,  cr]])

    # Combined rotation (yaw → pitch → roll)
    return Rz @ Ry @ Rx


def transform_point(point, R, t):
    """Apply rotation R and translation t to a 3D point."""
    return R @ point + t


# ---------- Setup world frame ----------
# Torso origin in world frame
torso_origin = np.array([0.0, 0.0, 135.0])  # e.g. 30 cm above ground

# Feet positions (fixed on ground, world frame)
feet_world = {
    "FL": np.array([ 221.0,  95.0, 0.0]),  # front-left
    "FR": np.array([ 221.0, -95.5, 0.0]),  # front-right
    "BL": np.array([-221.0,  95.5, 0.0]),  # back-left
    "BR": np.array([-221.0, -95.5, 0.0]),  # back-right
}

# Hip positions relative to torso origin (torso frame)
hips_local = {
    "FL": np.array([ 0.2,  0.1, 0.0]),
    "FR": np.array([ 0.2, -0.1, 0.0]),
    "BL": np.array([-0.2,  0.1, 0.0]),
    "BR": np.array([-0.2, -0.1, 0.0]),
}

# ---------- Apply torso transform ----------
# Example transform: yaw=20°, pitch=10°, roll=5°, translate +x 5cm, +z 2cm
yaw   = np.deg2rad(0)
pitch = np.deg2rad(0)
roll  = np.deg2rad(5)
translation = np.array([0.0, 0.0, 0.0])

R = rot_yaw_pitch_roll(yaw, pitch, roll)
new_origin = torso_origin + translation

# Compute hip positions in world frame after transform
hips_world = {}
for leg, pos_local in hips_local.items():
    hips_world[leg] = transform_point(pos_local, R, new_origin)

# ---------- Hip-to-foot vectors in hip-local frame ----------
hip_to_foot_local = {}
for leg in hips_world:
    foot_w = feet_world[leg]
    hip_w  = hips_world[leg]

    vec_world = foot_w - hip_w

    # Express in hip's rotated local axes → use transpose(R)
    vec_local = R.T @ vec_world
    hip_to_foot_local[leg] = vec_local

# ---------- Output ----------
print("Hip-to-foot vectors (local frames, feed to IK):")
for leg, vec in hip_to_foot_local.items():
    print(f"{leg}: {vec}")
