from animations import play_attack_animation
from settings import *
import pygame
import random
import card_data as card

# funktion for håndtering af minion death. Tjekker om minion er død, hvis ja, fjerner minion fra boardet og lægger i discard bunke.
def minion_death(minion, battle_state, discard_pile=None):
    if minion.current_hp <= 0:
        if minion.is_enemy:
            if minion in battle_state.enemy_front_row:
                battle_state.enemy_front_row.remove(minion)
            elif minion in battle_state.enemy_back_row:
                battle_state.enemy_back_row.remove(minion)
        else:  # hvis ikke is_enemy, så er det en spiller-minion
            if minion in battle_state.player_front_row:
                battle_state.player_front_row.remove(minion)
            elif minion in battle_state.player_back_row:
                battle_state.player_back_row.remove(minion)
        # discarder minion hvis dens hp <= 0
        if discard_pile is not None:
            discard_pile.append(minion)
        return True
    return False

# håndterer hero death
def hero_death(hero, play_menu):
    if hero.current_hp <= 0:
        # Get the actual board state from the PlayMenu object
        battle_state = play_menu.battle_state
            
        # clear board
        battle_state.player_front_row.clear()
        battle_state.player_back_row.clear()
        battle_state.enemy_front_row.clear()
        battle_state.enemy_back_row.clear()

        return True
    return False

def enemy_death(enemy, play_menu):
    if enemy.current_hp <= 0:
        # get the actual board state from the PlayMenu object
        battle_state = play_menu.battle_state
            
        # clear board
        battle_state.player_front_row.clear()
        battle_state.player_back_row.clear()
        battle_state.enemy_front_row.clear()
        battle_state.enemy_back_row.clear()

        return True
    return False

# håndterer tilføjelse af minion til boardet
def add_minion_to_board(minion, battle_state, is_enemy, is_front_row):
    target_row = None
    if is_enemy:
        target_row = battle_state.enemy_front_row if is_front_row else battle_state.enemy_back_row
    else:
        target_row = battle_state.player_front_row if is_front_row else battle_state.player_back_row
    
    # hvis første række, max antal minions er 2, hvis ikke første række, er det anden række, og derfor max antal minion er 3
    max_minions = 2 if is_front_row else 3
    if len(target_row) < max_minions:
        minion.is_enemy = is_enemy
        minion.is_front_row = is_front_row
        minion.has_taunt = False  # reset taunt status før summon
        target_row.append(minion)
        
        # udregn position baseret på række
        row_y = 100 if is_front_row else 200  # eksempel Y-coordinater
        column_x = 100 + len(target_row) * (CARD_WIDTH + 20)  # eksempel X-coordinater
        minion.position = (column_x, row_y)  # giv position til minion
        
        # aktiver summon effekt, hvis denne findes
        if minion.on_summon:
            minion.on_summon(battle_state)
            
        return True
    return False

# håndterer når en minion angriber noget
def perform_attack(attacker, target, battle_state, discard_pile=None, playmenu_draw_function=None):
    # først check om target er valid baseret på taunt check
    if not can_attack_target(attacker, target, battle_state):
        return False
        
    # check om target er en fjende
    if hasattr(target, 'is_enemy'):
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe allierede
            return False
    else:  # target er en hero
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egen hero
            return False

    # loader billede
    if isinstance(attacker.pic, str):
        attacker_image = pygame.image.load(f"assets/playingCard/{attacker.pic}").convert_alpha()
    else:
        attacker_image = attacker.pic

    # attack animation
    if hasattr(attacker, 'image') and attacker.image and hasattr(target, 'image') and target.image:
        attacker_pos = (attacker.image.x, attacker.image.y)
        target_pos = (target.image.x, target.image.y)
        if playmenu_draw_function:
            play_attack_animation(SCREEN, clock, attacker_pos, target_pos, attacker_image, playmenu_draw_function)
            
    # gør skade
    target.current_hp -= attacker.attack
    if hasattr(target, 'attack'):  # tager også selv skade
        attacker.current_hp -= target.attack
    
    # checker for minion death
    if hasattr(target, 'is_enemy'):  # Target er en minion
        minion_death(target, battle_state, discard_pile)
    else:  # target er en hero
        if target.current_hp <= 0:
            hero_death(target, battle_state)
    if hasattr(attacker, 'is_enemy'):  # kun check for minion death hvis det er en minion der bliver angrebet
        minion_death(attacker, battle_state, discard_pile)
    
    return True

