class textui_event(object):
    def __init__(self, event_type):
        self.event_type = event_type

class textui_mouse_event(textui_event):
    def __init__(self, x, y, events):
        super(textui_mouse_event, self).__init__("mouse")
        self.x = x
        self.y = y
        self.events = events
    def left_click(self):
        return "left_click" in self.events

class textui_keyboard_event(textui_event):
    def __init__(self, key):
        super(textui_keyboard_event, self).__init__("keyboard")
        self.key = key

class textui_resize_event(textui_event):
    def __init__(self):
        super(textui_resize_event, self).__init__("resize")

