import textui
import keymap
import display
import items
import grid
import history

PLAYER_COLOR=(textui.YELLOW, textui.BLACK, textui.BOLD)

def get_slot_ranges(inv):
    """get the slot ranges, so if we have items "a", "b", and "d", 
    we get ("a-b", "d")
    """
    if not inv:
        return ( )
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
        inv = inv[1:]
    if range_start == range_end:
        ranges.append(range_start)
    else:
        ranges.append(range_start + "-" + range_end)
    return tuple(ranges)

def inventory(ui, pc, inv_ofs):
    # TODO: truncate names in case we get very long item names
    ui.clear()
    while True:
        textui.wait_for_minimum_size(ui, 80, 24)
        (width, height) = ui.get_screen_size()

        # show our equipment
        equip_col = (width - 80) // 2
        ui.write(equip_col, 0, "+" + ("-" * 78) + "+")
        label = "=[ Equipment ]="
        ui.write((width - len(label)) // 2, 0, label)
        ui.write(equip_col, 1, "|       head: %s |" % 
                               pc.equip_label("head").ljust(64))
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
            pc.equip_label("left hand").ljust(24),
            pc.equip_label("right hand").rjust(25)))
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
            if event.key == 27:
                return inv_ofs
            elif event.key == textui.KEY_UP:
                inv_ofs = max(0, inv_ofs-1)
            elif event.key == textui.KEY_DOWN:
                if (inv_size - inv_win_size) > inv_ofs:
                    inv_ofs = inv_ofs + 1
            elif event.key in inv_by_slot_chr:
                pass
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
                                         name="door")
                m.drop_item_at(wall, x, y)

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
    for n in range(20):
        club = stuff.create_item_from_def("club")
        m.drop_item_at(club, 2+n, 5)

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

        if len(things_here) > 1:
            disabled = None
        else:
            disabled = ("g")
        display.show_keys_help(ui, width, height,
                  ("Esc", "Up", "Down", "Left", "Right", "g", "i"), disabled)

        event = ui.get_input()
        if event is None: continue

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
                    if pc.get_item(things_here[-2], player_history):
                        m.pickup_item(things_here[-2])
            elif event.key == ord('i'):
                inv_ofs = inventory(ui, pc, inv_ofs)
                ui.clear()
            elif event.key == 27:
                return
        elif event.event_type == 'resize':
            ui.clear()
        if m.can_move_onto(new_x, new_y):
            m.pickup_item(player)
            player_x, player_y = new_x, new_y
            things_here = m.items_at(player_x, player_y)
            for thing in things_here:
                player_history.add('You see a %s here' % thing.name.lower())
            m.drop_item_at(player, player_x, player_y)
        

