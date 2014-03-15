import textui
import chargen
import training
import background

def play_game(ui):
    backgrounds = background.load_all_backgrounds()
    (skill_list, pc) = chargen.make_char(ui, backgrounds)
    training.school(ui, backgrounds, skill_list, pc)

if __name__ == "__main__":
    textui.invoke(play_game)
