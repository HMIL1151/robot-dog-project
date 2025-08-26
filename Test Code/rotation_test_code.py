
import math
import matplotlib
from matplotlib.widgets import Slider



leg_x_seperation_mm = 221.0
foot_y_seperation_mm = 95.5 * 2
torso_zero_height_mm = 135.0

left_front_foot_coords_WORLD = (leg_x_seperation_mm / 2, foot_y_seperation_mm / 2, 0)
right_front_foot_coords_WORLD = (leg_x_seperation_mm / 2, -foot_y_seperation_mm / 2, 0)
left_back_foot_coords_WORLD = (-leg_x_seperation_mm / 2, foot_y_seperation_mm / 2, 0)
right_back_foot_coords_WORLD = (-leg_x_seperation_mm / 2, -foot_y_seperation_mm / 2, 0)

torso_origin_coords_WORLD = (0, 0, torso_zero_height_mm)

torso_width_y_mm = 85.0
torso_height_z_mm = 48.0
torso_length_x_mm = leg_x_seperation_mm

def on_any_slider(val):
    update(None)

# --- 3D Plotting and Sliders ---
import matplotlib.pyplot as plt

# --- Helper functions to replace numpy ---
def vec_add(a, b):
	return tuple(x + y for x, y in zip(a, b))

def vec_sub(a, b):
	return tuple(x - y for x, y in zip(a, b))

def vec_mul(a, scalar):
	return tuple(x * scalar for x in a)

def vec_div(a, scalar):
	return tuple(x / scalar for x in a)

def vec_dot(a, b):
	return sum(x * y for x, y in zip(a, b))

def vec_norm(a):
	return math.sqrt(sum(x * x for x in a))

def vec_distance(a, b):
	return vec_norm(vec_sub(a, b))

def mat_vec_mul(mat, vec):
	return tuple(sum(mat[i][j] * vec[j] for j in range(3)) for i in range(3))

def mat_mul(a, b):
	# Matrix multiplication (3x3)
	return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))

def transpose(mat):
	return tuple(tuple(mat[j][i] for j in range(3)) for i in range(3))

def make_eye3():
	return ((1,0,0),(0,1,0),(0,0,1))

def apply_rotation(points, center, yaw, pitch, roll):
	R = rotation_matrix(yaw, pitch, roll)
	rotated = []
	for pt in points:
		shifted = vec_sub(pt, center)
		rotated_pt = mat_vec_mul(R, shifted)
		rotated.append(vec_add(rotated_pt, center))
	return rotated

def rotation_matrix(yaw, pitch, roll):
	cy, sy = math.cos(yaw), math.sin(yaw)
	cp, sp = math.cos(pitch), math.sin(pitch)
	cr, sr = math.cos(roll), math.sin(roll)
	Rz = (
		(cy, -sy, 0),
		(sy,  cy, 0),
		( 0,   0, 1)
	)
	Ry = (
		(cp, 0, sp),
		( 0, 1,  0),
		(-sp,0, cp)
	)
	Rx = (
		(1,  0,   0),
		(0, cr, -sr),
		(0, sr,  cr)
	)
	return mat_mul(mat_mul(Rz, Ry), Rx)

def get_torso_corners(center, length, width, height):
	l = length / 2
	w = width / 2
	h = height / 2
	corners = [
		( l,  w,  h),
		( l, -w,  h),
		(-l, -w,  h),
		(-l,  w,  h),
		( l,  w, -h),
		( l, -w, -h),
		(-l, -w, -h),
		(-l,  w, -h),
	]
	return [vec_add(c, center) for c in corners]

def plot_torso(ax, corners):
	edges = [
		(0,1),(1,2),(2,3),(3,0), # top face
		(4,5),(5,6),(6,7),(7,4), # bottom face
		(0,4),(1,5),(2,6),(3,7)  # verticals
	]
	for i,j in edges:
		xs = [corners[i][0], corners[j][0]]
		ys = [corners[i][1], corners[j][1]]
		zs = [corners[i][2], corners[j][2]]
		ax.plot(xs, ys, zs, color='orange')

# --- 3D Plotting and Sliders ---
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

foot_points = [
	left_front_foot_coords_WORLD,
	right_front_foot_coords_WORLD,
	left_back_foot_coords_WORLD,
	right_back_foot_coords_WORLD
]
torso_origin = torso_origin_coords_WORLD

