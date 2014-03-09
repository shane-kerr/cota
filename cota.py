import sys
import random
import textwrap
import textui

class dialog:
    def __init__(self, filename="dialog.txt"):
        self.messages = { }
        self.filename = filename
        # TODO: catch missing file and display reasonable message
        f = open(filename, "r")
        line_num = 0
        while True:
            (msg_id, msg_txt, line_num) = self._next_msg(f, line_num)
            if msg_id:
                self.messages[msg_id] = msg_txt
            else:
                break
    def _next_msg(self, f, line_num):
        # skip blank lines
        while True:
            s = f.readline()
            if s == '':
                return (None, None, None)
            line_num = line_num + 1
            if s.strip() != '':
                break
        # first non-blank line is the message identifer... can be anything
        msg_id = s.strip()
        # next line should be '----'
        s = f.readline()
        line_num = line_num + 1
        if s.strip() != '----':
            sys.stderr.write("Badly formatted dialog file \"%s\"; expecting starting '----' on line %d\n" % (self.filename, line_num))
            sys.exit(1)
        # now read everything up to the next '----' as the message
        msg_txt_paragraphs = []
        msg_txt_lines = []
        while True:
            s = f.readline()
            if s == '':
                sys.stderr.write("Badly formatted dialog file \"%s\"; no ending '----' for message \"%s\"\n" % (self.filename, msg_id))
                sys.exit(1)
            line_num = line_num + 1
            if s.strip() == '----':
                msg_txt_paragraphs.append(' '.join(msg_txt_lines))
                break
            # separate paragraphs by blank lines; we need to do this in 
            # order to handle word wrap and the like properly on 
            # variable-sized terminals
            if s.strip() == '':
                msg_txt_paragraphs.append(' '.join(msg_txt_lines))
                msg_txt_lines = []
            else:
                msg_txt_lines.append(s.strip())
        return (msg_id, msg_txt_paragraphs, line_num)

# sets of keys
# we support the arrow keys, vi-keys, numpad keys, and WASD
keys_u = (textui.KEY_UP,    ord('k'), ord('8'), ord('w'))
keys_d = (textui.KEY_DOWN,  ord('j'), ord('2'), ord('s'))
keys_l = (textui.KEY_LEFT,  ord('h'), ord('4'), ord('a'))
keys_r = (textui.KEY_RIGHT, ord('l'), ord('6'), ord('d'))

class button:
    def __init__(self, ui, label, attr):
        self.ui = ui
        self.label = label
        self.attr = attr
        self.selected = False
    def show(self, x, y):
        if self.selected:
            self.ui.write(x, y, " >" + self.label + "< ", self.attr)
        else:
            self.ui.write(x, y, "  " + self.label + "  ", self.attr)

# Scroll design found here:
#     http://www.retrojunkie.com/asciiart/misc/scrolls.htm
#  ,----------------------------------------------------------,==.
# /                                                          /__  \
# \                                                          |(_\ /
# /                                                          \-`-'
# >                                                          /
# }                                                          }
# |                                                          \
# \                                                          /
# }                                                          {
# \                                                          /
# }                                                          >
# |                                                          {____
# }                                                          |__( \
# \                                                          \    /
#  `----------------------------------------------------------`=='
scroll_top_left = [ 
    r" ,-",
    r"/  ",
    r"\  ",
    r"/  " ,
]
scroll_top_right = [
    "-,==. ",
    "/__  \\",
    "|(_\ /",
    "\-`-' ",
]
scroll_bottom_left = [
    "|  ",
    "}  ",
    "\\  ",
    " `-",
]
scroll_bottom_right = [
    "{____ ",
    "|__( \\",
    "\    /",
    "-`==' ",
]

# initialize our scroll edges
scroll_side_rough_edges = "/>{}|\\"
scroll_left_edges = [ random.choice(scroll_side_rough_edges) ]
scroll_right_edges = [ random.choice(scroll_side_rough_edges) ]
for n in range(500):    # hopefully we won't ever have more than 500 lines...
    c = scroll_left_edges[-1]
    while c == scroll_left_edges[-1]:
        c = random.choice(scroll_side_rough_edges)
    scroll_left_edges.append(c)
    c = scroll_right_edges[-1]
    while c == scroll_right_edges[-1]:
        c = random.choice(scroll_side_rough_edges)
    scroll_right_edges.append(c)

