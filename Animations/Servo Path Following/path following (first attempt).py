import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def getSinPoints(count: int, range: float) -> tuple[list[float], list[float]]:
    x = np.linspace(0, range, count)
    y = np.cos(x)

    return (x, y)

def getGradient(coord1: tuple[int, int], coord2: tuple[int, int]) -> float:
    x, y = coord1
    x1, y1 = coord2

    m = (y-y1)/(x-x1)
    return m

def isOvershoot(accelDir: int, possNextY: float, nextCurveY: float) -> bool:
    if (accelDir == 1):
        if possNextY > nextCurveY:
            return True
    elif (accelDir == -1):
        if possNextY < nextCurveY:
            return True
    
    return False

def isUndershoot(accelDir: int, possNextY: float, nextCurveY: float) -> bool:
    if (accelDir == 1):
        if possNextY < nextCurveY:
            return True
    elif (accelDir == -1):
        if possNextY > nextCurveY:
            return True
    
    return False
    
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.5)

domain = 2*np.pi
coarseSin = getSinPoints(30, domain)
fineSin = getSinPoints(100, domain)

accelMag = 5
vmax = 1

def getServoLine(accelMag: float, iterations: int) -> tuple[list[float], list[float]]:
    coarseSin = getSinPoints(iterations, domain)
    dt = domain/iterations
    dxMax = vmax*(dt - (vmax/accelMag))
    print()
    print(f'{dxMax=}')


    x=[coarseSin[0][0]]
    y=[coarseSin[1][0]]

    for i in range(1, iterations):
        lastX = x[-1]
        lastY = y[-1]

        possNextX = coarseSin[0][i]
        accelDir = np.sign((coarseSin[1][i] - lastY))
        accel = accelMag * accelDir
        possNextY = lastY - accel*(lastX - possNextX)

        nextY = coarseSin[1][i]
        deltaX = 0
        if isOvershoot(accelDir, possNextY, coarseSin[1][i]):
            nextX = lastX - (lastY-nextY)/(accel)
            x.append(nextX)
            y.append(nextY)
            deltaX = nextX - lastX
            x.append(coarseSin[0][i])
            y.append(nextY)
        elif isUndershoot(accelDir, possNextY, coarseSin[1][i]):
            x.append(possNextX)
            y.append(possNextY)
            deltaX = possNextX - lastX


    return (x,y)
    
(x, y) = getServoLine(accelMag, 10) 
[servoLine] = ax.plot(x, y)
servoScatter = ax.scatter(x, y)
[sinLine] = ax.plot(fineSin[0], fineSin[1], color='red')


accelSliderAx = plt.axes([0.25, 0.12, 0.5, 0.03])
accelSlider = Slider(
    ax=accelSliderAx,
    label='Acceleration',
    valmax=3,
    valmin=0.2,
    valinit=0.5,
)

countSliderAx = plt.axes([0.25, 0.24, 0.5, 0.03])
countSlider = Slider(
    ax=countSliderAx,
    label='Steps',
    valmax=100,
    valmin=10,
    valinit=10,
    valstep=1
)

def update(val):
    accelMag = accelSlider.val
    iterations = countSlider.val
    (newX, newY) = getServoLine(accelMag, iterations)
    servoLine.set_xdata(newX)
    servoLine.set_ydata(newY)
    servoScatter.set_offsets(np.c_[newX, newY])

accelSlider.on_changed(update)
countSlider.on_changed(update)



plt.show()

