import pygame
from game_logic import perform_attack, minion_death, hero_death
from settings import CARD_WIDTH, CARD_HEIGHT

# Card superclass:
class Card:
    def __init__(self, category, name, mana_cost, effect, pic=None):
        self.category = category    # kategori af kortet (hero, minion, spell, weapon)
        self.name = name            # navn på kortet (f.eks. "Knight")
        self.mana_cost = mana_cost  # mana cost for at spille kortet (f.eks. 3)
        self.effect = effect        # effekt af kortet (f.eks. "taunt")
        self.pic = pic              # billede af kortet (f.eks. "knight.png")

# Hero subclass:
class Hero(Card):
    def __init__(self, name, attack, max_hp, is_enemy=False, pic=None):
        super().__init__('hero', name, mana_cost=0, effect=None, pic=pic)
        self.attack = attack        # angrebskraft (f.eks. 5)
        self.max_hp = max_hp        # maximum hp (f.eks. 30)
        self.current_hp = max_hp    # nuværende hp (f.eks. 30)
        self.is_enemy = is_enemy    # om helten er fjende eller spiller (True/False)
        self.has_taunt = False      # om helten har taunt (True/False)
        self.position = (120, 360)  # position på skærmen (x, y)
        self.image = pygame.image.load(f"assets/playingCard/{pic}").convert_alpha() if pic else None

# Minion subclass:
class Minion(Card):
    def __init__(self, name, mana_cost, attack, max_hp, effect, pic=None):
        super().__init__('minion', name, mana_cost, effect, pic)
        self.attack = attack                        # angrebskraft (f.eks. 3)
        self.max_hp = max_hp                        # maximum hp (f.eks. 5)
        self.current_hp = max_hp                    # nuværende hp (f.eks. 5)
        self.effect = effect                        # effekt af kortet (f.eks. "taunt")
        self.is_selected_for_attack = False         # boolean om minion er valgt til at angribe (True/False)
        self.is_enemy = False                       # boolean om minion er fjende eller spiller (True/False)
        self.is_front_row = False                   # boolean om minion er i front row eller back row (True/False)
        self.pic = pic                              # billede af kortet (f.eks. "knight.png")
        self.has_taunt = False                      # boolean om minion har taunt (True/False)
        self.rest = True                            # boolean om minion er i hvile (True/False) - kan kun angribe hver efter første tur
        self.on_summon = lambda battle_state: None  # funktion der kaldes når minionen bliver summonet - istedet for at definere en funktion bruges en lambda funktion
        self.position = (0, 0)                      # placeholder for position på skærmen (x, y)

    # funktion til at tjekke om musen er over en minion på boardet
    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    # funktion til at minion angriber
    def perform_attack(self, target, battle_state, playmenu_draw_function):
        if self.is_selected_for_attack and target and not self.rest:  # minion må kun angribe hvis den er valgt og ikke rester
            if perform_attack(self, target, battle_state, playmenu_draw_function=playmenu_draw_function):
                self.is_selected_for_attack = False   # fjern valget efter angreb
                self.rest = True                      # når minion angriber target så put den i rest
                return True
        return False

    # funktion til at vælge en minion til at angribe
    def selected(self):
        # tjekker om musen er over minion og om venstre museknap er trykket ned, er kun muligt hvis minion ikke rester
        if self.check_hover() and pygame.mouse.get_pressed()[0] and not self.rest:  
            self.is_selected_for_attack = not self.is_selected_for_attack
            return self

    # funktion til at give alle minions på boardet +1 attack
    def buff_allies(self, battle_state):
        # tjekker om minion er en speciel minion der giver buff til alle andre minions
        if self.name == "Some Cool Guy": # Some Cool Guy er vores eneste specielle minion
            # tjekker om minion er fjende eller spiller i hvert row
            rows = [battle_state.player_front_row, battle_state.player_back_row] if not self.is_enemy else [battle_state.enemy_front_row, battle_state.enemy_back_row]
            for row in rows:
                for minion in row:
                    if minion != self:     # buffer ikke sig selv
                        minion.attack += 1 # giver +1 attack til alle andre minions

