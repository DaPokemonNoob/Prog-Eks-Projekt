import pygame
from game_logic import perform_attack, add_minion_to_board

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
        self.base_attack = attack  # Store the original attack value
        self.hp = hp
        self.effect = effect
        self.is_selected_for_attack = False
        self.image = None
        self.is_enemy = False
        self.is_front_row = False
        self.pic = pic
        self._has_taunt = False
        self.on_summon = lambda battle_state: None  # Default empty on_summon handler
        Minion.all_minions.append(self)

    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    def selected(self):
        if self.check_hover() and pygame.mouse.get_pressed()[0]:
            self.is_selected_for_attack = not self.is_selected_for_attack
            return self

    def perform_attack(self, target, battle_state):
        if self.is_selected_for_attack and target:
            perform_attack(self, target, battle_state)
            self.is_selected_for_attack = False

    def buff_allies(self, battle_state):
        """Apply buff effect to all friendly minions on board"""
        if self.name == "Some Cool Guy":
            rows = [battle_state.player_front_row, battle_state.player_back_row] if not self.is_enemy else [battle_state.enemy_front_row, battle_state.enemy_back_row]
            for row in rows:
                for minion in row:
                    if minion != self:  # Don't buff self again
                        minion.attack += 1

# Spell subclass:
class Spell(Card):
    def __init__(self, name, manaCost, attack, activationTimes=1, effect=None, pic=None):
        super().__init__('spell', name, manaCost, effect, pic)
        self.attack = attack
        self.activationTimes = activationTimes

# Weapon subclass:
class Weapon(Card):
    def __init__(self, name, manaCost, attack, durability, pic=None):
        super().__init__('weapon', name, manaCost, effect=None, pic=pic)
        self.attack = attack
        self.durability = durability

class BoardState:
    def __init__(self):
        self.enemy_front_row = []  # max 2 minions
        self.enemy_back_row = []   # max 3 minions
        self.player_front_row = [] # max 2 minions
        self.player_back_row = []  # max 3 minions
        
    def add_minion(self, minion, is_enemy, is_front_row):
        return add_minion_to_board(minion, self, is_enemy, is_front_row)
    
    def handle_minion_click(self, clicked_minion):
        selected_minion = None
        for row in [self.player_front_row, self.player_back_row]:
            for minion in row:
                if minion.is_selected_for_attack:
                    selected_minion = minion
                    break
            if selected_minion:
                break
                
        if clicked_minion.is_enemy and selected_minion:
            selected_minion.perform_attack(clicked_minion, self)
            return True
        elif not clicked_minion.is_enemy:
            if selected_minion and selected_minion != clicked_minion:
                selected_minion.is_selected_for_attack = False
            clicked_minion.selected()
            return True
        return False