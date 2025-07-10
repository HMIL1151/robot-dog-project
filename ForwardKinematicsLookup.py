#This file is to compute the forward kinematics of a robot arm using a lookup table.
#It uses the numpy library for numerical operations and the scipy library for interpolation.

import numpy as np
from scipy.interpolate import RegularGridInterpolator

def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * (180 / np.pi)

def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * (np.pi / 180)

a = 40 #mm
b = 50 #mm
c = 25 #mm
d = 80 #mm
e = 78 #mm
f = 20 #mm
g = 70 #mm
z = 46 #mm

h = np.sqrt(pow(6.5,2) + pow(12,2)) #mm
theta_h = np.arctan(6.5/12) + np.pi/2

theta_a_min = 49 #degrees
theta_a_max = 112 #degrees
theta_d_min = 62 #degrees
theta_d_max = 242 #degrees
angle_step = 1 #degrees

def forward_kinematics(theta_a_deg, theta_d_deg):
    theta_a = degrees_to_radians(theta_a_deg)
    theta_d = degrees_to_radians(theta_d_deg)
    q = np.sqrt(pow(a, 2) + pow(z, 2) - 2 * a * z * np.cos(theta_a))
    theta_Q = np.arccos((pow(a, 2) + pow(q, 2) - pow(z, 2)) / (2 * a * q))
    theta_Q_prime = np.arccos((pow(q, 2) + pow(b, 2) - pow(c, 2)) / (2 * q * b))
    theta_b = theta_Q + theta_Q_prime
    print(f"θ_b: {radians_to_degrees(theta_b)} degrees")

    theta_q_prime = np.arccos((pow(q, 2) + pow(c, 2) - pow(b, 2)) / (2 * q * c))
    theta_q = np.arccos((pow(z, 2) + pow(q, 2) - pow(a, 2)) / (2 * z * q))
    theta_c = np.pi - theta_q - theta_q_prime
    print(f"θ_c: {radians_to_degrees(theta_c)} degrees")

    theta_k = np.pi - theta_d
    j = np.sqrt(pow(c, 2) + pow(h, 2) - 2 * c * h * np.cos(theta_h))
    theta_c_prime = np.arccos((pow(c, 2) + pow(j, 2) - pow(h, 2)) / (2 * c * j))
    theta_c_prime_prime = theta_c - theta_c_prime
    m = np.sqrt(pow(j, 2) + pow(d, 2) - 2 * j * d * np.cos(theta_c_prime_prime + theta_k))
    theta_f = np.arccos((pow(e, 2) + pow(f, 2) - pow(m, 2)) / (2 * e * f))
    print(f"θ_f: {radians_to_degrees(theta_f)} degrees")

    theta_E_prime = np.arccos((pow(h, 2) + pow(j, 2) - pow(c, 2)) / (2 * h * j))
    theta_E_prime_prime = np.arccos((pow(j, 2) + pow(m, 2) - pow(d, 2)) / (2 * j * m))
    theta_E_prime_prime_prime = np.arccos((pow(e, 2) + pow(m, 2) - pow(f, 2)) / (2 * m * e))
    theta_e = theta_E_prime + theta_E_prime_prime + theta_E_prime_prime_prime
    print(f"θ_e: {radians_to_degrees(theta_e)} degrees")

    theta_b_prime = np.pi - theta_a - theta_b
    theta_h_prime = theta_c + theta_h - np.pi
    theta_e_prime = 2*np.pi - theta_c - theta_h - theta_e
    theta_f_prime = theta_f - theta_e_prime

    x = a * np.cos(theta_a) + b * np.cos(theta_b_prime) + h * np.cos(theta_h_prime) + e * np.cos(theta_e_prime) - np.cos(theta_f_prime) * (f + g)
    y = -1 * (d * np.sin(theta_d) + g * np.sin(theta_f_prime))
    print(f"End Effector Position: x = {x:.2f} mm, y = {y:.2f} mm")
    return (x, y)


# Generate lookup table for all combinations of theta_a and theta_d
import csv

theta_a_values = np.arange(theta_a_min, theta_a_max + angle_step, angle_step)
theta_d_values = np.arange(theta_d_min, theta_d_max + angle_step, angle_step)

lookup_table = []
for theta_a in theta_a_values:
    for theta_d in theta_d_values:
        x, y = forward_kinematics(theta_a, theta_d)
        lookup_table.append({'theta_a': theta_a, 'theta_d': theta_d, 'x': x, 'y': y})

# Write lookup table to CSV
with open('forward_kinematics_lookup.csv', 'w', newline='') as csvfile:
    fieldnames = ['theta_a', 'theta_d', 'x', 'y']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in lookup_table:
        writer.writerow(row)

print(f"Lookup table generated with {len(lookup_table)} entries and saved to forward_kinematics_lookup.csv")
import matplotlib.pyplot as plt
import math

# Create reachability map
reachability = np.zeros((len(theta_a_values), len(theta_d_values)))
for i, theta_a in enumerate(theta_a_values):
    for j, theta_d in enumerate(theta_d_values):
        x, y = forward_kinematics(theta_a, theta_d)
        if not (math.isnan(x) or math.isnan(y)):
            reachability[i, j] = 1  # Reachable
        else:
            reachability[i, j] = 0  # Unreachable

plt.figure(figsize=(8, 6))
plt.imshow(reachability, extent=[theta_d_min, theta_d_max, theta_a_min, theta_a_max], origin='lower', aspect='auto', cmap='Greens')
plt.colorbar(label='Reachable (1) / Unreachable (0)')
plt.xlabel('theta_d (degrees)')
plt.ylabel('theta_a (degrees)')
plt.title('Reachability Map of End Effector')
plt.tight_layout()
plt.show()

# Plot reachable (x, y) workspace with unreachable (NaN) in red
x_coords = []
y_coords = []
nan_x_coords = []
nan_y_coords = []
for theta_a in theta_a_values:
    for theta_d in theta_d_values:
        x, y = forward_kinematics(theta_a, theta_d)
        if not (math.isnan(x) or math.isnan(y)):
            x_coords.append(x)
            y_coords.append(y)

plt.figure(figsize=(8, 8))
plt.scatter(x_coords, y_coords, s=2, c='green', label='Reachable')
# Add big black dots at (0,0) and (z,0)
plt.scatter([0, z], [0, 0], s=100, c='black', marker='o', label='Reference Points (0,0), (z,0)')
plt.xlabel('x (mm)')
plt.ylabel('y (mm)')
plt.title('Reachable Workspace of End Effector')
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()