def update(val):
	yaw = math.radians(slider_yaw.val)
	pitch = math.radians(slider_pitch.val)
	roll = math.radians(slider_roll.val)
	tx = slider_tx.val
	ty = slider_ty.val
	tz = slider_tz.val
	ax.cla()

	# 1. Compute rotation matrix
	R = rotation_matrix(yaw, pitch, roll)

	# 2. Torso origin (before translation)
	torso_origin_rot = torso_origin

	# 3. Torso box corners at original origin
	corners = get_torso_corners(torso_origin_rot, torso_length_x_mm, torso_width_y_mm, torso_height_z_mm)
	# 4. Rotate corners about original origin
	corners_rot = [mat_vec_mul(R, vec_sub(c, torso_origin_rot)) for c in corners]
	corners_rot = [vec_add(c, torso_origin_rot) for c in corners_rot]
	# 5. Translate all rotated corners
	torso_origin_final = vec_add(torso_origin_rot, (tx, ty, tz))
	corners_final = [vec_add(c, (tx, ty, tz)) for c in corners_rot]

	# Plot foot points (fixed in world)
	xs = [pt[0] for pt in foot_points]
	ys = [pt[1] for pt in foot_points]
	zs = [pt[2] for pt in foot_points]
	ax.scatter(xs, ys, zs, c='b', s=50, label='Feet')

	# Plot torso origin
	ax.scatter(*torso_origin_final, c='r', s=80, label='Torso Origin')

	# Plot torso box
	plot_torso(ax, corners_final)

	# Draw coordinate axes at torso origin, showing orientation
	axis_length = 60
	origin = torso_origin_final
	axes = [ (axis_length,0,0), (0,axis_length,0), (0,0,axis_length) ]
	axes_rot = [mat_vec_mul(R, a) for a in axes]
	colors = ['r', 'g', 'b']
	labels = ['X', 'Y', 'Z']
	for i in range(3):
		ax.plot([origin[0], origin[0]+axes_rot[i][0]],
				[origin[1], origin[1]+axes_rot[i][1]],
				[origin[2], origin[2]+axes_rot[i][2]],
				color=colors[i], linewidth=3)
		ax.text(origin[0]+axes_rot[i][0], origin[1]+axes_rot[i][1], origin[2]+axes_rot[i][2],
				f'{labels[i]}', color=colors[i], fontsize=12, weight='bold')

	# Add hip points (relative to torso, rotate with torso)
	l = torso_length_x_mm / 2
	w = torso_width_y_mm / 2
	h = 0
	hips_local = [
		( l,  w, h),  # left_front
		( l, -w, h),  # right_front
		(-l, -w, h),  # right_rear
		(-l,  w, h),  # left_rear
	]
	hips_rot = [mat_vec_mul(R, h) for h in hips_local]
	hips_world = [vec_add(vec_add(torso_origin_rot, h), (tx, ty, tz)) for h in hips_rot]
	hip_labels = ['left_front', 'right_front', 'right_rear', 'left_rear']
	for i in range(len(hip_labels)):
		ax.scatter(hips_world[i][0], hips_world[i][1], hips_world[i][2], c='m', s=80, marker='o')

	# Label torso faces (left, right, front, rear) with increased spacing
	face_offset = 1.5
	face_dirs = [ (0, w * face_offset, 0), (0, -w * face_offset, 0), (l * face_offset, 0, 0), (-l * face_offset, 0, 0) ]
	face_centers = [vec_add(torso_origin_final, mat_vec_mul(R, d)) for d in face_dirs]
	face_labels = ['left', 'right', 'front', 'rear']
	for fc, fl in zip(face_centers, face_labels):
		ax.text(fc[0], fc[1], fc[2]+torso_height_z_mm/2+10, fl, color='black', fontsize=12, ha='center', weight='bold')

	# Always pair hips to their original feet (fixed mapping)
	foot_points_arr = foot_points
	hip_to_foot_idx = [0, 1, 3, 2]  # left_front, right_front, right_rear (to left_back), left_rear (to right_back)

	# Draw vectors from each hip (rotated) to its paired stationary foot
	for i, idx in enumerate(hip_to_foot_idx):
		hip = hips_world[i]
		foot = foot_points_arr[idx]
		ax.plot([hip[0], foot[0]], [hip[1], foot[1]], [hip[2], foot[2]], color='k', linestyle='--', linewidth=2)

	# Draw custom coordinate axes at each hip (custom orientation)
	hip_axes_local = [
		# left_front
		[(-1, 0, 0), (0, 0, -1), (0, 1, 0)],
		# right_front
		[(-1, 0, 0), (0, 0, -1), (0, -1, 0)],
		# right_rear
		[(-1, 0, 0), (0, 0, -1), (0, -1, 0)],
		# left_rear
		[(-1, 0, 0), (0, 0, -1), (0, 1, 0)],
	]
	for i, hip in enumerate(hips_world):
		local_axes = hip_axes_local[i]
		for j, axis_dir in enumerate(local_axes):
			axis_vec = vec_mul(axis_dir, axis_length)
			axis_vec_rot = mat_vec_mul(R, axis_vec)
			ax.plot([hip[0], hip[0]+axis_vec_rot[0]],
					[hip[1], hip[1]+axis_vec_rot[1]],
					[hip[2], hip[2]+axis_vec_rot[2]],
					color=colors[j], linewidth=2, alpha=0.7)

	ax.set_xlabel('X (mm)')
	ax.set_ylabel('Y (mm)')
	ax.set_zlabel('Z (mm)')
	ax.set_title('Robot Dog Torso Orientation')
	ax.legend()
	ax.set_box_aspect([1,1,0.5])
	ax.set_xlim(-300, 300)
	ax.set_ylim(-200, 200)
	ax.set_zlim(0, 250)
	plt.draw()

	print('--- Hip to Foot Vectors (in Hip Local Axes) ---')
	# Define the new hip axes for each hip (in torso coordinates)
	hip_axes_local = [
		# left_front
		[(-1, 0, 0), (0, 0, -1), (0, 1, 0)],
		# right_front
		[(-1, 0, 0), (0, 0, -1), (0, -1, 0)],
		# right_rear
		[(-1, 0, 0), (0, 0, -1), (0, -1, 0)],
		# left_rear
		[(-1, 0, 0), (0, 0, -1), (0, 1, 0)],
	]
	z_offsets = [torso_width_y_mm/2] * 4  # or set different values for each hip if needed
	hip_labels = ['left front', 'right front', 'right rear', 'left rear']
	for i, idx in enumerate(hip_to_foot_idx):
		hip = hips_world[i]
		foot = foot_points_arr[idx]
		vec_world = vec_sub(foot, hip)
		axes = hip_axes_local[i]
		R_hip = tuple(mat_vec_mul(R, axis) for axis in axes)
		vec_local = [vec_dot(R_hip[j], vec_world) for j in range(3)]
		vec_local[2] += z_offsets[i]
		print(f"{hip_labels[i].capitalize()} Hip to Foot: X={vec_local[0]:.2f} mm, Y={vec_local[1]:.2f} mm, Z={vec_local[2]:.2f} mm")


