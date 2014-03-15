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

def success_roll(skill, r=None):
    if r is None:
        r = dieN(100)
    if skill >= 500:
        if r == 100:
            return "failure"
    else:
        if r == 100:
            return "fumble"
        if skill >= 400:
            if r >= 99:
                return "failure"
        elif skill >= 300:
            if r >= 98:
                return "failure"
        elif skill >= 200:
            if r >= 97:
                return "failure"
        else:
            if r >= 96:
                return "failure"
    if r <= (skill / 10):   # intentionally use real division
        return "critical"
    if r <= 5:
        return "success"
    if r <= skill:
        return "success"
    return "failure"

class die:
    def __init__(self, fmt):
        m = re.match(r'\s*([-+]?\d*)D(\d+)\s*([+-]\s*\d+)?\s*$', fmt, re.IGNORECASE)
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
    def min(self):
        return (self.n * 1) + self.plus
    def avg(self):
        return (self.n * ((self.sides / 2) + 0.5)) + self.plus
    def max(self):
        return (self.n * self.sides) + self.plus
    def __str__(self):
        if self.plus != 0:
            return "%dD%d%+d" % (self.n, self.sides, self.plus)
        else:
            return "%dD%d" % (self.n, self.sides)

