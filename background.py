import glob

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
    backgrounds.sort(key=lambda x: x.name)
    return backgrounds

