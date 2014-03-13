import weakref
import dice
import colors

class ItemDefinitions:
    def __init__(self, skill_list, filename="items.txt"):
        self.defs = { }

        f = open(filename, "r")
        # TODO: catch exceptions on open
        contents = f.read()
        for item_def_info in contents.strip().split("\n\n"):
            item_def_info = item_def_info.strip()
            item_attrs = { }
            attrs, desc = item_def_info.split("---\n")
            for attr in attrs.strip().split("\n"):
                attr_name, attr_val = attr.split(":", 1)
                attr_name = attr_name.strip().lower()
                if attr_name == "name":
                    item_attrs["name"] = attr_val.strip()
                elif attr_name == "weight":
                    weight_amt, weight_type = attr_val.split()
                    assert(weight_type == "libra")
                    item_attrs["weight"] = float(weight_amt)
                elif attr_name == "skill":
                    item_attrs["skill"] = [ ]
                    for skill_name in attr_val.split(","):
                        skill_name = skill_name.strip()
                        assert(skill_name in skill_list.defaults)
                        item_attrs["skill"].append(skill_name)
                elif attr_name == "www":
                    pass
                elif attr_name == "damage":
                    item_attrs["damage"] = { }
                    for damage in attr_val.split(","):
                        damage = damage.strip()
                        if damage == "entangle":
                            item_attrs["damage"]["entangle"] = True
                        else:
                            damage_amt, damage_type = damage.split()
                            assert(damage_type in ("impale", "crush", "cut"))
                            item_attrs["damage"][damage_type] = \
                                dice.die(damage_amt)
                elif attr_name == "equip":
                    item_attrs["equip"] = [ ]
                    for equip in attr_val.split(","):
                        equip = equip.strip()
                        assert(equip in ("1h weapon", "2h weapon", "hands"))
                        item_attrs["equip"].append(equip)
                elif attr_name == "symbol":
                    attr_val = attr_val.strip()
                    assert(len(attr_val) == 1)
                    item_attrs["symbol"] = attr_val
                elif attr_name == "color":
                    item_attrs["color"] = colors.parse_color(attr_val)
                else:
                    # unknown item attribute... probably a misspelling
                    assert(False)
            item_attrs["descr"] = ' '.join(desc.split("\n"))
            self.defs[item_attrs["name"].lower()] = item_attrs

class ItemCollection:
    def __init__(self, item_defs, next_uniq_id=500000):
        # use a high number as our starting point so item IDs don't 
        # match either speeds or locations on a map, so are easier to spot
        self.next_uniq_id = next_uniq_id
        self.item_defs = item_defs
        self.items = weakref.WeakValueDictionary()
    def _next_uniq_id(self, uniq_id):
        if uniq_id is None:
            uniq_id = self.next_uniq_id
            self.next_uniq_id = self.next_uniq_id + 1
        else:
            self.next_uniq_id = max(uniq_id+1, self.next_uniq_id)
        return uniq_id
    def create_item_from_def(self, def_name):
        attrs = self.item_defs.defs[def_name.lower()]
        return self.create_item(attrs["symbol"], attrs["color"], 
                                transparent=True, blocking=False, 
                                name=attrs["name"])
    def create_item(self, symbol, color, 
                          transparent=False, blocking=True, uniq_id=None,
                          name=None):
        uniq_id = self._next_uniq_id(uniq_id)
        item = Item(symbol, color, transparent, blocking, uniq_id, name=name)
        self.items[uniq_id] = item
        return item
    def copy_item(self, item):
        return self.create_item(item.symbol, item.color, 
                                item.transparent, item.blocking)
    def dump(self):
        items = [ ]
        for item in self.items.values():
            items.append(item.dump())
        return { "next_uniq_id": self.next_uniq_id, "items": items }
    def item_by_id(self, uniq_id):
        return self.items[uniq_id]
    def undump_items(self, items_info):
        hold_items = [ ]
        for item in items_info:
            hold_item = self.create_item(symbol=item["symbol"],
                                         color=undump_color(item["color"]),
                                         transparent=item["transparent"],
                                         blocking=item["blocking"],
                                         uniq_id=item["_id"])
            hold_item.pos = undump_pos(item["pos"])
            hold_items.append(hold_item)
        # we return an array holding the items, because the item collection
        # only holds it weakly
        return hold_items

class Item:
    def __init__(self, symbol, color, 
                       transparent=False, blocking=True, uniq_id=None,
                       name=None):
        self.symbol = symbol
        self.color = color
        self.transparent = transparent
        self.blocking = blocking
        self.pos = None
        self.uniq_id = uniq_id
        self.name = name
    def __repr__(self):
        if self.pos:
            pos_str = "(%d,%d)" % self.pos
        else:
            pos_str = "None"
        return "<Item('%s',%s,%s,%s,%s,%d)>" % (self.symbol, self.color,
                                    self.transparent, self.blocking, 
                                    pos_str, self.uniq_id)
    def dump(self):
        return { "symbol": self.symbol, 
                 "color": dump_color(self.color),
                 "transparent": self.transparent, 
                 "blocking": self.blocking,
                 "name": self.name, 
                 "pos": dump_pos(self.pos), 
                 "_id": self.uniq_id, } 
    def view(self):
        return (self.symbol, self.color)


if __name__ == "__main__":
    import playerchar

    skill_list = playerchar.Skills()
    item_defs = ItemDefinitions(skill_list)
    print(item_defs.defs.keys())