# TODO: make scroll get bigger/smaller on top/bottom
def dialog_scroll(ui, text):
    """show some dialog in a scroll"""
    text_ofs = 0
    ui.cursor_visible(False)
    but_up = button(ui, " Up ", 
                ui.color_attr(textui.BLACK, textui.WHITE, textui.NORMAL))
    but_down = button(ui, "Down", 
                ui.color_attr(textui.BLACK, textui.WHITE, textui.NORMAL))
    but_down.selected = True
    # convert our text to wrapped text
    (width, height) = ui.get_screen_size()
    lines = textwrap.wrap(text[0], width-13)
    for paragraph in text[1:]:
       lines.append("")
       lines.extend(textwrap.wrap(paragraph, width-13))
    refresh = True
    while True:
        if refresh:
            ui.set_default_color_attr(textui.YELLOW, textui.YELLOW, textui.BOLD)
            ui.clear()
            (width, height) = ui.get_screen_size()
            # show the top
            wid_l = len(scroll_top_left[0])
            wid_r = len(scroll_top_right[0])
            wid_m = width - (wid_l + wid_r) - 1
            n = 0
            for txt in scroll_top_left:
                ui.write(1, n, txt)
                n = n + 1
            n = 0
            for txt in scroll_top_right:
                ui.write(width-len(txt)-1, n, txt)
                n = n + 1
            ui.write(wid_l, 0, ("-" * wid_m))
            # display the sides
            side_rough_edges = "/>{}|\\"
            ofs = len(scroll_top_left)
            for n in range(height-ofs-len(scroll_bottom_left)):
                ui.write(1, ofs+n, scroll_left_edges[n])
                ui.write(width-7, ofs+n, scroll_right_edges[n])
            # display the bottom
            wid_l = len(scroll_bottom_left[0])
            wid_r = len(scroll_bottom_right[0])
            wid_m = width - (wid_l + wid_r) - 1
            n = 0
            for txt in scroll_bottom_left:
                ui.write(1, height-len(scroll_bottom_left)+n, txt)
                n = n + 1
            n = 0
            for txt in scroll_bottom_right:
                ui.write(width-len(txt)-1, 
                         height-len(scroll_bottom_right)+n, txt)
                n = n + 1
            ui.write(wid_l, height-1, "-" * wid_m)
            # display the text
            ui.set_default_color_attr(textui.BLACK, textui.YELLOW, 
                                      textui.NORMAL)
            n = 0
            while ((n+text_ofs) < len(lines)) and ((n+2) < (height-4)):
                ui.write(4, n+2, lines[n+text_ofs])
                n = n + 1
            refresh = False

        # display our buttons
        visible_range = height - 6
        max_text_ofs = len(lines) - visible_range
        if text_ofs > 0:
            but_up.show(width-27, height-3)
        else:
            ui.write(width-27, height-3, "        ")
        if text_ofs < max_text_ofs:
            text_done = False
            but_down.label = "Down"
        else:
            text_done = True
            but_down.label = "DONE"
        but_down.show(width-17, height-3)
        # read input
        ui.cursor_position(width-1, height-1)
        input_event = ui.get_input()
        if input_event.event_type == "keyboard":
            if but_down.selected and input_event.key in (textui.KEY_ENTER,
                                                         ord(' ')):
                if text_done:
                    break
                else:
                    text_ofs = text_ofs + 1
                    ui.scroll_up(4, 2, width-9, height-5)
                    ui.write(4, height-5, lines[text_ofs+height-7])
            if input_event.key == textui.KEY_PGDN:
                new_text_ofs = min(text_ofs + (visible_range-2), max_text_ofs)
                text_ofs_diff = new_text_ofs - text_ofs
                for n in range(text_ofs_diff):
                    text_ofs = text_ofs + 1
                    ui.scroll_up(4, 2, width-9, height-5)
                    ui.write(4, height-5, lines[text_ofs+height-7])
            elif input_event.key in keys_d:
                if not text_done:
                    text_ofs = text_ofs + 1
                    ui.scroll_up(4, 2, width-9, height-5)
                    ui.write(4, height-5, lines[text_ofs+height-7])
            elif input_event.key == textui.KEY_PGUP:
                new_text_ofs = max(text_ofs - (visible_range-2), 0)
                text_ofs_diff = text_ofs - new_text_ofs
                for n in range(text_ofs_diff):
                    text_ofs = text_ofs - 1
                    ui.scroll_down(4, 2, width-9, height-5)
                    ui.write(4, 2, lines[text_ofs])
                if text_ofs == 0:
                    but_up.selected = False
                    but_down.selected = True
            elif (input_event.key in keys_u) or \
                 (input_event.key in (textui.KEY_ENTER, ord(' ')) and \
                 but_up.selected):
                if text_ofs > 0:
                    text_ofs = text_ofs - 1
                    ui.scroll_down(4, 2, width-9, height-5)
                    ui.write(4, 2, lines[text_ofs])
                if text_ofs == 0:
                    but_up.selected = False
                    but_down.selected = True
            elif input_event.key == ord('\t'):
                if text_ofs > 0:
                    but_up.selected = not but_up.selected
                    but_down.selected = not but_down.selected
            elif input_event.key in keys_l:
                if text_ofs > 0:
                    but_up.selected = True
                    but_down.selected = False
            elif input_event.key in keys_r:
                if text_ofs > 0:
                    but_up.selected = False
                    but_down.selected = True
        elif input_event.event_type == "mouse" and input_event.left_click():
            if (width - 17 <= input_event.x <= width - 10) and \
               (input_event.y == height-3):
                if text_done:
                    break
                else:
                    text_ofs = text_ofs + 1
                    ui.scroll_up(4, 2, width-9, height-5)
                    ui.write(4, height-5, lines[text_ofs+height-7])
                    but_up.selected = False
                    but_down.selected = True
            elif (width - 27 <= input_event.x <= width - 20) and \
                 (input_event.y == height-3):
                if text_ofs > 0:
                    text_ofs = text_ofs - 1
                    ui.scroll_down(4, 2, width-9, height-6)
                    ui.write(4, 2, lines[text_ofs])
                if text_ofs > 0:
                    but_up.selected = True
                    but_down.selected = False
                else:
                    but_up.selected = False
                    but_down.selected = True
            but_up.show(width-27, height-3)
        elif input_event.event_type == "resize":
            refresh = True

class game:
    def __init__(self, debug_log=None):
        self.dialog = dialog()
        self.debug_log = debug_log
    def dbg(self, msg):
        if self.debug_log:
            self.debug_log.write(msg)


def main_loop(ui, g):
    ui.clear()
    dialog_scroll(ui, g.dialog.messages["welcome"])

if __name__ == "__main__":
    g = game(debug_log=open("cota.log", "w"))
    textui.invoke(main_loop, g)
    
