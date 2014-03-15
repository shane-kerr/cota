import textwrap
import textui
from keymap import *
from humans import Skills
import background
import playerchar
import display

def background_selection(ui, backgrounds):
    longest_name = -1
    for bg in backgrounds:
        longest_name = max(longest_name, len(bg.name))
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
            instr_txt = "-=[ SELECT YOUR BACKGROUND ]=-"
            ui.write((width-len(instr_txt))//2, 0, instr_txt)
            display.show_keys_help(ui, width, height, ("Up", "Down", "Enter"))
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
                return backgrounds[choice]
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
                        return backgrounds[choice]
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

def show_char_stats(ui, pc):
    # basic stats
    ui.write(2, 4, "STR: %2d" % pc.STR)
    ui.write(2, 5, "CON: %2d" % pc.CON)
    ui.write(2, 6, "DEX: %2d" % pc.DEX)
    ui.write(2, 7, "SIZ: %2d" % pc.SIZ)
    ui.write(2, 8, "INT: %2d" % pc.INT)
    ui.write(2, 9, "POW: %2d" % pc.POW)
    ui.write(2, 10, "APP: %2d" % pc.APP)
    ui.write(2, 11, "EDU: %2d" % pc.EDU)

    # derived stats
    ui.write(12, 4, "Sanity: %2d" % pc.Sanity)
    ui.write(12, 5, "Idea:   %2d" % pc.Idea)
    ui.write(12, 6, "Know:   %2d" % pc.Know)
    ui.write(12, 7, "Luck:   %2d" % pc.Luck)

    # and points
    ui.write(12, 9, "HP:     %2d" % pc.HP)
    ui.write(12, 10, "MP:     %2d" % pc.MP)
    ui.write(12, 11, "SP:     %2d" % pc.Sanity)

def show_skill_list(ui, width, height, ofs, cur, skill_list, pc, occupation):
    cur_on_color = ui.color_attr(textui.WHITE, textui.BLACK, textui.BOLD)
    if occupation:
        cur_off_color = ui.color_attr(textui.WHITE, textui.BLACK)
    else:
        cur_off_color = cur_on_color
    on_color = ui.color_attr(textui.BLACK, textui.WHITE)
    if occupation:
        off_color = ui.color_attr(textui.BLACK, textui.WHITE, textui.BOLD)
    else:
        off_color = on_color

    visible_height = height - 4
    n = 0
    while (n < visible_height) and (n+ofs < len(skill_list.names)):
        name = skill_list.names[n+ofs]
        if name == "---":
            ui.write(width // 2, n+2, "-" * ((width // 2) - 2), off_color)
        else:
            s = name.ljust((width // 2) - 7) + ("%3d" % pc.skill_levels[name])
            if n+ofs == cur:
                if name in pc.skills_added:
                    ui.write(width // 2, n+2, ">" + s + "<", cur_on_color)
                else:
                    ui.write(width // 2, n+2, ">" + s + "<", cur_off_color)
            else:
                if name in pc.skills_added:
                    ui.write(width // 2, n+2, " " + s + " ", on_color)
                else:
                    ui.write(width // 2, n+2, " " + s + " ", off_color)
        n = n + 1
    
def do_occupation_skills(ui, bg, pc, skill_list):
    # set defaults based on statistics
    for (name, default) in skill_list.defaults.items():
        if default.upper().startswith("DEX*"):
            default = pc.DEX * int(default[4:])
        elif default.upper().startswith("EDU*"):
            default = pc.EDU * int(default[4:])
        pc.skill_defaults[name] = int(default)
        pc.skill_levels[name] = int(default)
    # set new defaults from background
    for (name, default) in bg.default_skill_levels.items():
        if default.upper().startswith("DEX*"):
            default = pc.DEX * int(default[4:])
        elif default.upper().startswith("EDU*"):
            default = pc.EDU * int(default[4:])
        pc.skill_defaults[name] = int(default)
        pc.skill_levels[name] = int(default)
    # set added skills from background
    for name in bg.allowed_skills:
        pc.skills_started[name] = True
        pc.skills_added[name] = True
    # count the unassigned skills in the background
    unassigned_skill_cnt = 0
    for skill in bg.allowed_skills:
        if skill == "*":
            unassigned_skill_cnt = unassigned_skill_cnt + 1
    free_skill_points = pc.EDU * 20
    # set up screen
    ui.set_default_color_attr(textui.BLACK, textui.WHITE)
    ui.cursor_visible(False)
    menu_color = ui.color_attr(textui.BLACK, textui.WHITE)
    choice_color = ui.color_attr(textui.WHITE, textui.BLACK, textui.BOLD)
    disabled_color = ui.color_attr(textui.BLACK, textui.WHITE, textui.BOLD)
    ofs = 0
    cur = 0
    refresh = True
    while True:
        if refresh:
            textui.wait_for_minimum_size(ui, 80, 24)
            ui.clear()
            (width, height) = ui.get_screen_size()
            instr_txt = "-=[ ASSIGN YOUR OCCUPATION SKILLS ]=-"
            ui.write((width-len(instr_txt))//2, 0, instr_txt)
            ui.write(2, 2, "Background: %s" % bg.name)
            ui.write(2, 13, "Unassigned Skills:  %3d" % unassigned_skill_cnt)
            ui.write(2, 14, "Free Skill Points:  %3d" % free_skill_points)
            show_char_stats(ui, pc)
            step_txt = "[Step 2 of 3]"
            ui.write(width - len(step_txt) - 1, height - 1, step_txt)
            refresh = False
        disabled = []
        if cur == 0:
            disabled.append("Up")
        elif cur == len(skill_list.names) - 1:
            disabled.append("Down")
        name = skill_list.names[cur]
        if pc.skill_levels[name] == pc.skill_defaults[name]:
            disabled.append("Left")
        if free_skill_points <= 0:
            disabled.append("Right")
        elif (name not in pc.skills_added) and (unassigned_skill_cnt <= 0):
            disabled.append("Right")
        display.show_keys_help(ui, width, height, 
                           ("Esc", "Up", "Down", "Left", "Right", "Enter"), 
                           disabled)
        show_skill_list(ui, width, height, ofs, cur, skill_list, pc, True)
        input_event = ui.get_input()
        if input_event.event_type == "keyboard":
            if input_event.key in keys_d:
                if cur < len(skill_list.names)-1:
                    cur = cur + 1
                if skill_list.names[cur] == '---':
                    cur = cur + 1
            elif input_event.key in keys_u:
                if cur > 0:
                    cur = cur - 1
                if skill_list.names[cur] == '---':
                    cur = cur - 1
            elif input_event.key in keys_l:
                if not pc.skill_levels[name] == pc.skill_defaults[name]:
                    new_level = pc.skill_levels[name]
                    new_level = new_level - (new_level % 5)
                    if new_level == pc.skill_levels[name]:
                        new_level = new_level - 5
                    new_level = max(new_level, pc.skill_defaults[name])
                    points_gained = pc.skill_levels[name] - new_level
                    if new_level == pc.skill_defaults[name]:
                        if name not in pc.skills_started:
                            del pc.skills_added[name]
                            unassigned_skill_cnt = unassigned_skill_cnt + 1
                    pc.skill_levels[name] = new_level
                    free_skill_points = free_skill_points + points_gained
                    ui.write(2, 13, "Unassigned Skills:  %3d" % 
                                   unassigned_skill_cnt)
                    ui.write(2, 14, "Free Skill Points:  %3d" % 
                                   free_skill_points)
            elif input_event.key in keys_r:
                if (name not in pc.skills_added) and \
                   (unassigned_skill_cnt > 0) and (free_skill_points > 0):
                    pc.skills_added[name] = True
                    unassigned_skill_cnt = unassigned_skill_cnt - 1
                if (name in pc.skills_added) and (free_skill_points > 0):
                    increase = min(free_skill_points, 5)
                    new_level = pc.skill_levels[name] + increase
                    new_level = new_level - (new_level % increase)
                    points_used = new_level - pc.skill_levels[name]
                    pc.skill_levels[name] = new_level
                    free_skill_points = free_skill_points - points_used
                    ui.write(2, 13, "Unassigned Skills:  %3d" % 
                                   unassigned_skill_cnt)
                    ui.write(2, 14, "Free Skill Points:  %3d" % 
                                   free_skill_points)
            elif input_event.key in keys_ul:
                # home
                cur = 0
                ofs = 0
            elif input_event.key in keys_dl:
                # end
                cur = len(skill_list.names)-1
                ofs = cur - (height - 4)
            elif input_event.key in keys_dr:
                # pgdn
                cur = min(cur+height-6, len(skill_list.names)-1)
                if skill_list.names[cur] == '---':
                    cur = cur + 1
            elif input_event.key in keys_ur:
                # pgup
                cur = max(cur-(height-6), 0)
                if skill_list.names[cur] == '---':
                    cur = cur - 1
            elif input_event.key == textui.KEY_ENTER:
                return "next"
            elif input_event.key == textui.KEY_ESC:
                return "prev"
        elif input_event.event_type == "resize":
            refresh = True
        while (cur - ofs) >= (height - 4):
            ofs = ofs + 1
        while (cur - ofs) < 0:
            ofs = ofs - 1

# XXX: cut & paste hack due to lateness of hour and desire for progress
# TODO: merge and refactor
def do_other_skills(ui, bg, pc, skill_list):
    # get skill levels on entry - can't go lower than these
    skills_on_entry = pc.skill_levels.copy()
    # count the unassigned skills from personal interests
    free_skill_points = pc.INT * 10
    # set up screen
    ui.set_default_color_attr(textui.BLACK, textui.WHITE)
    ui.cursor_visible(False)
    menu_color = ui.color_attr(textui.BLACK, textui.WHITE)
    choice_color = ui.color_attr(textui.WHITE, textui.BLACK, textui.BOLD)
    disabled_color = ui.color_attr(textui.BLACK, textui.WHITE, textui.BOLD)
    ofs = 0
    cur = 0
    refresh = True
    while True:
        if refresh:
            textui.wait_for_minimum_size(ui, 80, 24)
            ui.clear()
            (width, height) = ui.get_screen_size()
            instr_txt = "-=[ ASSIGN YOUR PERSONAL INTEREST SKILLS ]=-"
            ui.write((width-len(instr_txt))//2, 0, instr_txt)
            ui.write(2, 2, "Background: %s" % bg.name)
            ui.write(2, 14, "Free Skill Points:  %3d" % free_skill_points)
            show_char_stats(ui, pc)
            step_txt = "[Step 3 of 3]"
            ui.write(width - len(step_txt) - 1, height - 1, step_txt)
            refresh = False
        disabled = []
        if cur == 0:
            disabled.append("Up")
        elif cur == len(skill_list.names) - 1:
            disabled.append("Down")
        name = skill_list.names[cur]
        if pc.skill_levels[name] == skills_on_entry[name]:
            disabled.append("Left")
        if free_skill_points <= 0:
            disabled.append("Right")
        display.show_keys_help(ui, width, height, 
                           ("Esc", "Up", "Down", "Left", "Right", "Enter"), 
                           disabled)
        show_skill_list(ui, width, height, ofs, cur, skill_list, pc, False)
        input_event = ui.get_input()
        if input_event.event_type == "keyboard":
            if input_event.key in keys_d:
                if cur < len(skill_list.names)-1:
                    cur = cur + 1
                if skill_list.names[cur] == '---':
                    cur = cur + 1
            elif input_event.key in keys_u:
                if cur > 0:
                    cur = cur - 1
                if skill_list.names[cur] == '---':
                    cur = cur - 1
            elif input_event.key in keys_l:
                if not pc.skill_levels[name] == skills_on_entry[name]:
                    new_level = pc.skill_levels[name]
                    new_level = new_level - (new_level % 5)
                    if new_level == pc.skill_levels[name]:
                        new_level = new_level - 5
                    new_level = max(new_level, pc.skill_defaults[name])
                    points_gained = pc.skill_levels[name] - new_level
                    pc.skill_levels[name] = new_level
                    free_skill_points = free_skill_points + points_gained
                    ui.write(2, 14, "Free Skill Points:  %3d" % 
                                   free_skill_points)
            elif input_event.key in keys_r:
                if free_skill_points > 0:
                    increase = min(free_skill_points, 5)
                    new_level = pc.skill_levels[name] + increase
                    new_level = new_level - (new_level % increase)
                    points_used = new_level - pc.skill_levels[name]
                    pc.skill_levels[name] = new_level
                    free_skill_points = free_skill_points - points_used
                    ui.write(2, 14, "Free Skill Points:  %3d" % 
                                   free_skill_points)
            elif input_event.key in keys_ul:
                # home
                cur = 0
                ofs = 0
            elif input_event.key in keys_dl:
                # end
                cur = len(skill_list.names)-1
                ofs = cur - (height - 4)
            elif input_event.key in keys_dr:
                # pgdn
                cur = min(cur+height-6, len(skill_list.names)-1)
                if skill_list.names[cur] == '---':
                    cur = cur + 1
            elif input_event.key in keys_ur:
                # pgup
                cur = max(cur-(height-6), 0)
                if skill_list.names[cur] == '---':
                    cur = cur - 1
            elif input_event.key == textui.KEY_ENTER:
                return "next"
            elif input_event.key == textui.KEY_ESC:
                return "prev"
        elif input_event.event_type == "resize":
            refresh = True
        while (cur - ofs) >= (height - 4):
            ofs = ofs + 1
        while (cur - ofs) < 0:
            ofs = ofs - 1

def make_char(ui, backgrounds):
    skill_list = Skills()
    pc = playerchar.PlayerCharacter()
    bg = background_selection(ui, backgrounds)
    while do_occupation_skills(ui, bg, pc, skill_list) == "prev":
        bg = background_selection(ui, backgrounds)
    while do_other_skills(ui, bg, pc, skill_list) == "prev":
        while do_occupation_skills(ui, bg, pc, skill_list) == "prev":
            bg = background_selection(ui, backgrounds)
    return (skill_list, pc)

if __name__ == "__main__":
    textui.invoke(make_char)
    
