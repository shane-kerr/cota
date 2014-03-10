import dice

class Skills:
    def __init__(self, filename="skills.txt"):
        self.names = [ ]        # ordered list of names
        self.defaults = { }     # default skill level for each skill
        lines = open(filename).readlines()
        for line in lines:
            line = line.strip()
            # skip empty and blank lines
            if line == '': continue
            if line.startswith('#'): continue
            # field separator
            if line == "---": 
                self.names.append(line)
                continue
            # split off default from skill name
            parts = line.split()
            default = parts[-1]
            name = ' '.join(parts[:-1])
            self.names.append(name)
            self.defaults[name] = default

# Using p.63 of Cthulhu Invictus for character creation
# ignore aging (assume all characters between 18 and 28)
class PlayerCharacter:
    def __init__(self):
        self.STR = dice.roll(3, 6)
        self.CON = dice.roll(3, 6)
        self.DEX = dice.roll(3, 6)
        self.SIZ = dice.roll(2, 6, 6)
        self.INT = dice.roll(2, 6, 6)
        self.POW = dice.roll(3, 6)
        self.APP = dice.roll(3, 6)
        self.EDU = dice.roll(3, 6, 3)
        
        self.Sanity = self.POW * 5
        self.Idea = self.INT * 5
        self.Know = self.EDU * 5
        self.Luck = self.POW * 5

        self.HP = (self.CON + self.SIZ + 1) // 2
        self.MP = self.POW
        self.SP = self.Sanity

        self.skill_defaults = { }
        self.skills_started = { }
        self.skills_added = { }
        self.skill_levels = { }

        # we'll treat this specially...
        self.cthulhu_mythos = 0

#if __name__ == "__main__":
#  import pprint
#  skills = Skills()
#  pprint.pprint(skills.names)
#  pprint.pprint(skills.defaults)

