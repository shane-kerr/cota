import random

random.seed(a=1)

def dieN(sides):
    return random.randint(1, sides)

def roll(n, sides, plus=0):
    total = 0
    for m in range(n):
        total = total + dieN(sides)
    return total + plus

