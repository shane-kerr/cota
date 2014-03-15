import weakref
import random
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
class Human:
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

        # places to store stuff
        self.equip = {
            "head": None,
            "torso": None,
            "cloak": None,
            "left arm": None,
            "right arm": None,
            "left hand": None,
            "right hand": None,
            "left leg": None,
            "right foot": None,
            "left foot": None,
            "right leg": None,
        }
        self.inventory = { }
        self.avail_slots = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for inv_slot in self.avail_slots:
            self.inventory[inv_slot] = None
        self.slot_stability_cache = { }
        self.last_slot_ofs = len(self.avail_slots)-1

        # -- weight limits --
        # We note that a typical legionary would carry 36.5 kg, which is 
        # about 110 libra.
        # Given an average STR of 10 and SIZ of 13, that works out to 
        # about 4.8 libra per (STR+SIZ).
        # Based on this, we'll set our weight limit to (STR+SIZ)*5
        # (Call of Cthulhu doesn't really have limits defined, and 
        # RuneQuest uses the abstract concept of "encumbrance".)
        self.weight_limit = (self.STR + self.SIZ) * 5
        self.weight_carried = 0

    # There are a few algorithms possible for finding the next free slot.
    # First of all, we try to see if the item has the previous slot that
    # it used available and use that.
    # Next, we try to get the next slot (so if we picked "a" last time, we 
    # go for "b")
    def _find_slot(self, item):
        # clear items that have disappeared from the slot stability cache
        items_destroyed = [ ]
        for (uniq_id, slot_item) in self.slot_stability_cache.items():
            [slot, item_ref] = slot_item
            if item_ref() is None:
                items_destroyed.append(uniq_id)
        for uniq_id in items_destroyed:
            del self.slot_stability_cache[uniq_id]
        # now see if our item is in our slot cache, and if that slot is free
        if item.uniq_id in self.slot_stability_cache:
            [slot, item_ref] = self.slot_stability_cache[item.uniq_id]
            if self.inventory[slot] is None:
                return slot
        # if not, we have to find a free slot
        next_slot_ofs = (self.last_slot_ofs + 1) % len(self.avail_slots)
        while next_slot_ofs != self.last_slot_ofs:
            slot = self.avail_slots[next_slot_ofs]
            if self.inventory[slot] is None:
                self.last_slot_ofs = next_slot_ofs
                self.slot_stability_cache[item.uniq_id] = [slot, 
                                                           weakref.ref(item)]
                return slot
            next_slot_ofs = (next_slot_ofs + 1) % len(self.avail_slots)
        # no free slots... bummer
        return None

    def get_item(self, item, history):
        slot = self._find_slot(item)
        if slot is None:
            history.add("No slots available to pick up the %s" % 
                        item.name.lower())
            return False
        if self.weight_carried + item.weight > self.weight_limit:
            history.add("You are already carrying too much weight to pick up the %s" %
                        item.name.lower())
            return False
        self.inventory[slot] = item
        self.weight_carried = self.weight_carried + item.weight
        history.add("You picked up the %s" % item.name.lower() + 
                    " (you can drop or equip from inventory)")
        return True

    def equip_label(self, part):
        if self.equip[part] is None:
            return "nothing"
        else:
            return self.equip[part].name

    def get_inventory(self):
        inv = [ ]
        for slot in self.avail_slots:
            if self.inventory[slot]:
                inv.append((slot, self.inventory[slot]))
        return inv

    def drop_item(self, slot):
        item = self.inventory[slot]
        self.inventory[slot] = None
        self.weight_carried = self.weight_carried - item.weight
        for (equip_place, equip_item) in self.equip.items():
            if item is equip_item:
                self.equip[equip_place] = None
        return item

    def equip_item(self, slot):
        item = self.inventory[slot]
        if item.equip == "1h weapon":
            # unequip 2-handed weapons if used
            if self.equip["left hand"] == self.equip["right hand"]:
                self.equip["left hand"] = None
            self.equip["right hand"] = item
        elif item.equip == "2h weapon":
            self.equip["right hand"] = item
            self.equip["left hand"] = item
        elif item.equip == "shield":
            # unequip 2-handed weapons if used
            if self.equip["left hand"] == self.equip["right hand"]:
                self.equip["right hand"] = None
            self.equip["left hand"] = item
        else:
            assert(False)

class Personality:
    def take_turn(self, human, human_item, history):
        pass

class Martyr(Personality):
    def take_turn(self, human, human_item, history):
        # Somewhat liberally pluked from:
        # http://www.inrebus.com/latinprayers.php
        # Christian prayers are fab-u-tastic
        # Oh, and some Monty Python
        possible_actions = [
            'seems to be praying... "sed libera nos a malo"',
            'spreads his arms and glances at the sky, saying "meus, ex toto corde paenitet me omnium meorum peccatorum"',
            'looks at you and says, "I forgive you your trespasses"',
            'stamps his feet and shouts, "SAN MICHAEL, THRUST INTO HELL THE EVIL SPIRITS WHO PROWL THE WORLD!!!"',
            'whispers something quietly to himself, looking at the ground',
            'seems to be casting a spell, tracing some shapes in the air',
            'chants, "Pie Iesu domine, dona eis requiem"',
            'folds his hands and closes his eyes',
        ]
        if dice.dieN(6) == 1:
            action = random.choice(possible_actions)
            if history:
                history.add("The %s %s" % (human_item.name, action))
