import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from math import comb

def bezier_curve(points, n_points=200):
    """Evaluate an n-th order Bézier curve given control points, using only math."""
    n = len(points) - 1
    Bx = []
    Bz = []
    for j in range(n_points):
        t = j / (n_points - 1)
        x = 0.0
        z = 0.0
        for i, P in enumerate(points):
            binom = comb(n, i)
            basis = binom * (1 - t) ** (n - i) * t ** i
            x += basis * P[0]
            z += basis * P[1]
        Bx.append(x)
        Bz.append(z)
    return Bx, Bz

def gait_swing(step_length=0.3, step_height=0.06, delta=0.05, n_points=200):
    """6th-order Bézier swing with smooth liftoff & touchdown."""
    L = step_length
    H = step_height
    d = delta * L
    base_y = 0.5

    # Define control points
    P0 = (-L/2, base_y)
    P1 = (-L/2 - d, base_y)
    P2 = (-L/2, H + base_y)       # small lift
    P3 = (L/2, H + base_y)
    P4 = (L/2 + d, base_y)
    P5 = (L/2, base_y)     # small pre-touch

    points = [P0, P1, P2, P3, P4, P5]
    return bezier_curve(points, n_points), points

def plot_gait():
    # Initial values
    init_L = 0.3
    init_H = 0.1
    init_delta = 0.3

    (Bx, Bz), ctrl_pts = gait_swing(step_length=init_L, step_height=init_H, delta=init_delta)

    fig, ax = plt.subplots(figsize=(7,4))
    plt.subplots_adjust(left=0.1, bottom=0.3)
    line, = ax.plot(Bx, Bz, 'b-', label='6th-order Bézier swing')
    ctrl_scatter = ax.scatter(*zip(*ctrl_pts), c='red', marker='o', label='Control points')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.set_title("6th-order Bézier Foot Swing")
    ax.set_xlabel("x (step length)")
    ax.set_ylabel("z (height)")
    ax.axis('equal')
    ax.grid(True)
    ax.legend()

    # Slider axes
    axcolor = 'lightgoldenrodyellow'
    ax_L = plt.axes([0.1, 0.2, 0.8, 0.03], facecolor=axcolor)
    ax_H = plt.axes([0.1, 0.15, 0.8, 0.03], facecolor=axcolor)
    ax_delta = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor=axcolor)

    slider_L = Slider(ax_L, 'Step Length (L)', 0.05, 0.6, valinit=init_L, valstep=0.01)
    slider_H = Slider(ax_H, 'Step Height (H)', 0.01, 0.2, valinit=init_H, valstep=0.005)
    slider_delta = Slider(ax_delta, 'Delta', 0.0, 0.5, valinit=init_delta, valstep=0.01)

    def update(val):
        L = slider_L.val
        H = slider_H.val
        delta = slider_delta.val
        (Bx, Bz), ctrl_pts = gait_swing(step_length=L, step_height=H, delta=delta)
        line.set_data(Bx, Bz)
        ctrl_scatter.set_offsets(ctrl_pts)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    slider_L.on_changed(update)
    slider_H.on_changed(update)
    slider_delta.on_changed(update)

    plt.show()

if __name__ == "__main__":
    plot_gait()
