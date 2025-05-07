# funktion for håndtering af minion death. Tjekker om minion er død, hvis ja, fjerner minion fra boardet og lægger i discard bunke.
def minion_death(minion, battle_state, discard_pile=None):
    if minion.hp <= 0:
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
    pass

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
        target_row.append(minion)
        minion.is_enemy = is_enemy
        minion.is_front_row = is_front_row
        
        # Activate any summon effects the minion might have
        minion.on_summon(battle_state)
            
        return True
    return False

# håndterer når en minion angriber noget
def perform_attack(attacker, target, battle_state, discard_pile=None):
    # checker for taunt
    if hasattr(target, 'is_enemy') and not can_attack_target(attacker, target, battle_state):
        return False
        
    # gør skade
    target.hp -= attacker.attack
    if hasattr(target, 'attack'):  # tager også selv skade
        attacker.hp -= target.attack
    
    # Checker for minion death
    if hasattr(target, 'is_enemy'):  # Target er en minion
        minion_death(target, battle_state, discard_pile)
    else:  # Target er en hero
        if target.hp <= 0:
            hero_death(target, battle_state)
            
    if hasattr(attacker, 'is_enemy'):  # kun check for minion death hvis det er en minion der bliver angrebet
        minion_death(attacker, battle_state, discard_pile)
    
    return True

# checker om en fjendtlig minion har taunt
def taunt_check(rows):
    for row in rows:
        for minion in row:
            if minion.has_taunt:
                return True
    return False

# checker om minion kan angribe (baseret på taunt_check())
def can_attack_target(attacker, target, battle_state):
    if not target.is_enemy:  # kan ikke angribe egne minions
        return False
        
    has_taunt = taunt_check([battle_state.enemy_front_row, battle_state.enemy_back_row])
    if has_taunt:
        # kan kun angribe minions med taunt hvis en fjendlig minion har taunt
        return target.has_taunt
    return True  # kan angribe alle fjender hvis ingen fjendlig minion har taunt

# funktion for brug af 'weapon' kort
def use_weapon(weapon, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    """Håndterer brug af et våben kort og tracker durability."""
    for row in [battle_state.enemy_front_row, battle_state.enemy_back_row]:
        for minion in row:
            if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                if taunt_check([battle_state.enemy_front_row, battle_state.enemy_back_row]) and not minion.has_taunt:
                    return False
                
                # gør skade på fjendlig minion og reducer durability med 1
                minion.hp -= weapon.attack
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
                minion.hp -= spell.attack
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
        self.is_player_turn = True # True = spillerens tur, False = fjendens tur
        self.player_screen = player_screen
        self.enemy = enemy

    # funktion der bliver kaldt når spilleren ender sin tur
    def end_player_turn(self):
        # trækker et kort fra bunken
        draw_card(self.player_screen.playerDeckPile, self.player_screen.playerHand)
        self.is_player_turn = False
        self.enemy.perform_turn()
        self.is_player_turn = True

    # funktion der checker om spilleren må spille et kort (ikke implementeret endnu)
    def can_play_card(self, card):
        return self.is_player_turn

    # funktion der checker hvis tur det er
    def get_current_player(self):
        return "player" if self.is_player_turn else "enemy"