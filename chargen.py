import glob
import textwrap
import textui

class background:
    def __init__(self, name, image, description):
        self.name = name
        self.image = image
        self.description = description
    def __cmp__(a, b):
        return cmp(a.name, b.name)

def load_all_backgrounds(directory="backgrounds"):
    backgrounds = [ ]
    longest_name = 0
    for filename in glob.glob("%s/*.txt" % directory):
        f = open(filename, "r")
        text = f.read()
        (name, image, description) = text.split("\n\n", 2)
#        name = name.strip()
        backgrounds.append(background(name, image, description.strip()))
        longest_name = max(len(name), longest_name)
    backgrounds.sort()
    return (backgrounds, longest_name)

def background_selection(ui):
    (backgrounds, longest_name) = load_all_backgrounds()
    ui.set_default_color_attr(textui.BLACK, textui.WHITE)
    ui.cursor_visible(False)
    ui.clear()
    (width, height) = ui.get_screen_size()
    ui.write(1, 0, "So now you're a gladiator. But what were you before...")
    step_txt = "[Step 1 of 2]"
    ui.write(width - len(step_txt) - 1, height - 1, step_txt)
    menu_color = ui.color_attr(textui.BLACK, textui.WHITE)
    choice_color = ui.color_attr(textui.WHITE, textui.BLACK)
    disabled_color = ui.color_attr(textui.BLACK, textui.WHITE, textui.BOLD)
    choice = 0
    for n in range(len(backgrounds)):
        txt = backgrounds[n].name.ljust(longest_name)
        if backgrounds[n].image == "x":
            ui.write(2, 2+n, " " + txt + " ", disabled_color)
        elif n == choice:
            ui.write(2, 2+n, ">" + txt + "<", choice_color)
        else:
            ui.write(2, 2+n, " " + txt + " ", menu_color)
    image = backgrounds[choice].image
    n = len(backgrounds)+3
    for line in image.split('\n'):
        ui.write(1, n, line, menu_color)
        n = n + 1
    desc_paragraphs = backgrounds[choice].description.split('\n\n')
    lines = textwrap.wrap(desc_paragraphs[0], width-(longest_name+8))
    for paragraph in desc_paragraphs[1:]:
        lines.append("")
        lines.extend(textwrap.wrap(paragraph, width-(longest_name+8)))
    for n in range(len(lines)):
        ui.write(longest_name+6, n+2, lines[n])
    ui.get_input()

if __name__ == "__main__":
    textui.invoke(background_selection)
    
