import textwrap

import textui
import keymap
import display
import items
import grid
import history
import humans

PLAYER_COLOR=(textui.YELLOW, textui.BLACK, textui.BOLD)
NPC_COLOR=(textui.RED, textui.BLACK, textui.BOLD)

def get_slot_ranges(inv):
    """get the slot ranges, so if we have items "a", "b", and "d", 
    we get ("a-b", "d")
    """
    if not inv:
        return ( )
    inv.sort()
    ranges = [ ]
    range_start = inv[0][0]
    range_end = range_start
    inv = inv[1:]
    while inv:
        slot = inv[0][0]
        if ord(range_end)+1 == ord(slot):
            range_end = slot
        else:
            if range_start == range_end:
                ranges.append(range_start)
            else:
                ranges.append(range_start + "-" + range_end)
            range_start = slot
            range_end = slot
        inv = inv[1:]
    if range_start == range_end:
        ranges.append(range_start)
    else:
        ranges.append(range_start + "-" + range_end)
    return tuple(ranges)

def item_view(ui, item):
    border_attr = ui.color_attr(textui.BLACK, textui.BLUE)
    view_attr = ui.color_attr(textui.WHITE, textui.BLUE, textui.BOLD)
    shadow_attr = ui.color_attr(textui.BLACK, textui.BLACK)
    while True:
        textui.wait_for_minimum_size(ui, 80, 24)
        (width, height) = ui.get_screen_size()

        item_wid = (width * 3) // 4
        item_col = (width - item_wid) // 2
        item_hig = (height * 3) // 4
        item_row = (height - item_hig) // 2
        item_row_max = item_row + item_hig

        ui.write(item_col, item_row, 
            "+" + ("-"*(item_wid-2)) + "+", border_attr)
        ui.write(item_col, item_row+1,
            "|" + (" "*(item_wid-2)) + "|", border_attr)
        ui.write(item_col+1, item_row+1, 
            item.name.center(item_wid-2), view_attr)
        ui.write(item_col+item_wid, item_row+1, "  ", shadow_attr)
        ui.write(item_col, item_row+2, 
            "+" + ("-"*(item_wid-2)) + "+", border_attr)
        ui.write(item_col+item_wid, item_row+2, "  ", shadow_attr)
        item_row = item_row + 3

        desc_lines = textwrap.wrap(item.desc, item_wid-4)
        while item_row < (item_hig-1):
            if desc_lines:
                txt = desc_lines[0]
                desc_lines = desc_lines[1:]
            else:
                txt = ''
            ui.write(item_col, item_row, 
                "|" + (" " * (item_wid-2)) + "|", border_attr)
            ui.write(item_col+2, item_row, txt.ljust(item_wid-4), view_attr)
            ui.write(item_col+item_wid, item_row, "  ", shadow_attr)
            item_row = item_row + 1

        label = " Keys=Esc/d/e "
        ui.write(item_col, item_row, 
            "+" + ("-" * (item_wid-2)) + "+", border_attr)
        ui.write((width-len(label)) // 2, item_row, label, border_attr)
        ui.write(((width-len(label)) // 2) + 6, item_row, "Esc/d/e", view_attr)
        ui.write(((width-len(label)) // 2) + 9, item_row, "/", border_attr)
        ui.write(((width-len(label)) // 2) + 11, item_row, "/", border_attr)
        ui.write(item_col+item_wid, item_row, "  ", shadow_attr)
        ui.write(item_col+2, item_row+1, " " * item_wid, shadow_attr)

        event = ui.get_input()
        if event is None:
            pass
        elif event.event_type == "keyboard":
            if event.key == textui.KEY_ESC:
                return None
            elif event.key == ord('d'):
                return "drop"
            elif event.key == ord('e'):
                return "equip"
        elif event.event_type == "resize":
            # we get a slightly ugly screen if we resize, but then we
            # don't have to redraw the underlying information
            ui.clear()

def eq_col(ui, s):
    if s == "nothing":
        return ui.color_attr(textui.BLACK, textui.WHITE)
    else:
        return ui.color_attr(textui.WHITE, textui.WHITE, textui.BOLD)

def inventory(ui, pc, inv_ofs, player_history):
    # TODO: truncate names in case we get very long item names
    ui.clear()
    dropped_items = [ ]
    while True:
        textui.wait_for_minimum_size(ui, 80, 24)
        (width, height) = ui.get_screen_size()

        # show our equipment
        equip_col = (width - 80) // 2
        ui.write(equip_col, 0, "+" + ("-" * 78) + "+")
        label = "=[ Equipment ]="
        ui.write((width - len(label)) // 2, 0, label)
        ui.write(equip_col, 1, "|       head: ")
        part = pc.equip_label("head")
        ui.write(equip_col+14, 1, part.ljust(64), eq_col(ui, part))
        ui.write(equip_col+79, 1, "|")
        torso = pc.equip_label("torso")
        cloak = pc.equip_label("cloak")
        if torso == "nothing":
            body = cloak
        elif cloak == "nothing":
            body = torso
        else:
            body = torso + ", " + cloak
        ui.write(equip_col, 2, "|      torso: %s |" % body.ljust(64))
        ui.write(equip_col, 3, "+" + ("-" * 38) + "+" + ("-" * 39) + "+")
        ui.write(equip_col, 4, "|   left arm: %s | %s :right arm  |" % (
            pc.equip_label("left arm").ljust(24),
            pc.equip_label("right arm").rjust(25)))
        ui.write(equip_col, 5, "|  left hand: %s | %s :right hand |" % (
                (" " * 24), (" " * 25)))
        part = pc.equip_label("left hand")
        ui.write(equip_col+14, 5, part.ljust(24), eq_col(ui, part))
        part = pc.equip_label("right hand")
        ui.write(equip_col+41, 5, part.rjust(25), eq_col(ui, part))
        ui.write(equip_col, 6, "|   left leg: %s | %s :right leg  |" % (
            pc.equip_label("left leg").ljust(24),
            pc.equip_label("right leg").rjust(25)))
        ui.write(equip_col, 7, "|  left foot: %s | %s :right foot |" % (
            pc.equip_label("left foot").ljust(24),
            pc.equip_label("right foot").rjust(25)))
        ui.write(equip_col, 8, "+" + ("-" * 38) + "+" + ("-" * 39) + "+")

        # show our inventory
        slots_used = [ ]
        ui.write(0, 9, "+" + ("-" * (width-2)) + "+")
        label = "=[ Inventory ]="
        ui.write((width - len(label)) // 2, 9, label)

        inv_win_size = height - 12
        inv = pc.get_inventory()
        inv_size = len(inv)
        key_ranges = get_slot_ranges(inv)
        inv_by_slot_chr = {}
        for (slot, item) in inv:
            inv_by_slot_chr[ord(slot)] = item

        # fix up our offset if necessary
        inv_ofs = min(inv_ofs, inv_size - inv_win_size)
        inv_ofs = max(inv_ofs, 0)

        inv = inv[inv_ofs:]
        row = 10
        while row < height-2:
            if inv:
                (slot, item) = inv[0]
                inv = inv[1:]
                ui.write(0, row, "| %s - %s |" %
                                  (slot, item.name.ljust(width-8)))
                slots_used.append(slot)
            else:
                ui.write(0, row, "|" + (" " * (width-2)) + "|")
            row = row + 1
        msg = "[ %2d more above / %2d more below ]" % (inv_ofs, len(inv))
        ui.write(0, height-2, "+-" + msg + ("-" * (width-len(msg)-3)) + "+")
    
        disabled = [ ]
        if inv_ofs == 0:
            disabled.append("Up")
        if (inv_size - inv_win_size) <= inv_ofs:
            disabled.append("Down")
        display.show_keys_help(ui, width, height, 
                               ("Esc", "Up", "Down") + key_ranges, disabled)
        event = ui.get_input()
        if event is None: 
            pass
        elif event.event_type == "keyboard":
            if event.key == textui.KEY_ESC:
                return [ inv_ofs, dropped_items ]
            elif event.key == textui.KEY_UP:
                inv_ofs = max(0, inv_ofs-1)
            elif event.key == textui.KEY_DOWN:
                if (inv_size - inv_win_size) > inv_ofs:
                    inv_ofs = inv_ofs + 1
            elif event.key in inv_by_slot_chr:
                ui.write(0, height-1, " " * (width-1))
                action = item_view(ui, inv_by_slot_chr[event.key])
                ui.clear()
                if action == "drop":
                    item = pc.drop_item(chr(event.key), player_history)
                    dropped_items.append(item)
                elif action == "equip":
                    pc.equip_item(chr(event.key))
        elif event.event_type == "resize":
            ui.clear()
            (width, height) = ui.get_screen_size()

school_map = """
+------------------------------------------------------------------------------+
|                                                                              |
|                                        +----+-------+---------------+----+   |
|                                        |    |       |               |    |   |
|                                        |    D       |               D    |   |
|                                        |    |       |               |    |   |
|                                        |    +---D---+------D--------+----+   |
|                                        |    |                       |    |   |
|                                        |    |                       |    |   |
+                                      +-+----+                       |    |   |
|                                      D D                            D    |   |
+                                      +-+----+                       |    |   |
|                                        |    |                       |    |   |
|                                        |    |                       |    |   |
|                                        |    |                       |    |   |
|                                        |    |                       |    |   |
|    +-----------+                       +--+-+--------+  +-----------+-D--+   |
|    |           |                       |  |                         |    |   |
|    |           +                       |  D                         |    |   |
|    |                                   |  |                         |    |   |
|    +D+D+D+D+   +                       +--+-------------------------+----+   |
|    | | | | |   |                                                             |
|    +-+-+-+-+---+                                                             |
+------------------------------------------------------------------------------+
"""

def apply_school_map(m, stuff):
    global school_map

    txt = school_map.strip()
    rows = txt.split("\n")
    for y in range(len(rows)):
        for x in range(len(rows[y])):
            if rows[y][x] in "+-|":
                wall = stuff.create_item('#', grid.WALL_COLOR)
                m.drop_item_at(wall, x, y)
            elif rows[y][x] == 'D':
                wall = stuff.create_item('+', grid.DOOR_COLOR, blocking=False,
                                         name="door", movable=False)
                m.drop_item_at(wall, x, y)

def human_list(items):
    if len(items) == 0:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return items[0] + " and " + items[1]
    else:
        return ", ".join(items[0:-1]) + ", and " + items[-1]

def school(ui, skill_list, pc):
    ui.clear()
    stuff = items.ItemCollection(items.ItemDefinitions(skill_list))
    m = grid.Map(80, 24, stuff)
    apply_school_map(m, stuff)
    mm = grid.MapMemory(m)

    player = stuff.create_item('@', PLAYER_COLOR, True)
    player_x = 2
    player_y = 2

    things_here = m.items_at(player_x, player_y)

    m.drop_item_at(player, player_x, player_y)
    club = stuff.create_item_from_def("club")
    m.drop_item_at(club, 2, 5)
    hasta = stuff.create_item_from_def("hasta")
    m.drop_item_at(hasta, 4, 4)
    sword = stuff.create_item_from_def("short sword")
    m.drop_item_at(sword, 6, 2)
    scutum = stuff.create_item_from_def("scutum")
    m.drop_item_at(scutum, 5, 1)

    john = stuff.create_item('p', NPC_COLOR, transparent=True, name="Christian")
    john_npc = humans.Human()
    john_personality = humans.Martyr()
    m.drop_item_at(john, 7, 4)

    (width, height) = ui.get_screen_size()
    player_history = history.history(width)

    inv_ofs = 0

    while True:
        textui.wait_for_minimum_size(ui, 80, 24)
        (width, height) = ui.get_screen_size()
        h_size = (width - 40) | 1
        h_half = h_size // 2
        v_size = ((height * 2) // 3) | 1
        v_half = v_size // 2
        view = mm.look_at(player_x - h_half, player_y - v_half,
                          player_x + h_half, player_y + v_half, 8)
        display.main_display(ui, width, height, view, pc, player_history)

        # figure out what item we would get if we picked something up
        item_to_get = None
        for n in range(len(things_here)-2, -1, -1):
            if things_here[n].movable:
                item_to_get = n

        disabled = [ ]
        if item_to_get is None:
            disabled.append("g")
        if not m.can_move_onto(player_x, player_y-1):
            disabled.append("Up")
        if not m.can_move_onto(player_x, player_y+1):
            disabled.append("Down")
        if not m.can_move_onto(player_x-1, player_y):
            disabled.append("Left")
        if not m.can_move_onto(player_x+1, player_y):
            disabled.append("Right")
        display.show_keys_help(ui, width, height,
                  ("Esc", "Up", "Down", "Left", "Right", "g", "i"),
                  disabled)

        event = ui.get_input()
        if event is None: continue

        player_moved = False

        new_x = player_x
        new_y = player_y
        if event.event_type == 'keyboard':
            if event.key in keymap.keys_ul:
                new_x = player_x - 1
                new_y = player_y - 1
            elif event.key in keymap.keys_u:
                new_y = player_y - 1
            elif event.key in keymap.keys_ur:
                new_x = player_x + 1
                new_y = player_y - 1
            elif event.key in keymap.keys_l:
                new_x = player_x - 1
            elif event.key in keymap.keys_r:
                new_x = player_x + 1
            elif event.key in keymap.keys_dl:
                new_x = player_x - 1
                new_y = player_y + 1
            elif event.key in keymap.keys_d:
                new_y = player_y + 1
            elif event.key in keymap.keys_dr:
                new_x = player_x + 1
                new_y = player_y + 1
            elif event.key == ord('g'):
                if len(things_here) > 1:
                    # TODO: need a menu of stuff to pick up
                    if item_to_get is not None:
                        if pc.get_item(things_here[item_to_get],
                                       player_history):
                            m.pickup_item(things_here[item_to_get])
                        player_moved = True
            elif event.key == ord('i'):
                [ inv_ofs, drops ] = inventory(ui, pc, inv_ofs, player_history)
                for item in drops:
                    m.drop_item_at(item, player_x, player_y)
                m.pickup_item(player)
                m.drop_item_at(player, player_x, player_y)
                ui.clear()
            elif event.key == textui.KEY_ESC:
                return
        elif event.event_type == 'resize':
            ui.clear()
        if m.can_move_onto(new_x, new_y):
            m.pickup_item(player)
            player_x, player_y = new_x, new_y
            things_here = m.items_at(player_x, player_y)
            if things_here:
                thing_str = map(lambda t: "a " + t.name.lower(), things_here)
                player_history.add("You see " + human_list(list(thing_str)) + 
                                   " here")
            m.drop_item_at(player, player_x, player_y)
            player_moved = True

        # if the player moved, the non-players can move too
        if player_moved:
            histories = [ ]
            if grid.item_in_view(john, view):
                histories.append(player_history)
            john_personality.take_turn(john_npc, john, histories)

