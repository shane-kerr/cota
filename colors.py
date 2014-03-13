from textui import BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW
import textui

_color_mappings = {
    "black":        ( BLACK, BLACK, textui.NORMAL ),
    "blue":         ( BLUE, BLACK, textui.NORMAL ),
    "cyan":         ( CYAN, BLACK, textui.NORMAL ),
    "green":        ( GREEN, BLACK, textui.NORMAL ),
    "magenta":      ( MAGENTA, BLACK, textui.NORMAL ),
    "red":          ( RED, BLACK, textui.NORMAL ),
    "white":        ( WHITE, BLACK, textui.BOLD ),
    "yellow":       ( YELLOW, BLACK, textui.BOLD ),
    "brown":        ( YELLOW, BLACK, textui.NORMAL ),
    "dark gray":    ( BLACK, BLACK, textui.BOLD ),
    "light gray":   ( WHITE, BLACK, textui.NORMAL ),
}

def parse_color(s):
    s = s.strip().lower()
    return _color_mappings[s]