fig = plt.figure(figsize=(8,7))
ax = fig.add_subplot(111, projection='3d')

# Sliders
axcolor = 'lightgoldenrodyellow'
ax_yaw = plt.axes([0.15, 0.02, 0.65, 0.02], facecolor=axcolor)
ax_pitch = plt.axes([0.15, 0.05, 0.65, 0.02], facecolor=axcolor)
ax_roll = plt.axes([0.15, 0.08, 0.65, 0.02], facecolor=axcolor)
ax_tx = plt.axes([0.02, 0.15, 0.02, 0.65], facecolor=axcolor)
ax_ty = plt.axes([0.06, 0.15, 0.02, 0.65], facecolor=axcolor)
ax_tz = plt.axes([0.10, 0.15, 0.02, 0.65], facecolor=axcolor)

slider_yaw = Slider(ax_yaw, 'Yaw (°)', -30, 30, valinit=0, valstep=0.5)
slider_pitch = Slider(ax_pitch, 'Pitch (°)', -30, 30, valinit=0, valstep=0.5)
slider_roll = Slider(ax_roll, 'Roll (°)', -30, 30, valinit=0, valstep=0.5)
slider_tx = Slider(ax_tx, 'X (mm)', -150, 150, valinit=0, valstep=0.5, orientation='vertical')
slider_ty = Slider(ax_ty, 'Y (mm)', -150, 150, valinit=0, valstep=0.5, orientation='vertical')
slider_tz = Slider(ax_tz, 'Z (mm)', -100, 100, valinit=0, valstep=0.5, orientation='vertical')

slider_yaw.on_changed(on_any_slider)
slider_pitch.on_changed(on_any_slider)
slider_roll.on_changed(on_any_slider)
slider_tx.on_changed(on_any_slider)
slider_ty.on_changed(on_any_slider)
slider_tz.on_changed(on_any_slider)

plt.show()

