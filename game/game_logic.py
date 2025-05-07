def handle_minion_death(minion, battle_state, discard_pile=None):
    """Handle the death of a minion or hero by removing it from the board and optionally adding it to a discard pile."""
    if minion.hp <= 0:
        # Handle Hero deaths differently from Minions
        if not hasattr(minion, 'is_enemy'):  # This is a Hero
            return False  # Heroes can't be discarded or removed
            
        # Handle Minion deaths
        if minion.is_enemy:
            if minion.is_front_row:
                battle_state.enemy_front_row.remove(minion)
            else:
                battle_state.enemy_back_row.remove(minion)
        else:
            if minion.is_front_row:
                battle_state.player_front_row.remove(minion)
            else:
                battle_state.player_back_row.remove(minion)
                
        if discard_pile is not None:
            discard_pile.append(minion)
        return True
    return False

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
        return True
    return False

def perform_attack(attacker, target, battle_state, discard_pile=None):
    """Handle combat between two units."""
    # Deal damage
    target.hp -= attacker.attack
    if hasattr(target, 'attack'):  # If target can counter-attack
        attacker.hp -= target.attack
    
    # Check for deaths
    handle_minion_death(target, battle_state, discard_pile)
    if hasattr(attacker, 'is_enemy'):  # Only check minion death for minions
        handle_minion_death(attacker, battle_state, discard_pile)

def has_taunt_minion(rows):
    """Check if there are any valid taunt minions in the given rows."""
    for row in rows:
        for minion in row:
            if (hasattr(minion, 'effect') and minion.effect and 
                'Taunt' in minion.effect and 
                (minion.name != 'Knight' or minion.is_front_row)):  # Only count Knight's taunt if in front row
                return True
    return False

def cast_spell(spell, target, battle_state, caster_discard):
    """Cast a spell on a target."""
    if not hasattr(target, 'hp'):
        return False
        
    target.hp -= spell.attack
    if handle_minion_death(target, battle_state):
        caster_discard.append(spell)
        return True
    return False

def use_weapon(weapon, target, battle_state, caster_discard, enemy_discard):
    """Use a weapon on a target."""
    if not hasattr(target, 'hp'):
        return False
        
    target.hp -= weapon.attack
    if handle_minion_death(target, battle_state, enemy_discard):
        caster_discard.append(weapon)
        return True
    return False

def can_attack_target(attacker, target, battle_state):
    """Check if a target can be attacked based on taunt rules."""
    if not target.is_enemy:  # Can't attack friendly units
        return False
        
    has_taunt = has_taunt_minion([battle_state.enemy_front_row, battle_state.enemy_back_row])
    if has_taunt:
        # If there's a taunt minion, can only attack units with taunt
        return (hasattr(target, 'effect') and target.effect and 
                'Taunt' in target.effect and 
                (target.name != 'Knight' or target.is_front_row))
    return True  # No taunt minions, can attack any target

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