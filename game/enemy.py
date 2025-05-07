import pygame
import card_data as card
import effects_data as effect
from card_classes import BoardState

class Enemy:
    def __init__(self, battle_state: BoardState):
        self.battle_state = battle_state
        self.deck_pile = [card.knight(), card.someGuy(), card.someCoolGuy(), card.knight()]
        self.hand = []      # index af fjendens hånd. Den har ikke et specielt navn da den bliver initialiseret separat fra spillerens hånd
        self.discard = []   # index af fjendens discard pile. Den har ikke et specielt navn da den bliver initialiseret separat fra spillerens discard pile

    def draw_card(self):
        if len(self.deck_pile) > 0 and len(self.hand) < 7:
            enemy_minion = self.deck_pile.pop(0)
            self.hand.append(enemy_minion)
            return True
        return False

    def perform_turn(self):
        # Træk et kort for fjenden
        self.draw_card()
        
        # Prøv at placere minions strategisk
        if len(self.hand) > 0:
            # Først prøv at fylde forreste række (max 2)
            if len(self.battle_state.enemy_front_row) < 2:
                enemy_minion = self.hand.pop(0)
                self.battle_state.add_minion(enemy_minion, True, True)
            # Derefter prøv at fylde bagerste række (max 3)
            elif len(self.battle_state.enemy_back_row) < 3:
                enemy_minion = self.hand.pop(0)
                self.battle_state.add_minion(enemy_minion, True, False)
        
        # Fjendens angreb med minions
        for attacking_minion in self.battle_state.enemy_front_row:
            if not self.battle_state.player_front_row:
                # Angrib modstander helt hvis ingen minions
                self.battle_state.player_hero.hp -= attacking_minion.attack
            elif self.battle_state.player_front_row:
                # Angrib første spiller minion og tag skade tilbage
                target = self.battle_state.player_front_row[0]
                target.hp -= attacking_minion.attack
                attacking_minion.hp -= target.attack
                
                # Håndter minion død
                if attacking_minion.hp <= 0:
                    self.battle_state.enemy_front_row.remove(attacking_minion)
                    self.discard.append(attacking_minion)
                if target.hp <= 0:
                    self.battle_state.player_front_row.remove(target)
                    # Bemærk: Spillerens discard bunke håndteres af PlayMenu