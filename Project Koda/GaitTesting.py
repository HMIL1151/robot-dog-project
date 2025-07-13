
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

# Load CSV data
df = pd.read_csv('forward_kinematics_lookup.csv')


# --- Curve definitions ---
# Choose curve_type: 'vertical', 'line', 'circle', 'ellipse'
curve_type = 'ellipse'  # options: 'vertical', 'line', 'circle', 'ellipse'


# Parameters for each curve type
curve_params = {
    'vertical': {'x0': 50, 'y_min': -120, 'y_max': -60},
    'horizontal': {'y0': -100, 'x_min': 20, 'x_max': 80},
    'line': {'m': 0.4, 'c': -100, 'x_min': 0, 'x_max': 125},
    'circle': {'xc': 50, 'yc': -70, 'r': 30},
    'ellipse': {'xc': 50, 'yc': -100, 'a': 30, 'b': 20},
    'half_flat_ellipse': {'xc': 23, 'yc': -120, 'a': 30, 'b': 40, 'flat_y': -90}
}



# Threshold for "closeness" to the curve
threshold = 5.0  # mm

# Step length for vertical/line (mm)
step_length_mm = 2.5
# Step length for ellipse (mm, arc length)
step_length_ellipse_mm = 2.5
# Step angle for circle (degrees)
step_angle_deg = 10.0

def curve_points():
    points = []
    if curve_type == 'vertical':
        # ...existing code...
        y_min = curve_params['vertical']['y_min'] if curve_params['vertical']['y_min'] is not None else df['y'].min()
        y_max = curve_params['vertical']['y_max'] if curve_params['vertical']['y_max'] is not None else df['y'].max()
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        y_vals = np.arange(y_min, y_max, step_length_mm)
        for y in y_vals:
            points.append((curve_params['vertical']['x0'], y))
    elif curve_type == 'horizontal':
        # ...existing code...
        y0 = curve_params['horizontal']['y0']
        x_min = curve_params['horizontal']['x_min'] if curve_params['horizontal']['x_min'] is not None else df['x'].min()
        x_max = curve_params['horizontal']['x_max'] if curve_params['horizontal']['x_max'] is not None else df['x'].max()
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        x_vals = np.arange(x_min, x_max, step_length_mm)
        for x in x_vals:
            points.append((x, y0))
    elif curve_type == 'line':
        # ...existing code...
        m = curve_params['line']['m']
        c = curve_params['line']['c']
        x_min = curve_params['line']['x_min'] if curve_params['line']['x_min'] is not None else df['x'].min()
        x_max = curve_params['line']['x_max'] if curve_params['line']['x_max'] is not None else df['x'].max()
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        x_vals = np.arange(x_min, x_max, step_length_mm)
        for x in x_vals:
            y = m * x + c
            points.append((x, y))
    elif curve_type == 'circle':
        # ...existing code...
        xc = curve_params['circle']['xc']
        yc = curve_params['circle']['yc']
        r = curve_params['circle']['r']
        theta_deg = np.arange(0, 360, step_angle_deg)
        theta_rad = np.deg2rad(theta_deg)
        for t in theta_rad:
            x = xc + r * np.cos(t)
            y = yc + r * np.sin(t)
            points.append((x, y))
    elif curve_type == 'ellipse':
        # ...existing code...
        xc = curve_params['ellipse']['xc']
        yc = curve_params['ellipse']['yc']
        a = curve_params['ellipse']['a']
        b = curve_params['ellipse']['b']
        perimeter = np.pi * (3*(a+b) - np.sqrt((3*a+b)*(a+3*b)))
        n_steps = int(perimeter / step_length_ellipse_mm)
        theta_fine = np.linspace(0, 2*np.pi, 1000)
        x_fine = xc + a * np.cos(theta_fine)
        y_fine = yc + b * np.sin(theta_fine)
        ds = np.sqrt(np.diff(x_fine)**2 + np.diff(y_fine)**2)
        s = np.concatenate(([0], np.cumsum(ds)))
        s_steps = np.linspace(0, s[-1], n_steps, endpoint=False)
        theta_steps = np.interp(s_steps, s, theta_fine)
        for t in theta_steps:
            x = xc + a * np.cos(t)
            y = yc + b * np.sin(t)
            points.append((x, y))
    elif curve_type == 'half_flat_ellipse':
        # Parametric: half-ellipse (top) + flat bottom, continuous, arc-length stepping
        xc = curve_params['half_flat_ellipse']['xc']
        yc = curve_params['half_flat_ellipse']['yc']
        a = curve_params['half_flat_ellipse']['a']
        b = curve_params['half_flat_ellipse']['b']
        # Top half-ellipse: theta from pi to 0
        theta_fine = np.linspace(np.pi, 0, 1000)
        x_fine = xc + a * np.cos(theta_fine)
        y_fine = yc + b * np.sin(theta_fine)
        ds_ellipse = np.sqrt(np.diff(x_fine)**2 + np.diff(y_fine)**2)
        s_ellipse = np.concatenate(([0], np.cumsum(ds_ellipse)))
        n_steps_ellipse = max(2, int(s_ellipse[-1] / step_length_ellipse_mm))
        s_steps_ellipse = np.linspace(0, s_ellipse[-1], n_steps_ellipse, endpoint=True)
        theta_steps_ellipse = np.interp(s_steps_ellipse, s_ellipse, theta_fine)
        ellipse_points = [(xc + a * np.cos(t), yc + b * np.sin(t)) for t in theta_steps_ellipse]
        points.extend(ellipse_points)
        # Automatically set flat_y to the y value at the horizontal tips of the ellipse
        flat_y = ellipse_points[0][1]  # y at left tip (theta=pi)
        # Flat bottom: from right end to left end of ellipse, arc-length stepping
        x_right = ellipse_points[-1][0]
        x_left = ellipse_points[0][0]
        flat_length = abs(x_right - x_left)
        n_steps_flat = max(2, int(flat_length / step_length_mm))
        x_flat = np.linspace(x_right, x_left, n_steps_flat, endpoint=True)
        # Exclude endpoints to avoid duplicate points
        for x in x_flat[1:-1]:
            points.append((x, flat_y))
        # Add left endpoint to close the curve
        points.append((x_left, flat_y))
    return points
    return points
    return points



