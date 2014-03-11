import weakref

class ItemCollection:
    def __init__(self, next_uniq_id=500000):
        # use a high number as our starting point so item IDs don't 
        # match either speeds or locations on a map, so are easier to spot
        self.next_uniq_id = next_uniq_id
        self.items = weakref.WeakValueDictionary()
    def _next_uniq_id(self, uniq_id):
        if uniq_id is None:
            uniq_id = self.next_uniq_id
            self.next_uniq_id = self.next_uniq_id + 1
        else:
            self.next_uniq_id = max(uniq_id+1, self.next_uniq_id)
        return uniq_id
    def create_item(self, symbol, color, transparent=False, uniq_id=None):
        uniq_id = self._next_uniq_id(uniq_id)
        item = Item(symbol, color, transparent, uniq_id)
        self.items[uniq_id] = item
        return item
    def copy_item(self, item):
        return self.create_item(item.symbol, item.color, item.transparent)
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
                                         uniq_id=item["_id"])
            hold_item.pos = undump_pos(item["pos"])
            hold_items.append(hold_item)
        # we return an array holding the items, because the item collection
        # only holds it weakly
        return hold_items

class Item:
    # TODO: add "blocking" attribute to allow/prevent movement
    def __init__(self, symbol, color, transparent=False, uniq_id=None):
        self.symbol = symbol
        self.color = color
        self.transparent = transparent
        self.pos = None
        self.uniq_id = uniq_id
    def __repr__(self):
        if self.pos:
            pos_str = "(%d,%d)" % pos
        else:
            pos_str = "None"
        return "<Item(%s,%s,%s,%s,%d)>" % (self.symbol, self.color, 
                                    self.transparent, pos_str, self.uniq_id)
    def dump(self):
        return { "symbol": self.symbol, 
                 "color": dump_color(self.color),
                 "transparent": self.transparent, 
                 "pos": dump_pos(self.pos), 
                 "_id": self.uniq_id, } 
    def view(self):
        return (self.symbol, self.color)

