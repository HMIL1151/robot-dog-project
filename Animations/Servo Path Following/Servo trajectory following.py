import numpy as np
import matplotlib.pyplot as plt

paddingTime = 1
riseDuration = 4
idleY = 1
targetYval = 5

def dampedReaction(dt, x0, x_target, steps, zeta=0.3, wn=20):
    t = np.linspace(0, dt, steps)

    wd = wn * np.sqrt(1 - zeta**2)
    
    return x_target + (x0 - x_target) * np.exp(-zeta * wn * t) * (
        np.cos(wd * t) + (zeta / np.sqrt(1 - zeta**2)) * np.sin(wd * t)
    )

def getGradientAndIntercept(coords1: tuple[float, float], coords2: tuple[float, float]) -> tuple[float, float]:
    x, y = coords1
    x1, y1 = coords2

    gradient = (y-y1)/(x-x1)
    intercept = y - (gradient * x)

    return (gradient, intercept)

def getY(x: float, coords: list[tuple[float, float], tuple[float, float], tuple[float, float]]) -> float:
    m1, c1 = getGradientAndIntercept(
        coords[0],
        coords[1]
    )
    m2, c2 = getGradientAndIntercept(
        coords[1],
        coords[2]
    )
    x1 = coords[0][0]
    x2 = coords[1][0]
    x3 = coords[2][0]

    if x1 <= x < x2:
        return (m1 * x) + c1
    elif x2 <= x <= x3:
        return (m2 * x) + c2
    else:
        return idleY

    
coords1 = (paddingTime, idleY)
coords2 = (riseDuration + paddingTime, targetYval)
coords3 = (paddingTime + 2*riseDuration, idleY)
coords = (coords1, coords2, coords3)

lineSteps = 100

linesX = np.linspace(0, 2 * (paddingTime + riseDuration), lineSteps)
linesY = []

for i in range(lineSteps):
    linesY.append(getY(linesX[i], coords))


steps = 100
startTime = paddingTime
endTime = 2*(paddingTime + riseDuration)
dt = (endTime - startTime)/steps

squareTargetX = [0]
squareTargetY = [idleY]

for i in range(steps):
    currentTime = paddingTime + (dt*(i))
    lastTime = currentTime - dt
    nextTime = currentTime + dt
    squareTargetX.append(currentTime)
    squareTargetX.append(currentTime)

    currentTargetY = getY(currentTime, coords)
    lastTargetY = getY(lastTime, coords)
    nextTargetY = getY(nextTime, coords)
    

    dir = np.sign(currentTargetY - lastTargetY)
    lastY = squareTargetY[-1]
    squareTargetY.append(currentTargetY)
    squareTargetY.append(nextTargetY)

dampedReactionX = [0, paddingTime]
dampedReactionY = [idleY, idleY]

for i in range(steps):
    currentTime = paddingTime + (dt*(i))
    lastTime = currentTime - dt
    nextTime = currentTime + dt
    lastTargetY = getY(lastTime, coords)
    nextTargetY = getY(nextTime, coords)

    t = np.linspace(currentTime, nextTime, lineSteps)
    response = dampedReaction(dt, dampedReactionY[-1], nextTargetY, lineSteps)


    dampedReactionX = np.concatenate([dampedReactionX, t])
    dampedReactionY =np.concatenate([dampedReactionY, response])


# plt.scatter(squareTargetX, squareTargetY)
plt.plot(squareTargetX, squareTargetY)
plt.plot(linesX, linesY)

print(f'{dampedReactionX.__sizeof__()=}')
print(f'{dampedReactionY.__sizeof__()=}')
plt.plot(dampedReactionX, dampedReactionY)

plt.show()