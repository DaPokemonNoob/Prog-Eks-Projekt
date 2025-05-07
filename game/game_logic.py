# funktion for håndtering af minion death. Tjekker om minion er død, hvis ja, fjerner minion fra boardet og lægger i discard pile.
def minion_death(minion, battle_state, discard_pile=None):
    """Håndterer når en minion dør. Fjerner minion fra boardet og lægger i discard pile."""
    if minion.hp <= 0:
        if minion.is_enemy:
            if minion.is_front_row:
                battle_state.enemy_front_row.remove(minion)
            else:
                battle_state.enemy_back_row.remove(minion)
        else:  # Hvis ikke is_enemy, så er det en spiller-minion
            if minion.is_front_row:
                battle_state.player_front_row.remove(minion)
            else:
                battle_state.player_back_row.remove(minion)
                
        if discard_pile is not None:
            discard_pile.append(minion)
        return True
    return False

def hero_death(hero, battle_state):
    """Håndterer når en hero dør."""
    pass

def draw_card(deck, hand, max_hand_size=7):
    """Draw a card from deck to hand if possible."""
    if len(deck) > 0 and len(hand) < max_hand_size:
        card = deck.pop(0)
        hand.append(card)
        return True
    return False

def add_minion_to_board(minion, battle_state, is_enemy, is_front_row):
    """Add a minion to the specified row on the board."""
    target_row = None
    if is_enemy:
        target_row = battle_state.enemy_front_row if is_front_row else battle_state.enemy_back_row
    else:
        target_row = battle_state.player_front_row if is_front_row else battle_state.player_back_row
        
    max_minions = 2 if is_front_row else 3
    if len(target_row) < max_minions:
        target_row.append(minion)
        minion.is_enemy = is_enemy
        minion.is_front_row = is_front_row
        
        # Activate any summon effects the minion might have
        minion.on_summon(battle_state)
            
        return True
    return False

def perform_attack(attacker, target, battle_state, discard_pile=None):
    """Handle combat between two units."""
    # Check if we can attack this target (taunt rules)
    if hasattr(target, 'is_enemy') and not can_attack_target(attacker, target, battle_state):
        return False
        
    # Deal damage
    target.hp -= attacker.attack
    if hasattr(target, 'attack'):  # If target can counter-attack
        attacker.hp -= target.attack
    
    # Check for deaths
    if hasattr(target, 'is_enemy'):  # Target is a minion
        minion_death(target, battle_state, discard_pile)
    else:  # Target is a hero
        if target.hp <= 0:
            hero_death(target, battle_state)
            
    if hasattr(attacker, 'is_enemy'):  # Only check minion death for minions
        minion_death(attacker, battle_state, discard_pile)
    
    return True

def taunt_check(rows):
    """Check if there are any minions with taunt in the given rows."""
    for row in rows:
        for minion in row:
            if minion.has_taunt:
                return True
    return False

def can_attack_target(attacker, target, battle_state):
    """Check if a target can be attacked based on taunt rules."""
    if not target.is_enemy:  # Can't attack friendly units
        return False
        
    has_taunt = taunt_check([battle_state.enemy_front_row, battle_state.enemy_back_row])
    if has_taunt:
        # If there's a taunt minion, can only attack units with taunt
        return target.has_taunt
    return True  # No taunt minions, can attack any target

def use_weapon(weapon, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    """Håndterer brug af et våben kort og tracker durability."""
    for row in [battle_state.enemy_front_row, battle_state.enemy_back_row]:
        for minion in row:
            if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                if taunt_check([battle_state.enemy_front_row, battle_state.enemy_back_row]) and not minion.has_taunt:
                    return False
                
                # Apply weapon damage
                minion.hp -= weapon.attack
                weapon.durability -= 1  # Reduce durability when weapon is used
                
                # Check if minion dies from the attack
                minion_death(minion, battle_state, enemy_discard)
                
                # Return weapon to hand if durability is 1 or more, otherwise discard it
                if weapon.durability <= 0:
                    player_discard.append(weapon)
                else:
                    pass
                
                return True
    return False

def use_minion(minion, mouse_x, mouse_y, battle_state, front_row_zone, back_row_zone):
    """Håndterer placering af en minion på brættet."""
    if front_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, True)
    elif back_row_zone.collidepoint(mouse_x, mouse_y):
        return battle_state.add_minion(minion, False, False)
    return False

def use_spell(spell, mouse_x, mouse_y, battle_state, enemy_discard, player_discard):
    """Håndterer brug af et spell kort."""
    # Hvis spell'en har en custom effekt, brug den
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

class TurnManager:
    """Manages game turns and tracks whose turn it is."""
    def __init__(self, player_screen, enemy):
        self.is_player_turn = True
        self.player_screen = player_screen
        self.enemy = enemy

    def end_player_turn(self):
        """End the player's turn and start enemy turn."""
        # Draw a card for next turn
        draw_card(self.player_screen.playerDeckPile, self.player_screen.playerHand)
        self.is_player_turn = False
        self.enemy.perform_turn()
        self.is_player_turn = True

    def can_play_card(self, card):
        """Check if a card can be played (correct turn, enough mana, etc)."""
        return self.is_player_turn  # For now just check turn, can add mana check later

    def get_current_player(self):
        """Get who's turn it currently is."""
        return "player" if self.is_player_turn else "enemy"