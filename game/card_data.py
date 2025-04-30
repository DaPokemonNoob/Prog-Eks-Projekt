from card_classes import *

# Eksempel på minion kort:
def someGuy():
    return Minion("Some Guy", manaCost=3, attack=2, hp=5)

# Eksempel på spell kort:
def fireball():
    return Spell("Fireball", manaCost=4)

# Eksempel på Hero kort:
def adventurer():
    return Hero("Adventurer", attack=1, hp=15)


