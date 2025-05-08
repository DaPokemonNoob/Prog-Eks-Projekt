import random
import pygame
import card_data as card
import effects_data as effect
from card_classes import BoardState
from game_logic import minion_death, draw_card, add_minion_to_board, perform_attack, can_attack_target

class Enemy:
    def __init__(self, battle_state: BoardState):
        self.battle_state = battle_state
        self.deck_pile = [card.knight(), card.slimeling(), card.someCoolGuy(), card.knight(), card.fireball()]
        random.shuffle(self.deck_pile)
        self.hand = []
        self.discard = []

    def draw_card(self):
        return draw_card(self.deck_pile, self.hand)

    def perform_turn(self):
        # fjenden trækker et kort hver tur
        self.draw_card()
        
        # prøver at placere minions
        if len(self.hand) > 0:
            # prøver at fylde række 1 med minions (maks 2)
            if len(self.battle_state.enemy_front_row) < 2:
                enemy_minion = self.hand.pop(0)
                add_minion_to_board(enemy_minion, self.battle_state, True, True)
            # prøver derefter at fylde række 2 med minions (maks 3)
            elif len(self.battle_state.enemy_back_row) < 3:
                enemy_minion = self.hand.pop(0)
                add_minion_to_board(enemy_minion, self.battle_state, True, False)
        
        # fjendens minions angriber - først angriber minions i første række
        for attacking_minion in self.battle_state.enemy_front_row[:]:  # copy af liste
            # Try to attack taunt minions first
            attacked = False
            
            # First try to attack player's minions
            for target in self.battle_state.player_front_row + self.battle_state.player_back_row:
                if can_attack_target(attacking_minion, target, self.battle_state):
                    perform_attack(attacking_minion, target, self.battle_state, self.discard)
                    attacked = True
                    break
                    
            # If no valid minion targets (or no minions with taunt when taunt exists)
            if not attacked and can_attack_target(attacking_minion, self.battle_state.player_hero, self.battle_state):
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)

        # anden række angriber bagefter med samme logik
        for attacking_minion in self.battle_state.enemy_back_row[:]:
            attacked = False
            
            # First try to attack player's minions
            for target in self.battle_state.player_front_row + self.battle_state.player_back_row:
                if can_attack_target(attacking_minion, target, self.battle_state):
                    perform_attack(attacking_minion, target, self.battle_state, self.discard)
                    attacked = True
                    break
                    
            # If no valid minion targets (or no minions with taunt when taunt exists)
            if not attacked and can_attack_target(attacking_minion, self.battle_state.player_hero, self.battle_state):
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)