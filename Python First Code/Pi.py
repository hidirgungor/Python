from vpython import *
from random import random
import math

f1 = gcurve(color=color.green)
f2 = gcurve(color=color.black)

n = 0
nc = 0
while n<10000:
    rate(1000)
    x = random
    y = random
    r = math.sqrt(x**2 + y**2)
    if r <= 1:
        f1.plot(x,y)
        nc = nc + 1
    else:
        f2.plot(x,y)
    n = n + 1

print("Pi = ", 4.*nc/n)