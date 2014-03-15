import humans

class PlayerCharacter(humans.Human):
    def drop_item(self, slot, history):
        item = humans.Human.drop_item(self, slot)
        history.add("You dropped the %s" % item.name.lower())
        return item
