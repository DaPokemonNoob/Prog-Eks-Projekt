from card_classes import Minion, Spell, Weapon, Hero
import effects_data as effect
from game_logic import minion_death, hero_death

# Minion kort:
def slimeling():
    return Minion("Some Guy", manaCost=2, attack=2, hp=5, effect=None, pic="slimeling.png")

def someCoolGuy():
    minion = Minion("Some Cool Guy", manaCost=5, attack=4, hp=6, 
                    effect="When summoned: increase all ally Minions attack by 1.")
    def custom_on_summon(battle_state):
        rows = [battle_state.player_front_row, battle_state.player_back_row] if not minion.is_enemy else [battle_state.enemy_front_row, battle_state.enemy_back_row]
        for row in rows:
            for other_minion in row:
                if other_minion != minion:  # Don't buff self
                    other_minion.attack += 1
                    
    minion.on_summon = custom_on_summon
    return minion

def knight():
    armor_amount = effect.armor(2)
    minion = Minion("Knight", manaCost=3, attack=1, hp=7 + armor_amount, effect="When summoned: gain 2 armor. Has taunt if placed in front row.", pic="knight.png")
    minion.has_taunt = True
    return minion
    
# Hero kort:
def adventurer():   # Den hero spilleren bruger
    return Hero("Adventurer", attack=1, hp=15)

def evilGuy():      # Den hero fjenden bruger
    return Hero("Evil Guy", attack=1, hp=15)

# Spell kort:
def fireball():
    return Spell("Fireball", manaCost=4, attack=2)

def chaosCrystal():
    spell = Spell("Chaos Crystal", manaCost=2, attack=1, activationTimes=5, effect="Deals 5 damage randomly split among all Minions and Heroes.", pic ="chaoscrystal.png")
    
    def custom_spell_effect(battle_state, spell, enemy_discard, player_discard):
        import random
        # Samler alle mulige targets (minions og heroes)
        possible_targets = []
        possible_targets.extend(battle_state.enemy_front_row)
        possible_targets.extend(battle_state.enemy_back_row)
        possible_targets.extend(battle_state.player_front_row)
        possible_targets.extend(battle_state.player_back_row)
        possible_targets.append(battle_state.enemy_hero)
        possible_targets.append(battle_state.player_hero)
        
        # Fjern døde targets
        possible_targets = [target for target in possible_targets if target.hp > 0]
        
        if possible_targets:
            # Aktiver 5 gange med random target hver gang
            for _ in range(spell.activationTimes):
                if possible_targets:  # Check igen i tilfælde af at nogle targets er døde
                    target = random.choice(possible_targets)
                    target.hp -= spell.attack
                    # Tjek for død efter hver aktivering
                    if hasattr(target, 'is_enemy'):  # Er det en minion
                        if minion_death(target, battle_state, enemy_discard if target.is_enemy else player_discard):
                            possible_targets.remove(target)
                    elif target.hp <= 0:  # Er det en hero
                        hero_death(target, battle_state)
            return True
        return False
        
    spell.use_effect = custom_spell_effect
    return spell

def firestorm():
    return Spell("Firestorm", manaCost=5, attack=3, effect="Deals 3 damage to all Minions.")

# Weapon kort:
def sword():
    return Weapon("Sword", manaCost=3, attack=3, durability=2)


