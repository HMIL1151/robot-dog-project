import math
import numpy as np

a = 7
d = 20
y = 20
z = 18

q = d/2 - z

theta_l = math.radians(120)


b = -2*a*math.cos(theta_l)
c = math.pow(a, 2) - math.pow(y, 2) - math.pow(q, 2)

roots = np.roots([1, b, c])

positive_roots = roots[roots > 0]
if positive_roots.size == 0:
    raise ValueError("No positive roots found")
y_prime = float(positive_roots[0])
print(f"y_prime: {y_prime:.2f}")

v = math.sqrt(math.pow(y, 2) + math.pow(q, 2))
if z < d/2:
    theta_a_prime = math.atan(y/q)
elif z > d/2:
    theta_a_prime = math.atan((z-d/2)/y) + math.pi/2
else:
    theta_a_prime = math.pi/2
theta_a_prime_prime = math.acos((math.pow(a, 2) + math.pow(v, 2) - math.pow(y_prime, 2)) / (2*a*v))
theta_a = theta_a_prime + theta_a_prime_prime

f = math.sqrt(math.pow(q, 2) + math.pow(a, 2) - 2*a*q*math.cos(theta_a))
theta_h = math.acos((math.pow(y, 2) + math.pow(y_prime, 2) - math.pow(f, 2)) / (2*y*y_prime))

if z > (d/2 + a*math.sin(math.pi - theta_l)):
    theta_h = -theta_h
elif z < (d/2 + a*math.sin(math.pi - theta_l)):
    theta_h = theta_h
else:
    theta_h = 0
    
print(f"theta_h: {math.degrees(theta_h):.2f}")