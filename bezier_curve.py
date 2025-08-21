from math import comb
from constants import ZERO_X, ZERO_Y, ZERO_Z

def bezier_curve(step_length, step_height, delta, swing_steps, stance_steps):

    L = step_length
    H = step_height
    d = delta * L

    P0 = (ZERO_X - L/2,     ZERO_Y,     ZERO_Z)
    P1 = (ZERO_X - L/2 - d, ZERO_Y,     ZERO_Z)
    P2 = (ZERO_X - L/2,     H + ZERO_Y, ZERO_Z)
    P3 = (ZERO_X + L/2,     H + ZERO_Y, ZERO_Z)
    P4 = (ZERO_X + L/2 + d, ZERO_Y,     ZERO_Z)
    P5 = (ZERO_X + L/2,     ZERO_Y,     ZERO_Z)

    points = [P0, P1, P2, P3, P4, P5]

    n = len(points) - 1
    Bx = []
    By = []
    Bz = []
    for j in range(swing_steps):
        t = j / (swing_steps - 1)
        x = 0.0
        z = 0.0
        y = 0.0
        for i, P in enumerate(points):
            binom = comb(n, i)
            basis = binom * (1 - t) ** (n - i) * t ** i
            x += basis * P[0]
            y += basis * P[1]
            z += basis * P[2]
        Bx.append(x)
        By.append(y)
        Bz.append(z)

    x0, z0, y0 = P5
    x1, z1, y1 = P0
    for k in range(1, stance_steps + 1):
        t = k / stance_steps
        x = x0 + (x1 - x0) * t
        z = z0 + (z1 - z0) * t
        y = y0 + (y1 - y0) * t
        Bx.append(x)
        Bz.append(z)
        By.append(y)

    return Bx, Bz, By
