import textui
import keymap
import display
import items
import grid

PLAYER_COLOR=(textui.YELLOW, textui.BLACK, textui.BOLD)

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
    club = stuff.create_item_from_def("club")
    m.drop_item_at(club, 5, 8)
    (width, height) = ui.get_screen_size()
    while True:
        textui.wait_for_minimum_size(ui, 80, 24)
        (width, height) = ui.get_screen_size()
        h_size = (width - 40) | 1
        h_half = h_size // 2
        v_size = ((height * 2) // 3) | 1
        v_half = v_size // 2
        view = mm.look_at(player_x - h_half, player_y - v_half,
                          player_x + h_half, player_y + v_half, 8)
        display.main_display(ui, width, height, view, pc, [])

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
            elif event.key == 27:
                return
        elif event.event_type == 'resize':
            ui.clear()
        if m.can_move_onto(new_x, new_y):
            m.pickup_item(player)
            player_x, player_y = new_x, new_y
            things_here = m.items_at(player_x, player_y)
            m.drop_item_at(player, player_x, player_y)
        

