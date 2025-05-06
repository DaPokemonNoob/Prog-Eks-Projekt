# Eksempel på minion kort:

def someGuy():
    from card_classes import Minion
    return Minion("Some Guy", manaCost=3, attack=2, hp=5, effect=None)

def someCoolGuy():
    from card_classes import Minion
    from effects_data import increase
    attack_bonus, hp_bonus = increase(1, 0)
    return Minion("Some Cool Guy", manaCost=5, attack=4 + attack_bonus, hp=6 + hp_bonus, effect="When summoned: increase all minions attack by 1.")

def knight():
    from card_classes import Minion
    from effects_data import armor, taunt
    armor_amount = armor(2)
    has_taunt = taunt()
    return Minion("Knight", manaCost=3, attack=1, hp=7 + armor_amount, effect="When summoned: gain 2 armor. If summoned in the 1st row: Taunt.")
    
# Eksempel på spell kort:
def fireball():
    from card_classes import Spell
    return Spell("Fireball", manaCost=4)

# Eksempel på Hero kort:
def adventurer():
    from card_classes import Hero
    return Hero("Adventurer", attack=1, hp=15)


