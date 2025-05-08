# funktion for håndtering af minion death. Tjekker om minion er død, hvis ja, fjerner minion fra boardet og lægger i discard bunke.
def minion_death(minion, battle_state, discard_pile=None):
    if minion.current_hp <= 0:
        if minion.is_enemy:
            if minion in battle_state.enemy_front_row:
                battle_state.enemy_front_row.remove(minion)
            elif minion in battle_state.enemy_back_row:
                battle_state.enemy_back_row.remove(minion)
        else:  # Hvis ikke is_enemy, så er det en spiller-minion
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
def hero_death(hero, battle_state):
    if hero.current_hp <= 0:
        # Get the actual board state from the PlayMenu object if needed
        if hasattr(battle_state, 'battle_state'):
            battle_state = battle_state.battle_state
            
        # Clear the board
        battle_state.player_front_row.clear()
        battle_state.player_back_row.clear()
        battle_state.enemy_front_row.clear()
        battle_state.enemy_back_row.clear()
        return True
    return False

def enemy_death(enemy, battle_state):
    if enemy.current_hp <= 0:
        # Get the actual board state from the PlayMenu object if needed
        if hasattr(battle_state, 'battle_state'):
            battle_state = battle_state.battle_state
            
        # Clear the board
        battle_state.player_front_row.clear()
        battle_state.player_back_row.clear()
        battle_state.enemy_front_row.clear()
        battle_state.enemy_back_row.clear()
        return True
    return False

# trækker et kort hvis det er muligt
def draw_card(deck, hand, max_hand_size=7):
    if len(deck) > 0 and len(hand) < max_hand_size:
        card = deck.pop(0)
        hand.append(card)
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
        minion.has_taunt = False  # Reset taunt status before on_summon
        target_row.append(minion)
        
        # Activate any summon effects the minion might have
        if minion.on_summon:
            minion.on_summon(battle_state)
            
        return True
    return False

# håndterer når en minion angriber noget
def perform_attack(attacker, target, battle_state, discard_pile=None):
    # First check if target is valid based on taunt rules
    if not can_attack_target(attacker, target, battle_state):
        return False
        
    # Check if target is an enemy (do this after taunt check)
    if hasattr(target, 'is_enemy'):
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe allierede
            return False
    else:  # target er en hero
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egen hero
            return False
            
    # gør skade
    target.current_hp -= attacker.attack
    if hasattr(target, 'attack'):  # tager også selv skade
        attacker.current_hp -= target.attack
    
    # Checker for minion death
    if hasattr(target, 'is_enemy'):  # Target er en minion
        minion_death(target, battle_state, discard_pile)
    else:  # Target er en hero
        if target.current_hp <= 0:
            hero_death(target, battle_state)
    if hasattr(attacker, 'is_enemy'):  # kun check for minion death hvis det er en minion der bliver angrebet
        minion_death(attacker, battle_state, discard_pile)
    
    return True

# checker om en minion har taunt
def taunt_check(battle_state, attacker):
    # Check the appropriate rows based on who is attacking
    if attacker.is_enemy:  # If enemy is attacking, check player rows
        rows = [battle_state.player_front_row, battle_state.player_back_row]
    else:  # If player/weapon is attacking, check enemy rows
        rows = [battle_state.enemy_front_row, battle_state.enemy_back_row]
        
    for row in rows:
        for minion in row:
            if minion.has_taunt:
                return True
    return False

# checker om minion kan angribe (baseret på taunt_check())
def can_attack_target(attacker, target, battle_state):
    # Check for valid target first
    if hasattr(target, 'is_enemy'):  # if target is a minion
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egne minions
            return False
    else:  # if target is a hero
        if target.is_enemy == attacker.is_enemy:  # kan ikke angribe egen hero
            return False
    
    # Get the appropriate rows to check for taunt based on who's attacking
    if attacker.is_enemy:  # If enemy is attacking, check player rows
        rows_to_check = [battle_state.player_front_row, battle_state.player_back_row]
    else:  # If player is attacking, check enemy rows
        rows_to_check = [battle_state.enemy_front_row, battle_state.enemy_back_row]
        
    # Check if there are any taunt minions
    has_taunt = False
    for row in rows_to_check:
        for minion in row:
            if minion.has_taunt:
                has_taunt = True
                break
        if has_taunt:
            break
            
    # If there's no taunt, can attack anything
    if not has_taunt:
        return True
        
    # If there is taunt, can only attack taunt minions
    if hasattr(target, 'is_enemy'):  # If target is a minion
        return target.has_taunt
    else:  # If target is a hero
        return False  # Can't attack hero if there's taunt

# funktion for brug af 'weapon' kort
def use_weapon(weapon, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    """Håndterer brug af et våben kort og tracker durability."""
    # Check for taunt
    has_taunt = taunt_check(battle_state, weapon)
    
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
                
                # retuner 'weapon' kort til hånden hvis durability er 1 eller derover
                if weapon.durability <= 0:
                    player_discard.append(weapon)
                else:
                    pass
                
                return True
    return False

# funktion for brug af 'minion' kort
def use_minion(minion, mouse_x, mouse_y, battle_state, front_row_zone, back_row_zone):
    if front_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, True)
    elif back_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, False)
    return False

# funktion for brug af 'spell' kort
def use_spell(spell, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    # Hvis spell har en custom effekt, brug den
    if hasattr(spell, 'use_effect'):
        if spell.use_effect(battle_state, spell, enemy_discard, player_discard):
            player_discard.append(spell)
            return True
        return False

    # Normal spell håndtering for andre spells
    spell_used = False
    for row in [battle_state.enemy_front_row, battle_state.enemy_back_row]:
        for minion in row:
            if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                minion.current_hp -= spell.attack
                spell_used = True
                player_discard.append(spell)
                minion_death(minion, battle_state, enemy_discard)
                break
        if spell_used:
            break
    return spell_used

# class for håndtering af hvis tur det er
class TurnManager:
    def __init__(self, player_screen, enemy):
        self.is_player_turn = True  # True = spillerens tur, False = fjendens tur
        self.player_screen = player_screen
        self.enemy = enemy
        self.current_mana = 1  # Start with 1 mana
        self.max_mana = 1
        self.spent_mana = 0

    # funktion der bliver kaldt når spilleren ender sin tur
    def end_player_turn(self):
        # trækker et kort fra bunken
        draw_card(self.player_screen.playerDeckPile, self.player_screen.playerHand)
        self.is_player_turn = False
        self.enemy.perform_turn()
        self.is_player_turn = True
        # Increase mana for next turn
        self.max_mana = min(10, self.max_mana + 1)
        self.current_mana = self.max_mana
        self.spent_mana = 0

    # funktion der checker om spilleren må spille et kort
    def can_play_card(self, card):
        return self.is_player_turn and card.manaCost <= self.current_mana

    # funktion der håndterer mana når et kort bliver spillet
    def spend_mana(self, amount):
        if amount <= self.current_mana:
            self.current_mana -= amount
            self.spent_mana += amount
            return True
        return False

    # funktion der checker hvis tur det er
    def get_current_player(self):
        return "player" if self.is_player_turn else "enemy"