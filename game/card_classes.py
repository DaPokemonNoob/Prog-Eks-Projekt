import pygame
from game_logic import perform_attack, minion_death, hero_death
from settings import CARD_WIDTH, CARD_HEIGHT

# Card superclass:
class Card:
    def __init__(self, category, name, mana_cost, effect, pic=None):
        self.category = category
        self.name = name
        self.mana_cost = mana_cost
        self.effect = effect
        self.pic = pic

# Hero subclass:
class Hero(Card):
    def __init__(self, name, attack, max_hp, is_enemy=False, pic=None):
        super().__init__('hero', name, mana_cost=0, effect=None, pic=pic)
        self.attack = attack
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.is_enemy = is_enemy
        self.has_taunt = False
        self.position = (0, 0)  # Default position, to be set when the hero is initialized
        self.image = pygame.image.load(f"assets/playingCard/{pic}").convert_alpha() if pic else None

# Minion subclass:
class Minion(Card):
    def __init__(self, name, mana_cost, attack, max_hp, effect, pic=None):
        super().__init__('minion', name, mana_cost, effect, pic)
        self.attack = attack
        self.base_attack = attack
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.effect = effect
        self.is_selected_for_attack = False
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.image.load(f"assets/playingCard/{pic}").convert_alpha() if pic else None
        self.is_enemy = False
        self.is_front_row = False
        self.pic = pic
        self.has_taunt = False
        self.rest = True  # Minions start in rest state
        self.on_summon = lambda battle_state: None
        self.position = (0, 0)  # Default position, to be set when added to the board

    # funktion til at checke om musen er over en minion på boardet
    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    # funktion til at minion angriber
    def perform_attack(self, target, battle_state, playmenu_draw_function):
        if self.is_selected_for_attack and target and not self.rest:  # Only allow attack if not resting
            if perform_attack(self, target, battle_state, playmenu_draw_function=playmenu_draw_function):
                self.is_selected_for_attack = False
                self.rest = True  # Set to rest after successful attack
                return True
        return False

    # funktion til at select en minion til at angribe
    def selected(self):
        if self.check_hover() and pygame.mouse.get_pressed()[0] and not self.rest:  # Only allow selection if not resting
            self.is_selected_for_attack = not self.is_selected_for_attack
            return self

    # funktion til at give alle minions på boardet +1 attack
    def buff_allies(self, battle_state):
        """Apply buff effect to all friendly minions on board"""
        if self.name == "Some Cool Guy":
            rows = [battle_state.player_front_row, battle_state.player_back_row] if not self.is_enemy else [battle_state.enemy_front_row, battle_state.enemy_back_row]
            for row in rows:
                for minion in row:
                    if minion != self:  # don't buff self again
                        minion.attack += 1

# spell subclass:
class Spell(Card):
    def __init__(self, name, mana_cost, attack, activationTimes=1, effect=None, pic=None):
        super().__init__('spell', name, mana_cost, effect, pic)
        self.attack = attack
        self.activationTimes = activationTimes

# weapon subclass:
class Weapon(Card):
    def __init__(self, name, mana_cost, attack, durability, pic=None):
        super().__init__('weapon', name, mana_cost, effect=None, pic=pic)
        self.attack = attack
        self.durability = durability
        self.is_enemy = False  # Weapons are always controlled by the player

# klasse der tracker minions på boardet
class BoardState:
    def __init__(self):
        self.enemy_front_row = []  # max 2 minions
        self.enemy_back_row = []   # max 3 minions
        self.player_front_row = [] # max 2 minions
        self.player_back_row = []  # max 3 minions
        self.turn_manager = None
        
    def set_turn_manager(self, turn_manager):
        self.turn_manager = turn_manager

    # funktion til at tilføje en minion til boardet
    def add_minion(self, minion, is_enemy, is_front_row):
        target_row = None
        if is_enemy:
            target_row = self.enemy_front_row if is_front_row else self.enemy_back_row
        else:
            target_row = self.player_front_row if is_front_row else self.player_back_row
            
        # Check max minions
        max_minions = 2 if is_front_row else 3
        if len(target_row) < max_minions:
            minion.is_enemy = is_enemy
            minion.is_front_row = is_front_row
            minion.has_taunt = False  # Reset taunt before on_summon
            target_row.append(minion)
            
            # Call on_summon effect after setting properties
            if minion.on_summon:
                minion.on_summon(self)
            return True
        return False
    
    # funktion til at håndtere klik på minions
    def handle_minion_click(self, clicked_minion, playmenu_draw_function):
        selected_minion = None
        for row in [self.player_front_row, self.player_back_row]:
            for minion in row:
                if minion.is_selected_for_attack:
                    selected_minion = minion
                    break
            if selected_minion:
                break

        # If a hero was clicked
        if isinstance(clicked_minion, Hero):
            if clicked_minion.is_enemy and selected_minion:
                selected_minion.perform_attack(clicked_minion, self, playmenu_draw_function=playmenu_draw_function)
                return True
            return False
            
        # If a minion was clicked
        if clicked_minion.is_enemy and selected_minion:
            selected_minion.perform_attack(clicked_minion, self, playmenu_draw_function=playmenu_draw_function)
            return True
        elif not clicked_minion.is_enemy:
            if selected_minion and selected_minion != clicked_minion:
                selected_minion.is_selected_for_attack = False
            clicked_minion.selected()
            return True
        return False