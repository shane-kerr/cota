def attack(attacker, weapon, victim, history):
    max_skill = 0
    for skill in weapon.skills:
        if attacker.skill_levels[skill] > max_skill:
            max_skill = attacker.skill_levels[skill]


