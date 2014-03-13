import random
import re

random.seed(a=1)

def dieN(sides):
    return random.randint(1, sides)

def roll(n, sides, plus=0):
    total = 0
    for m in range(n):
        total = total + dieN(sides)
    return total + plus

class die:
    def __init__(self, fmt):
        m = re.match(r'\s*(\d*)D(\d+)\s*([+-]\s*\d+)?\s*$', fmt, re.IGNORECASE)
        assert(m is not None)
        if m.group(1) == '':
            self.n = 1
        else:
            self.n = int(m.group(1))
        self.sides = int(m.group(2))
        if m.group(3):
            self.plus = int(m.group(3))
        else:
            self.plus = 0
    def roll(self):
        return roll(self.n, self.sides, self.plus)

