import pygame

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
        super().__init__('hero', name, manaCost=0, effect=None, pic=pic)
        self.attack = attack
        self.hp = hp

# Minion subclass:
class Minion(Card):
    all_minions = []  # Class variable to track all minions
    def __init__(self, name, manaCost, attack, hp, effect, pic=None):
        super().__init__('minion', name, manaCost, effect, pic)
        self.attack = attack
        self.hp = hp
        self.effect = effect
        self.is_selected = False
        self.image = None  # This should be set when the minion is placed on the board
        self.is_enemy = False
        self.is_front_row = False
        Minion.all_minions.append(self)  # Add this minion to the tracking list

    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    def selected(self):
        if self.check_hover() and pygame.mouse.get_pressed()[0]:
            self.is_selected = not self.is_selected
            return self

    def attack(self, target, battle_state):
        if self.is_selected and target:
            # Deal damage to target
            target.hp -= self.attack
            # Take damage from target if it's a minion
            if isinstance(target, Minion):
                self.hp -= target.attack
            # Handle minion death
            if target.hp <= 0:
                if target.is_enemy:
                    if target.is_front_row:
                        battle_state.enemy_front_row.remove(target)
                    else:
                        battle_state.enemy_back_row.remove(target)
                else:
                    if target.is_front_row:
                        battle_state.player_front_row.remove(target)
                    else:
                        battle_state.player_back_row.remove(target)
            if self.hp <= 0:
                if self.is_front_row:
                    battle_state.player_front_row.remove(self)
                else:
                    battle_state.player_back_row.remove(self)
            # Deselect after attack
            self.is_selected = False

# Spell subclass:
class Spell(Card):
    def __init__(self, name, manaCost, pic=None):
        super().__init__('spell', name, manaCost, effect=None, pic=pic)

# Weapon subclass:
class Weapon(Card):
    def __init__(self, name, manaCost, attack, durability, pic=None):
        super().__init__('weapon', name, manaCost, effect=None, pic=pic)
        self.attack = attack

class BoardState:
    def __init__(self):
        self.enemy_front_row = []  # max 2 minions
        self.enemy_back_row = []   # max 3 minions
        self.player_front_row = [] # max 2 minions
        self.player_back_row = []  # max 3 minions
        self.enemy_hero = None
        self.player_hero = None
        
    def add_minion(self, minion, is_enemy, is_front_row):
        target_row = None
        if is_enemy:
            target_row = self.enemy_front_row if is_front_row else self.enemy_back_row
        else:
            target_row = self.player_front_row if is_front_row else self.player_back_row
            
        max_minions = 2 if is_front_row else 3
        if len(target_row) < max_minions:
            target_row.append(minion)
            minion.is_enemy = is_enemy
            minion.is_front_row = is_front_row
            return True
        return False
    
    def handle_minion_click(self, clicked_minion):
        selected_minion = None
        # Find any currently selected minion
        for row in [self.player_front_row, self.player_back_row]:
            for minion in row:
                if minion.is_selected:
                    selected_minion = minion
                    break
            if selected_minion:
                break
                
        if clicked_minion.is_enemy and selected_minion:
            # Attack enemy minion
            selected_minion.attack(clicked_minion, self)
            return True
        elif not clicked_minion.is_enemy:
            # Select/deselect player minion
            if selected_minion and selected_minion != clicked_minion:
                selected_minion.is_selected = False
            clicked_minion.selected()
            return True
        return False