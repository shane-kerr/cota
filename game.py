import textui
import chargen
import training
import background

outcome = None

def play_game(ui):
    backgrounds = background.load_all_backgrounds()
    (skill_list, pc) = chargen.make_char(ui, backgrounds)
    global outcome
    outcome = training.school(ui, backgrounds, skill_list, pc)

if __name__ == "__main__":
    textui.invoke(play_game)
    if outcome == "dead":
        print("Your time training for the arena ends as it does for many,")
        print("with an ignoble death.")
    elif outcome == "unconscious":
        print("You end up knocked unconscious. Iudicatus decides you are")
        print("better off in the mines than entertaining the crowds.")

