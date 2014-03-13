import textui

def show_keys_help(ui, width, height, keys):
    text_color = ui.color_attr(textui.BLACK, textui.WHITE)
    key_color = ui.color_attr(textui.WHITE, textui.WHITE, textui.BOLD)
    total_len = len("Keys=") + len('/'.join(keys))
    help_col = (width-total_len) // 2
    ui.write(help_col, height-1, "Keys=", text_color)
    help_col = help_col + len("Keys=")
    while len(keys) > 1:
        ui.write(help_col, height-1, keys[0], key_color)
        help_col = help_col + len(keys[0])
        ui.write(help_col, height-1, '/', text_color)
        help_col = help_col + 1
        keys = keys[1:]
    ui.write(help_col, height-1, keys[0], key_color)

def main_display(ui, width, height, view, pc, history):
    # show the map
    for x in range(33):
        for y in range(17):
            (c, a) = view[x][y]
            ui.write(x+1, y+1, c, ui.color_attr(a[0], a[1], a[2]))


    # show the basic stats
    ui.write(38, 2, "STR: %2d" % pc.STR)
    ui.write(38, 3, "CON: %2d" % pc.CON)
    ui.write(38, 4, "DEX: %2d" % pc.DEX)
    ui.write(38, 5, "SIZ: %2d" % pc.SIZ)
    ui.write(38, 6, "INT: %2d" % pc.INT)
    ui.write(38, 7, "POW: %2d" % pc.POW)
    ui.write(38, 8, "APP: %2d" % pc.APP)
    ui.write(38, 9, "EDU: %2d" % pc.EDU)

    # derived stats
    ui.write(48, 2, "Sanity: %2d" % pc.Sanity)
    ui.write(48, 3, "Idea:   %2d" % pc.Idea)
    ui.write(48, 4, "Know:   %2d" % pc.Know)
    ui.write(48, 5, "Luck:   %2d" % pc.Luck)

    # and points
    ui.write(48, 7, "HP:     %2d" % pc.HP)
    ui.write(48, 8, "MP:     %2d" % pc.MP)
    ui.write(48, 9, "SP:     %2d" % pc.Sanity)

    # show our key help
    show_keys_help(ui, width, height, 
                   ("Esc", "Up", "Down", "Left", "Right", "i"))

    ui.cursor_position(17, 9)
#    ui.cursor_visible(True)
