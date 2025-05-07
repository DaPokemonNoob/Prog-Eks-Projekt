import random
import pygame
import card_data as card
import effects_data as effect
from card_classes import BoardState
from game_logic import minion_death, draw_card, add_minion_to_board, perform_attack

class Enemy:
    def __init__(self, battle_state: BoardState):
        self.battle_state = battle_state
        self.deck_pile = [card.knight(), card.someGuy(), card.someCoolGuy(), card.knight()]
        random.shuffle(self.deck_pile)
        self.hand = []
        self.discard = []

    def draw_card(self):
        return draw_card(self.deck_pile, self.hand)
# kill yourself github, please i hate you
    def perform_turn(self):
        # Draw a card for the enemy
        self.draw_card()
        
        # Try to place minions strategically
        if len(self.hand) > 0:
            # First try to fill front row (max 2)
            if len(self.battle_state.enemy_front_row) < 2:
                enemy_minion = self.hand.pop(0)
                add_minion_to_board(enemy_minion, self.battle_state, True, True)
            # Then try to fill back row (max 3)
            elif len(self.battle_state.enemy_back_row) < 3:
                enemy_minion = self.hand.pop(0)
                add_minion_to_board(enemy_minion, self.battle_state, True, False)
        
        # Enemy minion attacks - first front row
        for attacking_minion in self.battle_state.enemy_front_row[:]:  # Create a copy of the list to iterate
            if not self.battle_state.player_front_row:
                # Attack enemy hero if no minions
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)
            elif self.battle_state.player_front_row:
                # Attack first player minion
                target = self.battle_state.player_front_row[0]
                perform_attack(attacking_minion, target, self.battle_state, self.discard)

        # Then back row attacks
        for attacking_minion in self.battle_state.enemy_back_row[:]:
            if not self.battle_state.player_front_row:
                # Attack enemy hero if no minions
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)
            elif self.battle_state.player_front_row:
                # Attack first player minion
                target = self.battle_state.player_front_row[0]
                perform_attack(attacking_minion, target, self.battle_state, self.discard)