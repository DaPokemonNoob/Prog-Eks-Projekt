import card_classes as cc
import effects_data as ed

# Eksempel på minion kort:
def someGuy():
    return cc.Minion("Some Guy", manaCost=3, attack=2, hp=5, effect=None)

def someCoolGuy():
    ed.increase(1, 0)
    return cc.Minion("Some Cool Guy", manaCost=5, attack=4, hp=6, effect="When summoned: increase all minions attack by 1.")

def tank():
    ed.armor(2)
    ed.taunt()
    return cc.Minion("Tank", manaCost=3, attack=1, hp=7, effect="When summoned: gain 2 armor. If summoned in the 1st row: Taunt.")
    
# Eksempel på spell kort:
def fireball():
    return cc.Spell("Fireball", manaCost=4)

# Eksempel på Hero kort:
def adventurer():
    return cc.Hero("Adventurer", attack=1, hp=15)


