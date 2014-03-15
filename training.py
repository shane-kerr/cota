import textwrap

import textui
import keymap
import display
import items
import grid
import history
import humans
import combat
import background

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
        # head
        ui.write(equip_col, 1, "|       head: ")
        part = pc.equip_label("head")
        ui.write(equip_col+14, 1, part.ljust(64), eq_col(ui, part))
        ui.write(equip_col+79, 1, "|")
        # body
        torso = pc.equip_label("torso")
        cloak = pc.equip_label("cloak")
        if torso == "nothing":
            body = cloak
        elif cloak == "nothing":
            body = torso
        else:
            body = torso + ", " + cloak
        ui.write(equip_col, 2, "|      torso: %s |" % (" " * 64))
        ui.write(equip_col+14, 2, body, eq_col(ui, body))
        ui.write(equip_col, 3, "+" + ("-" * 38) + "+" + ("-" * 39) + "+")
        ui.write(equip_col, 4, "|   left arm: %s | %s :right arm  |" % (
            pc.equip_label("left arm").ljust(24),
            pc.equip_label("right arm").rjust(25)))
        # weapon
        ui.write(equip_col, 5, "|  left hand: %s | %s :right hand |" % (
                (" " * 24), (" " * 25)))
        part = pc.equip_label("left hand")
        ui.write(equip_col+14, 5, part, eq_col(ui, part))
        part = pc.equip_label("right hand")
        ui.write(equip_col+41, 5, part.rjust(25), eq_col(ui, part))
        ui.write(equip_col, 6, "|   left leg: %s | %s :right leg  |" % (
            pc.equip_label("left leg").ljust(24),
            pc.equip_label("right leg").rjust(25)))
        # footwear
        ui.write(equip_col, 7, "|  left foot: %s | %s :right foot |" % (
            " " * 24, " " * 25))
        part = pc.equip_label("left foot")
        ui.write(equip_col+14, 7, part, eq_col(ui, part))
        part = pc.equip_label("right foot")
        ui.write(equip_col+41, 7, part.rjust(25), eq_col(ui, part))
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

def die_at(victim, m, x, y, history):
    victim.human_item.symbol = '%'
    victim.human_item.name = 'body of a ' + victim.human_item.name
    victim.human_item.weight = victim.human_info.SIZ * 20
    # XXX: for now we don't pick up bodies
    victim.human_item.movable = False
    for item in victim.human_info.get_inventory():
        m.drop_item_at(item[1], x, y)

