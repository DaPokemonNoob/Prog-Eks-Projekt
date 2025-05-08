import random
import pygame
import card_data as card
from card_classes import BoardState
from game_logic import minion_death, draw_card, add_minion_to_board, perform_attack, can_attack_target
from animations import play_attack_animation

# -----Enemy behaviour class-----
# enemy kan kun bruge minion kort og angribe med minion kort, det var også meningen
# at fjenden skulle kunne bruge spell og weapon kort og have en mere avanceret spilopførsel
class Enemy:
    def __init__(self, battle_state: BoardState):
        self.battle_state = battle_state
        self.deck_pile = [card.knight(), card.slimeling(), card.knight()] # fjendens dæk
        random.shuffle(self.deck_pile)                                    # blander dækket
        self.hand = []
        self.discard = []

    # fjendens draw_card function, bruger samme funktion som spillerens draw_card function fra game_logic.py
    def draw_card(self):
        return draw_card(self.deck_pile, self.hand, self.discard)

    # funktion der bliver kaldt når det bliver fjendens tur
    def perform_turn(self, screen, clock, playmenu_draw_function):
        # fjenden trækker et kort hver tur
        self.draw_card()
        
        # Sorter hånd efter mana_cost for at spille det billigste kort først
        self.hand.sort(key=lambda x: x.mana_cost)
        
        # prøver at placere minions
        if len(self.hand) > 0:
            # filtrer kort der kan blive spillet
            remaining_mana = self.battle_state.turn_manager.current_mana
            
            for card in self.hand[:]:  # kopi af liste
                if card.mana_cost <= remaining_mana:
                # prøver at fylde række 1 med minions (maks 2)
                    if len(self.battle_state.enemy_front_row) < 2:
                        if add_minion_to_board(card, self.battle_state, True, True):
                            self.hand.remove(card)
                            remaining_mana -= card.mana_cost
                            self.battle_state.turn_manager.spend_mana(card.mana_cost)
                    # prøver derefter at fylde række 2 med minions (maks 3)
                    elif len(self.battle_state.enemy_back_row) < 3:
                        if add_minion_to_board(card, self.battle_state, True, False):
                            self.hand.remove(card) 
                            remaining_mana -= card.mana_cost
                            self.battle_state.turn_manager.spend_mana(card.mana_cost)
        
        # først vil enemy minions i den forreste række angribe
        # vil først angribe fjendtlige minions i første række
        for attacking_minion in self.battle_state.enemy_front_row[:]:
            attacked = False
            for target in self.battle_state.player_front_row + self.battle_state.player_back_row:
                if can_attack_target(attacking_minion, target, self.battle_state):
                    # load minions image for animation
                    attacker_image = pygame.image.load(f"assets/playingCard/{attacking_minion.pic}").convert_alpha()
                    play_attack_animation(
                        screen,
                        clock,
                        (attacking_minion.position[0], attacking_minion.position[1]), # brug position tuple direkte
                        (target.position[0], target.position[1]),                     # brug position tuple direkte
                        attacker_image,
                        playmenu_draw_function)
                    perform_attack(attacking_minion, target, self.battle_state, self.discard)
                    attacked = True
                    break

            # hvis fjende ikke kan angribe minions, angrib spillerens hero
            if not attacked and can_attack_target(attacking_minion, self.battle_state.player_hero, self.battle_state):
                attacker_image = pygame.image.load(f"assets/playingCard/{attacking_minion.pic}").convert_alpha()
                play_attack_animation(
                    screen,
                    clock,
                    (attacking_minion.position[0], attacking_minion.position[1]),                           # brug position tuple direkte
                    (self.battle_state.player_hero.position[0], self.battle_state.player_hero.position[1]), # brug position tuple direkte
                    attacker_image,
                    playmenu_draw_function)
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)

        # derefter angriber enemy minions i den bagerste række
        # følger samme mønster som ovenfor
        for attacking_minion in self.battle_state.enemy_back_row[:]:
            attacked = False
            # vil først angribe fjendtlige minions i første række
            for target in self.battle_state.player_back_row + self.battle_state.player_back_row:
                if can_attack_target(attacking_minion, target, self.battle_state):
                    # load minions image for animation
                    attacker_image = pygame.image.load(f"assets/playingCard/{attacking_minion.pic}").convert_alpha()
                    play_attack_animation(
                        screen,
                        clock,
                        (attacking_minion.position[0], attacking_minion.position[1]), # brug position tuple direkte
                        (target.position[0], target.position[1]),                     # brug position tuple direkte
                        attacker_image,
                        playmenu_draw_function
                    )
                    perform_attack(attacking_minion, target, self.battle_state, self.discard)
                    attacked = True
                    break

        # hvis fjende ikke kan angribe minions, angrib spillerens hero
            if not attacked and can_attack_target(attacking_minion, self.battle_state.player_hero, self.battle_state):
                attacker_image = pygame.image.load(f"assets/playingCard/{attacking_minion.pic}").convert_alpha()
                play_attack_animation(
                    screen,
                    clock,
                    (attacking_minion.position[0], attacking_minion.position[1]),                           # brug position tuple direkte
                    (self.battle_state.player_hero.position[0], self.battle_state.player_hero.position[1]), # brug position tuple direkte
                    attacker_image,
                    playmenu_draw_function
                )
                perform_attack(attacking_minion, self.battle_state.player_hero, self.battle_state, self.discard)
