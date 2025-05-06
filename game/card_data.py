from card_classes import Minion, Spell, Weapon, Hero
import effects_data as effect

# Eksempel på minion kort:
def someGuy():
    return Minion("Some Guy", manaCost=2, attack=2, hp=5, effect=None)

def someCoolGuy():
    attack_bonus, hp_bonus = effect.increase(1, 0)
    return Minion("Some Cool Guy", manaCost=5, attack=4 + attack_bonus, hp=6 + hp_bonus, effect="When summoned: increase all minions attack by 1.")

def knight():
    armor_amount = effect.armor(2)
    has_taunt = effect.taunt()
    return Minion("Knight", manaCost=3, attack=1, hp=7 + armor_amount, effect="When summoned: gain 2 armor. If summoned in the 1st row: Taunt.")
    
# Eksempel på Hero kort:
def adventurer():
    return Hero("Adventurer", attack=1, hp=15)

# Eksempel på spell kort:
def fireball():
    return Spell("Fireball", manaCost=4, attack=2)

# Eksempel på weapon kort:
def sword():
    return Weapon("Sword", manaCost=3, attack=3, durability=2)