# Clean CSV points: remove rows with NaN or non-numeric x/y
df_clean = df.copy()
df_clean = df_clean[pd.to_numeric(df_clean['x'], errors='coerce').notnull()]
df_clean = df_clean[pd.to_numeric(df_clean['y'], errors='coerce').notnull()]
csv_points = df_clean[['x', 'y']].astype(float).values
curve_step_points = np.array(curve_points())
print(f"Number of curve step points: {len(curve_step_points)}")
print(f"Number of valid CSV points: {len(csv_points)}")

# Check for sufficient points
if len(csv_points) < len(curve_step_points):
    print("Error: Not enough valid CSV points for matching. Reduce step density or check CSV data.")
    matched_points = np.empty((0,2))
else:
    # Expanding radius search for each curve step point, no reuse
    csv_points_available = csv_points.copy()
    used_indices = set()
    matched_points = []
    for i, step_pt in enumerate(curve_step_points):
        found = False
        radius = 1.0  # Start with 1mm
        max_radius = 100.0  # Maximum search radius
        while not found and radius <= max_radius:
            dists = np.linalg.norm(csv_points_available - step_pt, axis=1)
            candidates = np.where(dists <= radius)[0]
            # Only consider unused points
            candidates = [idx for idx in candidates if idx not in used_indices]
            if candidates:
                # Pick the closest among candidates
                min_idx = candidates[np.argmin(dists[candidates])]
                matched_points.append(csv_points_available[min_idx])
                used_indices.add(min_idx)
                found = True
            else:
                radius += 1.0  # Increase radius by 1mm
        if not found:
            print(f"Warning: No CSV point found within {max_radius}mm for curve step point {i} at {step_pt}. Assigning NaN.")
            matched_points.append([np.nan, np.nan])
    matched_points = np.array(matched_points)

print(f"Number of matched points: {len(matched_points)} (should equal number of curve step points: {len(curve_step_points)})")