# checker om en minion har taunt
def taunt_check(battle_state, attacker):
    if attacker.is_enemy:  # hvis fjendlig minion angriber, check player rækker
        rows = [battle_state.player_front_row, battle_state.player_back_row]
    else:  # hvis spilleren bruger weapon, check enemy rækker
        rows = [battle_state.enemy_front_row, battle_state.enemy_back_row]
    
    # hvis taunt bliver fundet, return True. Hvis ikke, return False
    for row in rows:
        for minion in row:
            if minion.has_taunt:
                return True
    return False

# checker om minion kan angribe (baseret på taunt_check())
def can_attack_target(attacker, target, battle_state):
    # Check for valid target først
    if hasattr(target, 'is_enemy'):  # om target er en minion
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egne minions
            return False
    else:  # om target er en hero
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egen hero
            return False
    
    # hvis fjendtlig minion angriber, tjekkes spillerens rækker for taunt
    if attacker.is_enemy:
        rows_to_check = [battle_state.player_front_row, battle_state.player_back_row]
    else:  # hvis spillerens minion angriber, tjekkes fjendens rækker for taunt
        rows_to_check = [battle_state.enemy_front_row, battle_state.enemy_back_row]
        
    # check om der er taunt minions
    has_taunt = False
    for row in rows_to_check:
        for minion in row:
            if minion.has_taunt:
                has_taunt = True
                break
        if has_taunt:
            break
            
    # hvis taunt ikke kan findes, kan minions target alting
    if not has_taunt:
        return True
        
    # hvis taunt findes, kan minions kun target fjender med taunt
    if hasattr(target, 'is_enemy'):  # om target er en minion
        return target.has_taunt
    else:  # om target er en hero
        return False

# funktion for brug af 'weapon' kort
def use_weapon(weapon, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    # check for taunt
    has_taunt = taunt_check(battle_state, weapon)
    
    # Check for enemy hero click first
    if not has_taunt and battle_state.enemy_hero.image and battle_state.enemy_hero.image.collidepoint(mouse_x, mouse_y):
        battle_state.enemy_hero.current_hp -= weapon.attack
        weapon.durability -= 1
        
        # Check weapon durability - discard if 0 or below
        if weapon.durability <= 0:
            player_discard.append(weapon)
        
        return True
    
    # Then check enemy minions
    for row in [battle_state.enemy_front_row, battle_state.enemy_back_row]:
        for minion in row:
            if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                # If there's a taunt minion, can only attack taunt minions
                if has_taunt and not minion.has_taunt:
                    return False
                
                # gør skade på fjendlig minion og reducer durability med 1
                minion.current_hp -= weapon.attack
                weapon.durability -= 1
                
                # checker om minion dør efter angrebet
                minion_death(minion, battle_state, enemy_discard)
                
                # Check weapon durability - discard if 0 or below
                if weapon.durability <= 0:
                    player_discard.append(weapon)
                
                return True
    return False

# funktion for summon af 'minion' kort
def use_minion(minion, mouse_x, mouse_y, battle_state, front_row_zone, back_row_zone):
    if front_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, True)
    elif back_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, False)
    return False

