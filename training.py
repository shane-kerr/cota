import textui
import keymap
import display
import items
import grid

PLAYER_COLOR=(textui.RED, textui.BLACK, textui.BOLD)

def school(ui, skill_list, pc):
    ui.clear()
    stuff = items.ItemCollection()
    m = grid.Map(80, 24, stuff)
    m.enclose()
    player = stuff.create_item('@', PLAYER_COLOR, True)
    player_x = 2
    player_y = 2
    m.drop_item_at(player, player_x, player_y)
    (width, height) = ui.get_screen_size()
    while True:
        view = m.view(player_x, player_y, 17, 17, 8)
        display.main_display(ui, width, height, view, pc, [])
        event = ui.get_input()
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
        if m.can_move_onto(new_x, new_y):
            m.pickup_item(player)
            player_x, player_y = new_x, new_y
            m.drop_item_at(player, player_x, player_y)
        

