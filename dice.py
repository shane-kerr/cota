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
    def info(self):
        min_roll = (self.n * 1) + self.plus
        avg_roll = (self.n * ((self.sides / 2) + 0.5)) + self.plus
        max_roll = (self.n * self.sides) + self.plus
        return (min_roll, avg_roll, max_roll)
    def __str__(self):
        if self.plus != 0:
            return "%dD%d%+d" % (self.n, self.sides, self.plus)
        else:
            return "%dD%d" % (self.n, self.sides)

