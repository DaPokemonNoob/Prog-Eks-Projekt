# Card superclass:
class Card:
    def __init__(self, category, name, manaCost, effect, pic=None):
        self.category = category
        self.name = name
        self.manaCost = manaCost
        self.effect = effect
        self.pic = pic

# Hero subclass:
class Hero(Card):
    def __init__(self, name, attack, hp, pic=None):
        super().__init__(category='hero', name, manaCost=0, effect=None, pic=pic)
        self.attack = attack
        self.hp = hp

# Minion subclass:
class Minion(Card):
    def __init__(self, name, manaCost, attack, hp, effect, pic=None):
        super().__init__('minion', name, manaCost, effect, pic)
        self.attack = attack
        self.hp = hp
        self.effect = effect

# Spell subclass:
class Spell(Card):
    def __init__(self, name, manaCost, pic=None):
        super().__init__('spell', name, manaCost, effect=None, pic=pic)

# Weapon subclass:
class Weapon(Card):
    def __init__(self, name, manaCost, attack, durability, pic=None):
        super().__init__('weapon', name, manaCost, effect=None, pic=pic)
        self.attack = attack