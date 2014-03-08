"""
This module defines an API for working with the console that works
on both curses systems (traditional Unix systems) and Windows.

The functionality provided is:

* Clearing the screen
* Detecting the console size
  * Also receive notification when the console is resized
* Drawing a string a position with a specified color
* Moving the cursor to a given position
* Scrolling a region of the screen
* Read a character from the keyboard
* Detect mouse clicks
* Timeout on input

Missing, but easily possible, functionality is:
* Mouse position as it passes over the window
* Setting fill color on scrolling (default color currently used)
* Box drawing

That's it!

To use the library:

    import textui

    textui.invoke(start_func, [start_func_param1, [...]])

The start_func() will be invoked

Output will be done using the old IBM extended ASCII character set.

Screen positions are given as x,y where x is the column of output and
y is the row of output (note that this is the opposite of what curses 
uses, but matches Windows console functions... and normal geometry). 
The x value goes from 0 on the left of the screen to width-1 on the 
right of the screen. The y value goes from 0 on the top of the screen
to height-1 on the bottom of the screen.

The Windows approach is using ctypes to invoke the appropriate Windows
console functions, as documented here:

http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/

Next time, probably I should use pygame. :)
"""

import sys

if sys.platform == 'win32':
    from textuiwin32 import *

    invoke = textui_win_invoke
else:
    from textuicurses import *

    invoke = textui_curses_invoke

# curses testing stuff

#def hello(ui, s=None):
#    if not s:
#        s = "Hello, world"
#    ui.write(0, 0, s, ui.color_attr(BLACK, WHITE))
#    ui.write(0, 1, "blah")
#    ui.set_default_color_attr(YELLOW, BLACK, BOLD)
#    ui.write(0, 2, "Hello, yellow!")
#    ui.set_default_color_attr(YELLOW, BLACK)
#    ui.write(0, 3, "Golden brown, always the same!")
#    ui.write(0, 4, "Screen is %dx%d" % ui.get_screen_size())
#    while True:
#        input_event = ui.get_input()
#        if input_event.event_type == "keyboard": break
#    ui.scroll_up(0, 0, 2, 2)
#    ui.scroll_down(6, 2, 12, 4, 2)
#    ui.get_input()
#    timeout_cnt = 0
#    while True:
#        input_event = ui.get_input(1000)
#        if input_event is None:
#            timeout_cnt = timeout_cnt + 1
#            ui.write(0, 7, "timeout %d" % timeout_cnt)
#        elif input_event.event_type == "keyboard":
#            ui.write(0, 5, "key is %d    " % input_event.key)
#            if input_event.key == ord('q'): return
#            if input_event.key == KEY_UP:
#                ui.write(0, 5, "key is KEY_UP")
#        elif (input_event.event_type == "mouse") and input_event.left_click():
#            ui.write(0, 6, "click at %d,%d" % (input_event.x, input_event.y))
#        elif input_event.event_type == "resize":
#            ui.write(0, 4, "Screen is %dx%d    " % ui.get_screen_size())
#if __name__ == "__main__":
#    invoke(hello, "foo")
