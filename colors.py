from textui import BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW
from textui import NORMAL, BOLD

_color_mappings = {
    "black":        ( BLACK, BLACK, NORMAL ),
    "blue":         ( BLUE, BLACK, NORMAL ),
    "cyan":         ( CYAN, BLACK, NORMAL ),
    "green":        ( GREEN, BLACK, NORMAL ),
    "magenta":      ( MAGENTA, BLACK, NORMAL ),
    "red":          ( RED, BLACK, NORMAL ),
    "white":        ( WHITE, BLACK, BOLD ),
    "yellow":       ( YELLOW, BLACK, BOLD ),
    "brown":        ( YELLOW, BLACK, NORMAL ),
    "dark gray":    ( BLACK, BLACK, BOLD ),
    "light gray":   ( WHITE, BLACK, NORMAL ),
    "bright red":   ( RED, BLACK, BOLD)
}

def parse_color(s):
    s = s.strip().lower()
    return _color_mappings[s]
