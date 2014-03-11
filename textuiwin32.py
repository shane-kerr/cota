import ctypes
import sys
from textuievents import *

# we only support bold or non-bold attributes
BOLD = 8
NORMAL = 0

# we support the 8 holy TTY colors
BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
YELLOW = 6
WHITE = 7

# defined keys
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms683499%28v=vs.85%29.aspx
# make these negative, so we can share the space with Unicode :)
KEY_UP = -0x26
KEY_DOWN = -0x28
KEY_LEFT = -0x25
KEY_RIGHT = -0x27
KEY_HOME = -0x24
KEY_PGUP = -0x21
KEY_END = -0x23
KEY_PGDN = -0x22
KEY_F1 = -0x70
KEY_ENTER = ord('\r')

# Windows types are documented here:
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa383751%28v=vs.85%29.aspx
BOOL = ctypes.c_int
CHAR = ctypes.c_char
DWORD = ctypes.c_ulong
SHORT = ctypes.c_short
UINT = ctypes.c_uint
WCHAR = ctypes.c_wchar
WORD = ctypes.c_ushort

# Windows has some standard handles, documented here:
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms683231%28v=vs.85%29.aspx
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# to read input, we need to enable input, using these constants
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms686033%28v=vs.85%29.aspx
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_MOUSE_INPUT  = 0x0010

# the event types are identified with these constants
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms683499%28v=vs.85%29.aspx
KEY_EVENT                = 0x0001
MOUSE_EVENT              = 0x0002
WINDOW_BUFFER_SIZE_EVENT = 0x0004

