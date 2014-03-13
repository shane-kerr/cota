import os
import curses
import locale
from textuievents import *

# we only support bold or non-bold attributes
BOLD = curses.A_BOLD
NORMAL = curses.A_NORMAL

# we support the 8 holy TTY colors
BLACK = curses.COLOR_BLACK
BLUE = curses.COLOR_BLUE
CYAN = curses.COLOR_CYAN
GREEN = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
RED = curses.COLOR_RED
WHITE = curses.COLOR_WHITE
YELLOW = curses.COLOR_YELLOW

# defined keys
KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT
KEY_HOME = curses.KEY_HOME
KEY_PGUP = curses.KEY_PPAGE
KEY_END = curses.KEY_END
KEY_PGDN = curses.KEY_NPAGE
KEY_F1 = curses.KEY_F1
KEY_ENTER = ord('\n')

class textui_curses:
    def __init__(self, scr):
        self.scr = scr
        # we keep a cache of color pairs so we don't have to re-initialize
        self.color_pairs = { }
        # white on black is hard-coded as color pair 0 in curses
        self.color_pairs[self._color_hash(WHITE, BLACK)] = 0
        self.next_color_pair = 1
        self.default_color_attr = None
        self.set_default_color_attr(WHITE, BLACK)
        # get our locale encoding (important for Python 2)
        locale.setlocale(locale.LC_ALL, '')
        self.locale_code = locale.getpreferredencoding()
    def _color_hash(self, fg, bg):
        return fg | (bg << 32)
    def color_attr(self, fg=WHITE, bg=BLACK, attr=NORMAL):
        color_hash = self._color_hash(fg, bg)
        if color_hash in self.color_pairs:
            pair = self.color_pairs[color_hash]
        else:
            pair = self.next_color_pair
            self.next_color_pair = self.next_color_pair + 1
            curses.init_pair(pair, fg, bg)
            self.color_pairs[color_hash] = pair
        return curses.color_pair(pair) | attr
    def set_default_color_attr(self, fg=WHITE, bg=BLACK, attr=NORMAL):
        self.default_color_attr = self.color_attr(fg, bg, attr)
    def clear(self):
        self.scr.bkgdset(' ', self.default_color_attr)
        self.scr.clear()
        self.scr.bkgdset(' ', 0)
    def write(self, x, y, s, color_attr=None):
        if color_attr is None:
            color_attr = self.default_color_attr
        self.scr.addstr(y, x, s.encode(self.locale_code), color_attr)
    def cursor_position(self, x, y):
        self.scr.move(y, x)
    def cursor_visible(self, visible):
        if visible:
            curses.curs_set(1)
        else:
            curses.curs_set(0)
    def get_screen_size(self):
        return (curses.tigetnum("cols"), curses.tigetnum("lines"))
    def scroll_up(self, x1, y1, x2, y2, lines=1):
        cols = x2 - x1 + 1
        rows = y2 - y1 + 1
        win = self.scr.subwin(rows, cols, y1, x1)
        win.scrollok(True)
        win.bkgd(' ', self.default_color_attr)
        win.scroll(lines)
    def scroll_down(self, x1, y1, x2, y2, lines=1):
        (save_y, save_x) = self.scr.getyx()
        cols = x2 - x1 + 1
        rows = y2 - y1 + 1
        win = self.scr.subwin(rows, cols, y1, x1)
        win.scrollok(True)
        win.bkgd(' ', self.default_color_attr)
        win.move(0,0)
        win.insdelln(lines)
        self.scr.move(save_y, save_x)
    def get_input(self, timeout_msec=None):
        if timeout_msec is None:
            timeout_msec = -1
        self.scr.timeout(timeout_msec)
        ch = self.scr.getch()
        if ch == curses.KEY_MOUSE:
            try:
                (dev_id, x, y, z, bstate) = curses.getmouse()
                events = { }
                if bstate & curses.BUTTON1_CLICKED:
                    events["left_click"] = 1
                return textui_mouse_event(x, y, events)
            except curses.error:
                return None
        elif ch == curses.KEY_RESIZE:
            return textui_resize_event()
        elif ch == -1:
            return None
        else:
            return textui_keyboard_event(ch)

# The best way to use Python curses is via the curses.wrapper 
# function, but we don't want to expose that directly to the user of 
# this API. So we do a little dance to allow us to intermediate 
# between the curses callback and one for this API.
def _textui_wrapper_callback(scr, func, args):
    # if we wanted real-time mouse positioning we could do this
    #curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    ui = textui_curses(scr)
    func(ui, *args)

def textui_curses_invoke(func, *args):
    # if we wanted real-time mouse positioning we could do this
    #if os.environ.get('TERM', '') == 'xterm':
    #    os.environ['TERM'] = 'xterm-1003'
    os.environ['ESCDELAY'] = '25'
    curses.wrapper(_textui_wrapper_callback, func, args)