# spell subclass:
class Spell(Card):
    def __init__(self, name, mana_cost, attack, activationTimes=1, effect=None, pic=None):
        super().__init__('spell', name, mana_cost, effect, pic)
        self.attack = attack                       # angrebskraft (f.eks. 3)
        self.activationTimes = activationTimes     # antal gange spell kan aktiveres (f.eks. 1)

# weapon subclass:
class Weapon(Card):
    def __init__(self, name, mana_cost, attack, durability, pic=None):
        super().__init__('weapon', name, mana_cost, effect=None, pic=pic)
        self.attack = attack                       # angrebskraft (f.eks. 3)
        self.durability = durability               # holdbarhed (f.eks. 2) - hvor mange gange den kan bruges
        self.is_enemy = False                      # boolean om våben er fjende eller spiller (True/False) - kun spilleren kan bruge våben

# klasse der tracker minions på boardet
class BoardState:
    def __init__(self):
        self.enemy_front_row = []  # max 2 minions
        self.enemy_back_row = []   # max 3 minions
        self.player_front_row = [] # max 2 minions
        self.player_back_row = []  # max 3 minions
        self.turn_manager = None   # holder styr på hvem der har turen
        
    def set_turn_manager(self, turn_manager):
        # sætter turn manager til at holde styr på hvem der har turen
        self.turn_manager = turn_manager

    # funktion til at tilføje en minion til boardet
    def add_minion(self, minion, is_enemy, is_front_row):
        target_row = None # target_row er den række hvor minionen skal tilføjes
        if is_enemy: # tjekker om minionen er fjende eller spiller og sætter target_row derefter - front row bliver prioriteret af enemy
            target_row = self.enemy_front_row if is_front_row else self.enemy_back_row
        else:
            target_row = self.player_front_row if is_front_row else self.player_back_row
            
        # tjekker om der er plads til at tilføje minionen - max 2 minions i front row og max 3 minions i back row
        max_minions = 2 if is_front_row else 3
        if len(target_row) < max_minions:       # tjekker om der er plads i target_row
            minion.is_enemy = is_enemy          # sætter minionens is_enemy property
            minion.is_front_row = is_front_row  # sætter minionens is_front_row property
            minion.has_taunt = False            # Reset taunt før on_summon effect - failsafe til knight kortet
            target_row.append(minion)           # tilføjer minionen til target_row
            
            # tjekker om minionen har en on_summon effekt og kalder den hvis den har
            if minion.on_summon:
                minion.on_summon(self)
            return True
        return False
    
    # funktion til at håndtere klik på minions
    def handle_minion_click(self, clicked_minion, playmenu_draw_function):
        selected_minion = None
        for row in [self.player_front_row, self.player_back_row]:
            for minion in row:
                if minion.is_selected_for_attack:
                    selected_minion = minion
                    break
            if selected_minion:
                break

        # hvis en hero blev klikket og der er en minion valgt til at angribe
        if isinstance(clicked_minion, Hero):
            if clicked_minion.is_enemy and selected_minion:
                selected_minion.perform_attack(clicked_minion, self, playmenu_draw_function=playmenu_draw_function) # angriber fjende helten
                return True
            return False
            
        # hvis en minion blev klikket og der er en minion valgt til at angribe
        if clicked_minion.is_enemy and selected_minion:
            selected_minion.perform_attack(clicked_minion, self, playmenu_draw_function=playmenu_draw_function)
            return True
        elif not clicked_minion.is_enemy:
            # hvis en player minion blev klikket og der er en minion valgt til at angribe, så bliver den klikkede player minion valgt til at angribe
            if selected_minion and selected_minion != clicked_minion:
                selected_minion.is_selected_for_attack = False
            clicked_minion.selected()
            return True
        return False