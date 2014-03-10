import glob
import textwrap
import textui
from keymap import *
import playerchar

class background:
    def __init__(self, name, image, description, 
                       allowed_skills, default_skill_levels):
        self.name = name
        self.image = image
        self.description = description
        self.allowed_skills = allowed_skills
        self.default_skill_levels = default_skill_levels

def load_all_backgrounds(directory="backgrounds"):
    backgrounds = [ ]
    longest_name = 0
    for filename in glob.glob("%s/*.txt" % directory):
        f = open(filename, "r")
        text = f.read()
        (name, image, description) = text.split("\n\n", 2)
        descr_parts = description.split("\n\n")
        allowed_skills = [ ]
        default_skill_levels = { }
        if descr_parts[-1].startswith("---\n"):
            # get skill changes
            for info in descr_parts[-1].strip().split('\n')[1:]:
                tag,val = info.split(' ', 1)
                if tag == 'skills':
                    allowed_skills = val.split(',')
                elif tag == 'default':
                    default_parts = val.split()
                    default_val = default_parts[-1]
                    default_skill = ' '.join(default_parts[:-1])
                    default_skill_levels[default_skill] = default_val
            descr_parts = descr_parts[:-1]
        description = '\n\n'.join(descr_parts)
        bg = background(name, image, description.strip(), 
                        allowed_skills, default_skill_levels)
        backgrounds.append(bg)
        longest_name = max(len(name), longest_name)
    backgrounds.sort(key=lambda x: x.name)
    return (backgrounds, longest_name)

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

def background_selection(ui):
    (backgrounds, longest_name) = load_all_backgrounds()
    ui.set_default_color_attr(textui.BLACK, textui.WHITE)
    ui.cursor_visible(False)
    menu_color = ui.color_attr(textui.BLACK, textui.WHITE)
    choice_color = ui.color_attr(textui.WHITE, textui.BLACK, textui.BOLD)
    disabled_color = ui.color_attr(textui.BLACK, textui.WHITE, textui.BOLD)
    choice = 0
    refresh = True
    while True:
        if refresh:
            textui.wait_for_minimum_size(ui, 80, 24)
            ui.clear()
            (width, height) = ui.get_screen_size()
            ui.write(1, 0, 
                     "So now you're a gladiator. But what were you before...")
            show_keys_help(ui, width, height, ("Up", "Down", "Enter"))
            step_txt = "[Step 1 of 3]"
            ui.write(width - len(step_txt) - 1, height - 1, step_txt)
            refresh = False
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
        new_choice = choice
        input_event = ui.get_input()
        if input_event.event_type == "keyboard":
            if input_event.key is textui.KEY_ENTER:
                return choice
            elif input_event.key in keys_d:
                # pick a new choice
                new_choice = (choice + 1) % len(backgrounds)
                while backgrounds[new_choice].image == "x":
                    new_choice = (new_choice + 1) % len(backgrounds)
            elif input_event.key in keys_u:
                # pick a new choice
                if choice == 0:
                    new_choice = len(backgrounds)-1
                else:
                    new_choice = choice - 1
                while backgrounds[new_choice].image == "x":
                    if new_choice == 0:
                        new_choice = len(backgrounds)-1
                    else:
                        new_choice = new_choice - 1
        elif (input_event.event_type == "mouse") and (input_event.left_click()):
                if (2 <= input_event.x <= 4+longest_name):
                    new_choice = input_event.y-2
                    if new_choice >= len(backgrounds):
                        new_choice = choice
                    elif backgrounds[new_choice].image == 'x':
                        new_choice = choice
                    elif new_choice == choice:
                        return choice
        elif input_event.event_type == "resize":
            refresh = True
        if new_choice != choice:
            # erase old picture
            image = backgrounds[choice].image
            n = len(backgrounds)+3
            for line in image.split('\n'):
                ui.write(1, n, ' ' * len(line), menu_color)
                n = n + 1
            # clear the text area
            ui.scroll_up(longest_name+6, 2, width-1, height-2, height-4)
            choice = new_choice

if __name__ == "__main__":
    textui.invoke(background_selection)
    
