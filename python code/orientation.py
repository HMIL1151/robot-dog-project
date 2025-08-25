import math

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

def deg2rad(deg):
    return deg * math.pi / 180.0

def get_rotation_matrix(yaw, pitch, roll):
    cy = math.cos(deg2rad(yaw))
    sy = math.sin(deg2rad(yaw))
    cp = math.cos(deg2rad(pitch))
    sp = math.sin(deg2rad(pitch))
    cr = math.cos(deg2rad(roll))
    sr = math.sin(deg2rad(roll))
    yaw_matrix = [
        [cy, -sy, 0],
        [sy,  cy, 0],
        [ 0,   0, 1]
    ]
    pitch_matrix = [
        [cp, 0, sp],
        [ 0, 1,  0],
        [-sp,0, cp]
    ]
    roll_matrix = [
        [1, 0, 0],
        [0, cr, -sr],
        [0, sr, cr]
    ]
    return matmul3(matmul3(yaw_matrix, pitch_matrix), roll_matrix)


def draw_cuboid(ax, vertices, edges, lines):
    # Remove old lines
    for l in lines:
        l.remove()
    lines.clear()
    # Draw new lines
    for i,j in edges:
        l, = ax.plot(*zip(vertices[i], vertices[j]), color='k')
        lines.append(l)

def fmt(coords):
        return f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f})"


leg_x_seperation_mm = 221.0
foot_y_seperation_mm = 95.5*2
torso_zero_height_mm = 135.0

left_front_foot_coords_WORLD = [leg_x_seperation_mm / 2, foot_y_seperation_mm/2, 0]
right_front_foot_coords_WORLD = [leg_x_seperation_mm / 2, -foot_y_seperation_mm/2, 0]
left_back_foot_coords_WORLD = [-leg_x_seperation_mm / 2, foot_y_seperation_mm/2, 0]
right_back_foot_coords_WORLD = [-leg_x_seperation_mm / 2, -foot_y_seperation_mm/2, 0]

torso_origin_coords_WORLD = [0, 0, torso_zero_height_mm]

torso_width_y_mm = 85.0
torso_height_z_mm = 48.0
torso_length_x_mm = 367.4

# Returns (front_left_leg_coords, front_right_leg_coords, back_left_leg_coords, back_right_leg_coords)
def get_coords(yaw_angle_deg, pitch_angle_deg, roll_angle_deg):
    foot_points = [
        left_front_foot_coords_WORLD,
        right_front_foot_coords_WORLD,
        left_back_foot_coords_WORLD,
        right_back_foot_coords_WORLD
    ]
    torso_point = torso_origin_coords_WORLD
    rot = get_rotation_matrix(yaw_angle_deg, pitch_angle_deg, roll_angle_deg)
    rotT = transpose3(rot)
    # Transform feet to torso frame, then back to world frame (for plotting/leg coords)
    foot_points_torso = [matvecmul3(rotT, vec_sub(fp, torso_point)) for fp in foot_points]
    foot_points_torso_world = [vec_add(fp, torso_point) for fp in foot_points_torso]

    def world_foot_coords_to_leg_foot_coords(coords, side, face):
        x_world, y_world, z_world = coords
        if face == 'front':
            x_leg = (leg_x_seperation_mm / 2) - x_world
        else:
            x_leg = -(leg_x_seperation_mm / 2) - x_world
        y_leg = torso_height_z_mm - z_world + 87.0
        z_leg = abs(y_world)
        return (x_leg, y_leg, z_leg)

    front_left_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[0], 'left', 'front')
    front_right_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[1], 'right', 'front')
    back_left_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[2], 'left', 'back')
    back_right_leg_coords = world_foot_coords_to_leg_foot_coords(foot_points_torso_world[3], 'right', 'back')

    #print(f"Front Left: {fmt(front_left_leg_coords)}, Front Right: {fmt(front_right_leg_coords)}, Back Left: {fmt(back_left_leg_coords)}, Back Right: {fmt(back_right_leg_coords)}")

    return (front_left_leg_coords, front_right_leg_coords, back_left_leg_coords, back_right_leg_coords)