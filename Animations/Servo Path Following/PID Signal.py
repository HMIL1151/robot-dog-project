import numpy as np
import matplotlib.pyplot as plt

import numpy as np

def second_order_step(t, x0, x_target, zeta=0.1, wn=15):
    wd = wn * np.sqrt(1 - zeta**2)
    
    return x_target + (x0 - x_target) * np.exp(-zeta * wn * t) * (
        np.cos(wd * t) + (zeta / np.sqrt(1 - zeta**2)) * np.sin(wd * t)
    )

t = np.linspace(0, 1.9, 100)
signal = second_order_step(t, x0=1.9523, x_target=2.8)

plt.plot(t, signal)
plt.show()