# Print thetaA and thetaD for each matched point
print("Matched points (thetaA, thetaD):")
if len(matched_points) > 0:
    # For each matched point, find the corresponding row in df_clean and print thetaA, thetaD
    for pt in matched_points:
        # If NaN, skip
        if np.isnan(pt[0]) or np.isnan(pt[1]):
            print("NaN, NaN")
            continue
        # Find the row in df_clean with matching x, y
        match = df_clean[(np.isclose(df_clean['x'], pt[0], atol=1e-6)) & (np.isclose(df_clean['y'], pt[1], atol=1e-6))]
        if not match.empty:
            thetaA = match.iloc[0]['theta_a']
            thetaD = match.iloc[0]['theta_d']
            print(f"{thetaA}, {thetaD}")
        else:
            print("Not found")


# Plot all points
plt.scatter(df['x'], df['y'], color='gray', label='All CSV Points', alpha=0.5)

# Plot step points along the curve
plt.scatter(curve_step_points[:,0], curve_step_points[:,1], color='green', s=10, label='Curve Step Points', alpha=0.7)


# Plot curve
if curve_type == 'vertical':
    x0 = curve_params['vertical']['x0']
    y_min = curve_params['vertical']['y_min'] if curve_params['vertical']['y_min'] is not None else df['y'].min()
    y_max = curve_params['vertical']['y_max'] if curve_params['vertical']['y_max'] is not None else df['y'].max()
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    plt.plot([x0, x0], [y_min, y_max], color='blue', label=f'x = {x0}')
elif curve_type == 'horizontal':
    y0 = curve_params['horizontal']['y0']
    x_min = curve_params['horizontal']['x_min'] if curve_params['horizontal']['x_min'] is not None else df['x'].min()
    x_max = curve_params['horizontal']['x_max'] if curve_params['horizontal']['x_max'] is not None else df['x'].max()
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    plt.plot([x_min, x_max], [y0, y0], color='blue', label=f'y = {y0}')
elif curve_type == 'line':
    m = curve_params['line']['m']
    c = curve_params['line']['c']
    x_min = curve_params['line']['x_min'] if curve_params['line']['x_min'] is not None else df['x'].min()
    x_max = curve_params['line']['x_max'] if curve_params['line']['x_max'] is not None else df['x'].max()
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    x_curve = np.linspace(x_min, x_max, 100)
    y_curve = m * x_curve + c
    plt.plot(x_curve, y_curve, color='blue', label=f'y = {m}x + {c}')
elif curve_type == 'circle':
    xc = curve_params['circle']['xc']
    yc = curve_params['circle']['yc']
    r = curve_params['circle']['r']
    theta = np.linspace(0, 2 * np.pi, 200)
    x_circle = xc + r * np.cos(theta)
    y_circle = yc + r * np.sin(theta)
    plt.plot(x_circle, y_circle, color='blue', label=f'Circle (r={r})')
elif curve_type == 'ellipse':
    xc = curve_params['ellipse']['xc']
    yc = curve_params['ellipse']['yc']
    a = curve_params['ellipse']['a']
    b = curve_params['ellipse']['b']
    theta = np.linspace(0, 2 * np.pi, 200)
    x_ellipse = xc + a * np.cos(theta)
    y_ellipse = yc + b * np.sin(theta)
    plt.plot(x_ellipse, y_ellipse, color='blue', label=f'Ellipse (a={a}, b={b})')
elif curve_type == 'half_flat_ellipse':
    curve_pts = np.array(curve_points())
    plt.plot(curve_pts[:,0], curve_pts[:,1], color='blue', label='Half Flat Ellipse')


# Plot matched points
if len(matched_points) > 0:
    plt.scatter(matched_points[:,0], matched_points[:,1], color='red', label='Matched Points')
    # Draw lines between curve step points and matched points
    for (cx, cy), (mx, my) in zip(curve_step_points, matched_points):
        plt.plot([cx, mx], [cy, my], color='orange', linewidth=1, alpha=0.7)

plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.title('CSV Points and Curve Intersection')
plt.show()