# button state as documented on this page:
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms684239%28v=vs.85%29.aspx
FROM_LEFT_1ST_BUTTON_PRESSED = 0x0001
RIGHTMOST_BUTTON_PRESSED     = 0x0002

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms682119%28v=vs.85%29.aspx
class COORD(ctypes.Structure):
    _fields_ = [
        ("X", SHORT),
        ("Y", SHORT)
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms686311%28v=vs.85%29.aspx
class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", SHORT),
        ("Top", SHORT),
        ("Right", SHORT),
        ("Bottom", SHORT)
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms682093%28v=vs.85%29.aspx
class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms682013%28v=vs.85%29.aspx
class Char(ctypes.Union):
    _fields_ = [
        ("UnicodeChar", WCHAR),
        ("AsciiChar", CHAR),
    ]
class CHAR_INFO(ctypes.Structure):
    _fields_ = [
        ("Char", Char),
        ("Attributes", WORD),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms683149%28v=vs.85%29.aspx
class FOCUS_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("bSetFocus", BOOL),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms684166%28v=vs.85%29.aspx
class KEY_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("bKeyDown", BOOL),
        ("wRepeatCount", WORD),
        ("wVirtualKeyCode", WORD),
        ("wVirtualScanCode", WORD),
        ("uChar", Char),
        ("dwControlKeyState", DWORD),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms684213%28v=vs.85%29.aspx
class MENU_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("dwCommandId", UINT),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms684239%28v=vs.85%29.aspx
class MOUSE_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", DWORD),
        ("dwControlKeyState", DWORD),
        ("dwEventFlags", DWORD),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms687093%28v=vs.85%29.aspx
class WINDOW_BUFFER_SIZE_RECORD(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms683499%28v=vs.85%29.aspx
class Event(ctypes.Union):
    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD),
        ("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
        ("MenuEvent", MENU_EVENT_RECORD),
        ("FocusEvent", FOCUS_EVENT_RECORD),
    ]
class INPUT_RECORD(ctypes.Structure):
    _fields_ = [
        ("EventType", WORD),
        ("Event", Event),
    ]

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms682068%28v=vs.85%29.aspx
class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("bVisible", BOOL),
    ]

class textui_win:
    def __init__(self):
        self.kern = ctypes.windll.kernel32
        self.hIn = self.kern.GetStdHandle(STD_INPUT_HANDLE)
        self.hOut = self.kern.GetStdHandle(STD_OUTPUT_HANDLE)
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms683171%28v=vs.85%29.aspx
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        self.kern.GetConsoleScreenBufferInfo(self.hOut, ctypes.byref(csbi))
        self.start_attr = csbi.wAttributes
        cci = CONSOLE_CURSOR_INFO()
        self.kern.GetConsoleCursorInfo(self.hOut, ctypes.byref(cci))
        self.start_cursor_info = cci
        dwMode = DWORD(ENABLE_WINDOW_INPUT| ENABLE_MOUSE_INPUT)
        self.kern.SetConsoleMode(self.hIn, 
                                 ENABLE_WINDOW_INPUT| ENABLE_MOUSE_INPUT)
        self.default_color_attr = None
        self.set_default_color_attr(WHITE, BLACK)
    def restore(self):
        self.default_color_attr = self.start_attr
        self.kern.SetConsoleTextAttribute(self.hOut, self.start_attr)
        self.kern.SetConsoleCursorInfo(self.hOut, 
                                       ctypes.byref(self.start_cursor_info))
    def color_attr(self, fg=WHITE, bg=BLACK, attr=NORMAL):
        return fg | attr | bg << 4
    def set_default_color_attr(self, fg=WHITE, bg=BLACK, attr=NORMAL):
        self.default_color_attr = self.color_attr(fg, bg, attr)
    def clear(self):
        (width, height) = self.get_screen_size()
        self.write(0, 0, ' ' * (width * height))
        self.cursor_position(0, 0)
    def write(self, x, y, s, color_attr=None):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms686047%28v=vs.85%29.aspx
        if color_attr is None:
            color_attr = self.default_color_attr
        self.kern.SetConsoleTextAttribute(self.hOut, color_attr)
        self.cursor_position(x, y)
        sys.stdout.write(s)
        sys.stdout.flush()
    def cursor_position(self, x, y):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms686025%28v=vs.85%29.aspx
        pos = COORD()
        pos.X = x
        pos.Y = y
        self.kern.SetConsoleCursorPosition(self.hOut, pos)
    def cursor_visible(self, visible):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms683163%28v=vs.85%29.aspx
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms686019%28v=vs.85%29.aspx
        # we need to get the cursor info first, because we must set the
        # height of the cursor, but we really just want to leave that alone
        cci = CONSOLE_CURSOR_INFO()
        self.kern.GetConsoleCursorInfo(self.hOut, ctypes.byref(cci))
        cci.bVisible = visible
        self.kern.SetConsoleCursorInfo(self.hOut, ctypes.byref(cci))
    def get_screen_size(self):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms683171%28v=vs.85%29.aspx
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        self.kern.GetConsoleScreenBufferInfo(self.hOut, ctypes.byref(csbi))
        columns = csbi.srWindow.Right - csbi.srWindow.Left + 1
        rows = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        return (columns, rows)
    def _scroll(self, srctScrollRect, coordDest):
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ms685107%28v=vs.85%29.aspx
        fill = CHAR_INFO()
        fill_char = Char()
        fill_char.AsciiChar = b" "
        fill.Char = fill_char
        fill.Attributes = self.default_color_attr
        self.kern.ScrollConsoleScreenBufferW(self.hOut, 
                                             ctypes.byref(srctScrollRect), None,
                                             coordDest, ctypes.byref(fill)) 
    def scroll_up(self, x1, y1, x2, y2, lines=1):
        area_height = y2 - y1 + 1
        max_scroll = area_height // 2
        while lines > 0:
            scroll_amt = min(lines, max_scroll)
            srctScrollRect = SMALL_RECT()
            srctScrollRect.Left = x1
            srctScrollRect.Top = y1+scroll_amt
            srctScrollRect.Right = x2
            srctScrollRect.Bottom = y2
            coordDest = COORD()
            coordDest.X = x1
            coordDest.Y = y1
            self._scroll(srctScrollRect, coordDest)
            lines = lines - scroll_amt
    def scroll_down(self, x1, y1, x2, y2, lines=1):
        area_height = y2 - y1 + 1
        max_scroll = area_height // 2
        while lines > 0:
            scroll_amt = min(lines, max_scroll)
            srctScrollRect = SMALL_RECT()
            srctScrollRect.Left = x1
            srctScrollRect.Top = y1
            srctScrollRect.Right = x2
            srctScrollRect.Bottom = y2 - scroll_amt
            coordDest = COORD()
            coordDest.X = x1
            coordDest.Y = y1 + scroll_amt
            lines = lines - scroll_amt
            self._scroll(srctScrollRect, coordDest)
    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms685035%28v=vs.85%29.aspx
    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms685035%28v=vs.85%29.aspx
    def get_input(self, timeout_msec=None):
        buf = INPUT_RECORD()
        while True:
            while True:
                numberOfEventsRead = DWORD()
                if timeout_msec:
                    wait_result = self.kern.WaitForSingleObject(self.hIn, 
                                                                timeout_msec)
                    if wait_result != 0:
                        return None
                self.kern.ReadConsoleInputW(self.hIn, ctypes.byref(buf), 1, 
                                            ctypes.byref(numberOfEventsRead))
                if numberOfEventsRead.value == 1: break
            if buf.EventType == WINDOW_BUFFER_SIZE_EVENT:
                return textui_resize_event()
            if buf.EventType == KEY_EVENT:
                key_event = buf.Event.KeyEvent
                if key_event.bKeyDown:
                    # return the character we got from the keyboard
                    char = ord(key_event.uChar.UnicodeChar)
                    # if we didn't read an actual character, return the keycode
                    if char == 0:
                        char = -key_event.wVirtualKeyCode
                    return textui_keyboard_event(char)
            if buf.EventType == MOUSE_EVENT:
                mouse_event = buf.Event.MouseEvent
                x = mouse_event.dwMousePosition.X
                y = mouse_event.dwMousePosition.Y
                events = { }
                if mouse_event.dwButtonState == FROM_LEFT_1ST_BUTTON_PRESSED:
                    events["left_click"] = 1
                return textui_mouse_event(x, y, events)


def textui_win_invoke(func, *args):
    ui = textui_win()
    ui.clear()
    try:
        func(ui, *args)
    finally:
        ui.restore()
        ui.clear()