# funktion for brug af 'spell' kort
def use_spell(spell, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    # hvis spell har en custom effekt, brug den
    if hasattr(spell, 'use_effect'):
        if spell.use_effect(battle_state, spell, enemy_discard, player_discard):
            player_discard.append(spell)
            return True
        return False

    # check om spell bliver brugt på fjendlig hero
    if battle_state.enemy_hero.image and battle_state.enemy_hero.image.collidepoint(mouse_x, mouse_y):
        battle_state.enemy_hero.current_hp -= spell.attack
        player_discard.append(spell)
        return True

    # normal spell håndtering for andre spells
    for row in [battle_state.enemy_front_row, battle_state.enemy_back_row]:
        for minion in row:
            if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                minion.current_hp -= spell.attack
                player_discard.append(spell)
                minion_death(minion, battle_state, enemy_discard)
                return True
    return False

# class for håndtering af hvis tur det er
class TurnManager:
    def __init__(self, play_menu, enemy, draw_function):
        self.play_menu = play_menu
        self.enemy = enemy
        self.draw_function = draw_function
        self.is_player_turn = True  # True = spillerens tur, False = fjendens tur
        self.current_mana = 1  # start med 1 mana
        self.max_mana = 1
        self.spent_mana = 0

    # funktion der bliver kaldt når spilleren ender sin tur
    def end_player_turn(self):
        # reset alle minions' rest variabel
        for row in [self.play_menu.battle_state.player_front_row, 
                   self.play_menu.battle_state.player_back_row,
                   self.play_menu.battle_state.enemy_front_row,
                   self.play_menu.battle_state.enemy_back_row]:
            for minion in row:
                minion.rest = False
        draw_card(self.play_menu.playerDeckPile, self.play_menu.playerHand, self.play_menu.playerDiscard)
        self.is_player_turn = False
        self.enemy.perform_turn(SCREEN, self.play_menu.clock, self.draw_function)
        self.is_player_turn = True
        # øg max_mana til næste tur
        self.max_mana = min(10, self.max_mana + 1)
        self.current_mana = self.max_mana
        self.spent_mana = 0

    # funktion der checker om spilleren må spille et kort
    def can_play_card(self, card):
        return self.is_player_turn and card.mana_cost <= self.current_mana

    # funktion der bruger mana når et kort bliver spillet
    def spend_mana(self, amount):
        if amount <= self.current_mana:
            self.current_mana -= amount
            self.spent_mana += amount
            return True
        return False

    # funktion der checker hvis tur det er
    def get_current_player(self):
        return "player" if self.is_player_turn else "enemy"

# funktion der bliver kaldt når en kamp starter
def battle_start(play_menu):
    # reset alle rækker
    play_menu.battle_state.player_front_row.clear()
    play_menu.battle_state.player_back_row.clear()
    play_menu.battle_state.enemy_front_row.clear()
    play_menu.battle_state.enemy_back_row.clear()
    
    # reset mana til 1
    play_menu.turn_manager.max_mana = 1
    play_menu.turn_manager.current_mana = 1
    
    # flyt alle kort til discard
    play_menu.playerDiscard.extend(play_menu.playerHand)
    play_menu.playerHand.clear()
    
    # gendan dæk til original tilstand
    play_menu.playerDeckPile = [card.knight(), card.knight(), card.slimeling(), 
                               card.slimeling(), card.slimeling(), card.chaosCrystal(), 
                               card.fireball(), card.fireball(), card.sword(), card.sword()]
    
    # shuffle dæk
    random.shuffle(play_menu.playerDeckPile)
    
    # træk 4 kort til playerHand i starten af kampen
    for _ in range(4):
        draw_card(play_menu.playerDeckPile, play_menu.playerHand, play_menu.playerDiscard)

# trækker et kort hvis det er muligt. Hvis der ikke er flere kort i deck, tager den kort fra discard
def draw_card(deck, hand, discard, max_hand_size=7):
    # hvis dæk er tomt og der er kort i discard, flyt kortene fra discard til dæk og shuffle
    if len(deck) == 0 and len(discard) > 0:
        deck.extend(discard)
        discard.clear()
        random.shuffle(deck)
    
    # prøv at trække et kort hvis der er kort tilbage og hånden ikke er fuld
    if len(deck) > 0 and len(hand) < max_hand_size:
        card = deck.pop(0)
        # reset kort stats
        if hasattr(card, 'max_hp'):  # for minions
            card.current_hp = card.max_hp
        if hasattr(card, 'durability'):  # for weapons
            card.durability = card.base_durability if hasattr(card, 'base_durability') else card.durability
        hand.append(card)
        return True
    return False