import dice

def attack(attacker, attacker_name, weapon, victim, victim_name, history):
    # find the best skill the attacker has for this weapon
    max_skill_lvl = -1
    max_skill_name = None
    if weapon:
        skills = weapon.skills
    else:
        skills = [ "Punch", "Kick", "Head Butt" ]
    for skill in skills:
        if attacker.skill_levels[skill] > max_skill_lvl:
            max_skill_lvl = attacker.skill_levels[skill]
            max_skill_name = skill

    # roll for the attacker
    attack_roll = dice.success_roll(max_skill_lvl)

    # figure out the damage based on the weapon
    if weapon:
        best_attack_avg = -1
        for attack_type in weapon.damage.keys():
            avg_roll = weapon.damage[attack_type].avg()
            if avg_roll > best_attack_avg:
                best_attack_avg = avg_roll
                dmg = weapon.damage[attack_type]
    elif max_skill_name == "Punch":
        dmg = dice.die("1D3")
    elif max_skill_name == "Kick":
        dmg =  dice.die("1D6")
    elif max_skill_name == "Head Butt":
        dmg =  dice.die("1D4")
    else:
        assert(0)
    dmg_bonus = attacker.damage_bonus()

    # find the best chance for the defender
    best_defense = [ None, -1 ]
    # the victim has a weapon...
    if victim.equip["right hand"] and victim.can_parry:
        parry_weapon = victim.equip["right hand"]
        parry_skill = -1
        for skill in parry_weapon.skills:
            if victim.skill_levels[skill] > best_defense[1]:
                best_defense = [ "parry", victim.skill_levels[skill] ]
    # the victim has no weapon, but the attack was unarmed
    elif victim.can_parry and not weapon:
        for skill in [ "Punch", "Kick", "Head Butt" ]:
            if victim.skill_levels[skill] > best_defense[1]:
                best_defense = [ "parry", victim.skill_levels[skill] ]
    # the victim has a shield
    elif victim.can_block and victim.equip["left hand"] and \
         ("shield" in victim.equip["left hand"].name.lower()):
        block_shield = victim.equip["left hand"]
        block_skill = -1
        for skill in block_shield.skills:
            if victim.skill_levels[skill] > best_defense[1]:
                best_defense = [ "block", victim.skill_levels[skill] ]
    elif victim.can_dodge:
        if victim.skill_levels["Dodge"] > best_defense[1]:
            best_defense = [ "dodge", victim.skill_levels["Dodge"] ]

    if best_defense[0]:
        defense_roll = dice.success_roll(best_defense[1])
        # mark our defense as done until our next turn
        if best_defense[0] == "block":
            victim.can_block = False
        elif best_defense[0] == "dodge":
            victim.can_dodge = False
        elif best_defense[0] == "parry":
            victim.can_parry = False
    else:
        defense_roll = "fail"


    hp = 0
    # TODO: add flavor text
    if attack_roll == "critical":
        if defense_roll == "critical":
            hp = dmg.min() + dmg_bonus.min()
        elif defense_roll == "success":
            hp = dmg.roll() + dmg_bonus.roll()
        else:
            hp = dmg.max() + dmg_bonus.max()
    elif attack_roll == "success":
        if defense_roll == "critical":
            hp = 0
        elif defense_roll == "success":
            hp = dmg.min() + dmg_bonus.min()
        elif defense_roll == "failure":
            hp = dmg.roll() + dmg_bonus.roll()
        elif defense_roll == "fumble":
            hp = dmg.max() + dmg_bonus.max()

    if hp <= 0:
        history.add("%s attack %s: miss" % (attacker_name, victim_name))
    else:
        # reduce by armor amount
        armor = victim.equip["torso"]
        if armor:
            if armor.armor:
                protection = armor.armor
            else:
                protection = 0
            hp = max(hp - protection, 0)
        history.add("%s attack %s: hit for %d damage!" % (attacker_name, 
                                                            victim_name, hp))
        victim.wounds.append(hp)
        victim.HP = victim.HP - hp

