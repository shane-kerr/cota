import textui
import chargen
import training

def play_game(ui):
    (skill_list, pc) = chargen.make_char(ui)
    training.school(ui, skill_list, pc)

if __name__ == "__main__":
    textui.invoke(play_game)