def school(ui, backgrounds, skill_list, pc):
    bg_by_name = { }
    for bg in backgrounds:
        bg_by_name[bg.name] = bg

    ui.clear()
    stuff = items.ItemCollection(items.ItemDefinitions(skill_list))
    m = grid.Map(80, 24, stuff)
    apply_school_map(m, stuff)
    mm = grid.MapMemory(m)


    actors_by_pos = { }

    # add our boss
    npc_body = stuff.create_item('p', (textui.RED, textui.BLACK, textui.NORMAL),
                                 transparent=True, name="Iudictus",
                                 blocking=False)
    npc_stats = humans.Human()
    npc_stats.STR = 14
    npc_stats.CON = 15
    npc_stats.DEX = 14
    npc_stats.SIZ = 15
    npc_stats.compute()
    npc_stats.set_default_skills(bg_by_name["Legionary"], skill_list)
    npc_stats.skill_levels["Dodge"] = 100
    npc_stats.skill_levels["Sword - Short"] = 140
    gladius = stuff.create_item_from_def("gladius")
    npc_stats.equip_item(npc_stats.get_item(gladius))
    tunic = stuff.create_item_from_def("tunic")
    npc_stats.equip_item(npc_stats.get_item(tunic))
    boots = stuff.create_item_from_def("boots")
    npc_stats.equip_item(npc_stats.get_item(boots))
    npc = humans.Observer(npc_stats, npc_body)
    m.drop_item_at(npc.human_item, 8, 12)
    actors_by_pos[(8, 12)] = npc

    # add some Christians
    npc_x = 4
    npc_y = 3
    for name in [ "Matthew", "Mark", ]:
        npc_body = stuff.create_item('p', NPC_COLOR, transparent=True,
                                     name="Christian", blocking=False)
        npc_stats = humans.Human()
        npc_stats.set_default_skills(bg_by_name["Christian"], skill_list)
        toga = stuff.create_item_from_def("toga")
        npc_stats.equip_item(npc_stats.get_item(toga))
        sandals = stuff.create_item_from_def("sandals")
        npc_stats.equip_item(npc_stats.get_item(sandals))
        npc = humans.Martyr(npc_stats, npc_body)
        m.drop_item_at(npc.human_item, npc_x, npc_y)
        actors_by_pos[(npc_x, npc_y)] = npc
        npc_x = npc_x + 2
        npc_y = npc_y + 2

    # add our player
    player = stuff.create_item('@', PLAYER_COLOR, True, blocking=False,
                               name="you")
    player_x = 8
    player_y = 5
    pc.equip_item(pc.get_item(stuff.create_item_from_def("toga")))
    pc.equip_item(pc.get_item(stuff.create_item_from_def("sandals")))
    things_here = m.items_at(player_x, player_y)
    m.drop_item_at(player, player_x, player_y)
    player_actor = humans.Personality(pc, player)
    actors_by_pos[(player_x, player_y)] = player_actor

    (width, height) = ui.get_screen_size()
    player_history = history.history(width)

    # sprinkle some weapons around
    for club_loc in [(4,6), (5,7), (7,6), (8,6), (10,8)]:
        club = stuff.create_item_from_def("club")
        m.drop_item_at(club, club_loc[0], club_loc[1])
    for shield_loc in [(2,6), (3,6), (5,6), (6, 7), (9, 8)]:
        shield = stuff.create_item_from_def("medium shield")
        m.drop_item_at(shield, shield_loc[0], shield_loc[1])

    inv_ofs = 0

    while True:
        player_state = pc.check_health()
        if player_state != "okay":
            return player_state

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
        attack = [ ]
        for (actor_x, actor_y) in actors_by_pos.keys():
            if (actor_x == player_x-1) and (actor_y == player_y):
                attack.append("Left")
            elif (actor_x == player_x+1) and (actor_y == player_y):
                attack.append("Right")
            elif (actor_x == player_x) and (actor_y == player_y-1):
                attack.append("Up")
            elif (actor_x == player_x) and (actor_y == player_y+1):
                attack.append("Down")
        display.show_keys_help(ui, width, height,
                  ("Esc", "Up", "Down", "Left", "Right", "g", "i"),
                  disabled, attack)

        event = ui.get_input()
        if event is None: continue
        if event.event_type == 'resize':
            ui.clear()
            continue
        elif event.event_type == 'mouse':
            continue

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

        # check for bump combat
        del actors_by_pos[(player_x, player_y)]
        if (new_x, new_y) in actors_by_pos:
            victim = actors_by_pos[(new_x, new_y)]
            victim_start_state = victim.human_info.check_health()
            combat.attack(pc, "You", pc.equip["right hand"], 
                          victim.human_info, "the %s" % victim.human_item.name,
                          player_history)
            victim_end_state = victim.human_info.check_health()
            if victim_start_state == "okay":
                if victim_end_state == "dead":
                    player_history.add("The %s dies" % victim.human_item.name)
                    die_at(victim, m, new_x, new_y, player_history)
                    del actors_by_pos[(new_x, new_y)]
                elif victim_end_state == "unconscious":
                    player_history.add("The %s loses consciousness" % 
                                       victim.human_item.name)
            elif victim_start_state == "unconscious":
                if victim_end_state == "dead":
                    player_history.add("The %s dies" % victim.human_item.name)
                    die_at(victim, m, new_x, new_y, player_history)
                    del actors_by_pos[(new_x, new_y)]

            # we don't actually want to move, but we do use a turn
            new_x = player_x
            new_y = player_y
            player_moved = True
        # otherwise move
        elif m.can_move_onto(new_x, new_y):
            m.pickup_item(player)
            player_x, player_y = new_x, new_y
            things_here = m.items_at(player_x, player_y)
            if things_here:
                thing_str = map(lambda t: "a " + t.name.lower(), things_here)
                player_history.add("You see " + human_list(list(thing_str)) + 
                                   " here")
            m.drop_item_at(player, player_x, player_y)
            player_moved = True
        actors_by_pos[(player_x, player_y)] = player_actor

        # if the player moved, the non-players can move too
        if player_moved:
            player.can_parry = True
            player.can_block = True
            player.can_dodge = True
            for actor in actors_by_pos.values():
                if actor is player_actor:
                    continue
                histories = [ ]
                if grid.item_in_view(actor.human_item, view):
                    # TODO: each actor also needs a history...
                    histories.append(player_history)
                if actor.human_info.check_health() == "okay":
                    actor.take_turn(m, actors_by_pos, histories)

