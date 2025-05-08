# Brugte biblioteker
import pygame
import random
import card_data as card
from card_classes import BoardState
from enemy import Enemy
from screen import Screen, Button
from settings import *
from animations import play_card_draw_and_flip_animation
from game_logic import (TurnManager, use_weapon, use_minion, use_spell)

# Objekt PlayMenu, som er en subclass af Screen
# Den indeholder alle funktioner og metoder til at spille spillet
class PlayMenu(Screen):
    def __init__(self, switch_screen, clock):
        super().__init__()
        # En række variabler der bruges i PlayMenu
        self.switch_screen = switch_screen              # Giver adgang til klassens attribut switch_screen
        self.clock = clock                              # Giver adgang til klassens attribut clock    



        # Bruger pygame til at indlæse billeder gemmer dem som attributter
        self.mana_full = pygame.image.load("assets/mana/mana_full.png").convert_alpha()
        self.mana_empty = pygame.image.load("assets/mana/mana_empty.png").convert_alpha()
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))              # Skalerer billedet til skærmstørrelsen
              
        # Game state initialization
        self.battle_state = BoardState()                        # Opretter et BoardState objekt, som indeholder spillets tilstand
        self.battle_state.player_hero = card.adventurer()       # Opretter spillerens helte kort
        self.battle_state.enemy_hero = card.evilGuy()           # Opretter modstanderens helte kort

        # Laver et område (en firkant) på skærmen hvor helte kortene bliver vist (Position: x,y og Størrelse: bredde, højde)
        self.player_hero_rect = pygame.Rect(20, HEIGHT//2 - HERO_CARD_HEIGHT//2, HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        self.enemy_hero_rect = pygame.Rect(WIDTH - 20 - HERO_CARD_WIDTH, HEIGHT//2 - HERO_CARD_HEIGHT//2, HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        
        # Opretter et Enemy objekt og giver det adgang til battle_state
        self.enemy = Enemy(self.battle_state)
        self.turn_manager = TurnManager(self, self.enemy, self.draw)               # Opretter et TurnManager objekt, der styrer turene i spillet
        self.battle_state.set_turn_manager(self.turn_manager)                      # Gør at battle_state kender til turn_manager, så den kan bruge den til at hvad kortene kan

        # denne funktion initialiserer spillerens dæk
        self.playerDeckPile = [card.knight(), card.knight(), card.slimeling(),              # Spillerens dæk
                               card.slimeling(), card.slimeling(), card.chaosCrystal(),
                                 card.fireball(), card.fireball(), card.sword(),
                                   card.sword()]    
        random.shuffle(self.playerDeckPile)                                                 # Blander spillerens dæk        
        self.playerHand = []                                                                # Laver en tom liste til kortene i spillerens hånd
        self.playerDiscard = []                                                             # Laver en tom liste til kortene i spillerens discard pile

        self.dragged_card = None        # Attribut der tjekker om spilleren rykker på et kort
        self.drag_offset = (0, 0)       # Forskellen mellem musens position og kortets position når spilleren trækker kortet

        # Laver zonerne hvor kortene kan placeres
        self.player_front_row_zone = pygame.Rect(440, 87, 200, 300)
        self.player_back_row_zone = pygame.Rect(240, 25, 200, 450)
        self.enemy_front_row_zone = pygame.Rect(640, 87, 200, 300)
        self.enemy_back_row_zone = pygame.Rect(840, 25, 200, 450)
        
        # Laver knapper med objektet Button
        self.menu_button = Button((100, 100), "red", (200, 50))                                                                                                         # Knap til at gå til menuen
        self.next_turn_button = Button((993, 587), "gray", (240, 128), image_path="assets/button/end_turn.png", hover_image_path="assets/button/end_turn_hover.png")    # Knap til at afslutte turen

        # Tildeler knapperne en funktion
        self.buttons = [self.menu_button, self.next_turn_button]
        self.actions = {
            self.menu_button: lambda: self.switch_screen("map_menu"),
            self.next_turn_button: self.end_turn
        }
        # En liste over alle kortenes firkanter i hånden, så musen kan tjekke om den er over et kort
        self.hand_card_rects = []

    # Funktion der slutter spillerens tur
    def end_turn(self):
        card_back = pygame.image.load("assets/playingCard/back.png").convert_alpha() # Indlæser et billede af bagsiden af kortet

        # Dynamisk indlæsning af card_front baseret på card.pic
        card = self.playerDeckPile[0] if self.playerDeckPile else None          # Prøver at tage det øverste kort fra bunken
        card_front = None
        if card and card.pic:                                                   # Tjekker om kortet har et billede
            card_front_path = f"assets/playingCard/{card.pic}"                  # Laver stien til kortet
            card_front = pygame.image.load(card_front_path).convert_alpha()     # Indlæser kortet
        # Hvis kortet ikke har et billede printes en fejlmeddelelse
        else:
            print("No card or card.pic is missing!")

        # Definition af attributter til animationen
        draw_animation_start = (64, 525)                                                                           # Startposition
        draw_animation_end = (WIDTH // 2 - card_back.get_width() // 2, HEIGHT // 2 - card_back.get_height() // 2)  # Slutposition

        # Hvis forsiden er korrekt indlæst, så køre animationen
        if card_front:
            play_card_draw_and_flip_animation(SCREEN, self.clock, card_back, card_front, draw_animation_start, draw_animation_end, self.draw, delay_after_flip=1000)

        # bruger turn_manager til at afslutte spillerens tur
        self.turn_manager.end_player_turn()

     # Funktion der håndterer alle events i spillet
    def handle_event(self, event):
        super().handle_event(event)

        # Tjekker om det er spillerens tur, hvis det ikke er spillerens tur, så gør ingenting
        if not self.turn_manager.is_player_turn:
            return

        # Tjekker om der er trykkes på en knap på musen
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Hvis trykket er på modstanderens helte kort
            if self.enemy_hero_rect.collidepoint(mouse_x, mouse_y):
                # Angriber modstanderens helte kort
                self.battle_state.handle_minion_click(self.battle_state.enemy_hero, playmenu_draw_function=self.draw)
                return
                
            # Tjekker alle kort i spillerens hånd 
            for i, rect in enumerate(self.hand_card_rects):
                # Hvis musekliket er over et kort
                if rect.collidepoint(mouse_x, mouse_y):
                    card = self.playerHand[i]   # Henter kort objektet fra hånden
                    # Tjekker om kortet har attributten category og om det enten er en minion, spell eller weapon kort
                    if hasattr(card, 'category') and (card.category == 'minion' or card.category == 'spell' or card.category == 'weapon'):
                        # Bruger turn mangager til at tjekke om kortet kan spilles
                        if self.turn_manager.can_play_card(card):
                            self.dragged_card = self.playerHand.pop(i)              # Kortet bliver tilføjet til dragged_card og fjernet fra hånden
                            self.drag_offset = (mouse_x - rect.x, mouse_y - rect.y) # Gemmer forskellen mellem musens position og kortets position
                    break

            # Hvis spilleren ikke trækker et kort
            if not self.dragged_card:
                # Tjekker rækkerne for minions
                for row in [self.battle_state.enemy_front_row, self.battle_state.enemy_back_row,
                          self.battle_state.player_front_row, self.battle_state.player_back_row]:
                    # Tjekker minions i rækken
                    for minion in row:
                        if minion.image and minion.image.collidepoint(mouse_x, mouse_y):                        # Hvis minionen har et billede og musen er over den
                            self.battle_state.handle_minion_click(minion, playmenu_draw_function=self.draw)     # Så bruger den battle_state til at håndtere minionen
                            break

        # Hvis musen knappen slippes
        elif event.type == pygame.MOUSEBUTTONUP:
            # Hvis spilleren holder et kort
            if self.dragged_card:
                mouse_x, mouse_y = event.pos      # Opdaterer musens position

                # Hvis kortets kategori er weapon
                if self.dragged_card.category == 'weapon':
                    # Prøver at bruge våbnet
                    if use_weapon(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost)  # Hvis det lykkedes at bruge våbnet, så bruges manaen våbnet koster
                        # Hvis våbnet ikke har mere holdbarhed
                        if self.dragged_card.durability <= 0:               
                            self.playerDiscard.append(self.dragged_card)    # Så tilføjes det til discard pile
                            self.dragged_card = None                        # Kortet slettes fra dragged_card
                        # Ellers returnes kortet til hånden
                        else:
                            self.return_card_to_hand(mouse_x)
                    else:
                        self.return_card_to_hand(mouse_x)
                    return

                # Hvis kortets kategori er spell
                if self.dragged_card.category == 'spell':
                    # Prøver at bruge spell kortet
                    if use_spell(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost)               # Hvis det lykkedes at bruge spell kortet, så bruges manaen
                        self.playerDiscard.append(self.dragged_card)                            # og kortet tilføjes til discard pile
                        self.dragged_card = None                                                # Kortet slettes fra dragged_card       
                    # Ellers returneres kortet til hånden                
                    else:
                        self.return_card_to_hand(mouse_x)
                    return

                # Hvis kortets kategori er minion
                elif self.dragged_card.category == 'minion':
                    placed = False                                                          # Variabel der siger at kortet ikke er placeret endnu
                    # Hvis musen er over den foreste række        
                    if self.player_front_row_zone.collidepoint(mouse_x, mouse_y):
                        # Og battle_state tillader at tilføje kortet til rækken
                        if self.battle_state.add_minion(self.dragged_card, False, True):
                            # Så placeres kortet i rækken
                            placed = True
                    # Det samme gælder for den bagerste række
                    elif self.player_back_row_zone.collidepoint(mouse_x, mouse_y):
                        if self.battle_state.add_minion(self.dragged_card, False, False):
                            placed = True
                            
                    # Hvis kortet bliver placeret
                    if placed:
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost)            # Manaen bruges
                        self.dragged_card = None                                             # Kortet slettes fra dragged_card   
                        return

                # Hvis kortet ikke bliver placeret returnes det til hånden
                self.return_card_to_hand(mouse_x)

    # Funktion der returnerer kortet til hånden hvis det ikke bliver placeret
    def return_card_to_hand(self, mouse_x):
        insert_pos = 0                  #                    Variabel der siger at det første sted kortet kan placeres er ved 0 
        # Gennemgår alle positionerne (rektanglerne) i hånden
        for i, rect in enumerate(self.hand_card_rects):     
            # Tjekker om musen er til venstre for rektanglet
            if mouse_x < rect.centerx:
                insert_pos = i              # Hvis ja, så placeres kortet til venstre for rektanglet
                break
            # Hvis løkken ikke brydes indsættes kortet til sidst i hånden
            insert_pos = i + 1
        self.playerHand.insert(insert_pos, self.dragged_card)   # Indsætter kortet i hånden på den rigtige position
        self.dragged_card = None                                # Kortet slettes fra dragged_card 

    # Funktioner der tegner ting på skærmen
    def draw(self, screen):
        # Tegner baggrunden i (0,0)
        screen.blit(self.background_image, (0, 0))
        
        # Tegner heltekortene
        self.draw_hero_card(screen, self.battle_state.player_hero, self.player_hero_rect)
        self.draw_hero_card(screen, self.battle_state.enemy_hero, self.enemy_hero_rect, True) # True ændrer helten til enemy
        
        # Tegner manaen
        self.draw_mana(screen)
        
        # Tegner zonerne til minion
        pygame.draw.rect(screen, (100, 200, 100), self.player_front_row_zone, 2)        # (skærm, farve, rektangel, tykkelse)
        pygame.draw.rect(screen, (100, 200, 100), self.player_back_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_front_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_back_row_zone, 2)

        # Laver minion rækkerne
        self.draw_minion_row(screen, self.battle_state.player_front_row, self.player_front_row_zone) # (skærm, minion række, zone)
        self.draw_minion_row(screen, self.battle_state.player_back_row, self.player_back_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_front_row, self.enemy_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_back_row, self.enemy_back_row_zone)

        self.draw_hand(screen)              # Tegner hånden
        self.draw_dragged_card(screen)      # Tegner det kort der bliver trukket

        # Tegner og opdaterer knapperne
        for button in self.buttons:
            button.run()


    # Funktion der tegner manaen på skærmen
    def draw_mana(self, screen):
        x, y = 980, 530                             # Start position for mana ikoner
        spacing = 5                                 # Mellemrum i mellem ikonerne
        icon_width = self.mana_full.get_width()     # Finder bredden på ikonerne

        # Løkke over det maksimale antal mana spilleren har
        for i in range(self.turn_manager.max_mana):
            # hvis antalet er mindre end det nuværende antal mana
            if i < self.turn_manager.current_mana:
                icon = self.mana_full               # Så er ikonet = den fulde version
            # Ellers er ikonet = den tomme version
            else:
                icon = self.mana_empty
            # Tegner ikonerne på skærmen
            screen.blit(icon, (x + i * (icon_width + spacing), y))

    # Funktion der tegner minion rækkerne på skærmen
    def draw_minion_row(self, screen, row, zone_rect):
        spacing = 20                                            # Mellemrum i mellem kortene          
        x = zone_rect.x + (zone_rect.width - CARD_WIDTH) // 2   # Finder x værdien til kortene
        y = zone_rect.y + spacing                               # Finder y værdien til kortene    

        # Går igennem alle minions i rækken
        for minion in row:
            minion.image = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)                           # Giver minionen en rektangel der bruges til at tjekke kollision

            # Hvis minionen har et billede
            if hasattr(minion, 'pic') and minion.pic:
                image = pygame.image.load(f"assets/playingCard/{minion.pic}").convert_alpha()   # Laver stien til billedet
                image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))                # Skalerer billedet til kortets størrelse
                screen.blit(image, (x, y))                                                      # Tegner billedet på skærmen                
                
                # Tjekker om minionen har taunt og tegner en guld kant rundt om kortet
                if minion.has_taunt:
                    pygame.draw.rect(screen, (255, 215, 0), minion.image, 3)
            
            # Definere en font
            font = pygame.font.Font(None, 24)
            # Tegner teksten på kortet
            screen.blit(font.render(str(minion.mana_cost), True, (255, 255, 255)), (x + 81, y + 9))         # (font, tekst, antialiasing = True, farve, position)
            screen.blit(font.render(str(minion.attack), True, (255, 255, 255)), (x + 11, y + 119))
            screen.blit(font.render(str(minion.current_hp), True, (255, 255, 255)), (x + 81, y + 119))
            
            y += 120 + spacing  # Opdaterer y værdien til næste kort i rækken

    # Funktion der tegner helte kortene på skærmen
    def draw_hero_card(self, screen, hero, rect, is_enemy=False):
        color = (200, 0, 0) if is_enemy else (0, 200, 0)                # Sætter farverne rød for modstander og grøn for spilleren
        pygame.draw.rect(screen, color, rect)                           # Tegner rektanglet på skærmen  
        
        # hero objektet gives en reference til rektanglet, så det kan bruges i andre funktioner blandt andet handle_event
        hero.image = rect
        
        # Tegner teksten på kortet
        font = pygame.font.Font(None, int(24 * 1.8))                                        # Scalerer en standard font op
        text = font.render(hero.name, True, (0, 0, 0))                                      # Skriver navnet på helten på kortet    
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - rect.height//4))     # Placeringen af teksten på rektanglet
        screen.blit(text, text_rect)                                                        # Tegner teksten på skærmen                       
        
        # Heltens liv ændrer farve alt efter hvor meget liv den har
        if hero.current_hp == hero.max_hp:
            hp_text = font.render(f"HP: {hero.current_hp}", True, (0, 0, 0))
        elif hero.current_hp > hero.max_hp:
            hp_text = font.render(f"HP: {hero.current_hp}", True, (0, 255, 0))
        elif hero.current_hp < hero.max_hp:
            hp_text = font.render(f"HP: {hero.current_hp}", True, (150, 0, 0))
        elif hero.current_hp < 0:
            hp_text = font.render(f"HP: {hero.current_hp}", True, (255, 0, 0))
        hp_rect = hp_text.get_rect(center=(rect.centerx, rect.centery + rect.height//4))
        screen.blit(hp_text, hp_rect)                                                       # Tegner livet på skærmen   

    def draw_hand(self, screen):
        # Laver en tom liste der gemmer alle rektanglerne til kortene i hånden
        self.hand_card_rects = []
        # Start position for kortene i hånden
        x, y = 370, 570
        # Tjekker alle kortene i hånden
        for card in self.playerHand:
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)   # Opretter et rektangel til kortende som bruges til at tjekke kollision
            # Hvis kortet har et billede
            if card.pic:
                image = pygame.image.load(f"assets/playingCard/{card.pic}").convert_alpha()     # Laver stien til billedet
                image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))                # Skalerer billedet til kortets størrelse
                screen.blit(image, (x, y))                                                      # Tegner billedet på skærmen    

            # Definere en font
            font = pygame.font.Font(None, 24)
            screen.blit(font.render(str(card.mana_cost), True, (255, 255, 255)), (x + 81, y + 9))   # tegner mana cost på kortet

            # Tjekker kortets kategori, hvis det er en minion, så tegnes attack og hp
            if hasattr(card, "category") and card.category == "minion":
                screen.blit(font.render(str(card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(card.current_hp), True, (255, 255, 255)), (x + 81, y + 119))
            # Tjekker kortets kategori, hvis det er et våben, så tegnes attack og durability
            elif hasattr(card, "category") and card.category == "weapon":
                screen.blit(font.render(str(card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(card.durability), True, (255, 255, 255)), (x + 81, y + 119))
            else:
                None

            self.hand_card_rects.append(rect)   # Tilføjer rektanglet til listen
            x += 100                            # Opdaterer x værdien til næste kort i hånden

    # Funktion der tegner det kort spilleren holder og trækker på
    def draw_dragged_card(self, screen):
        # Forsætter kun hvis spilleren holder et kort og kortet har et billede
        if self.dragged_card and self.dragged_card.pic:
            mouse_x, mouse_y = pygame.mouse.get_pos()       # Finder musens position
            x = mouse_x - self.drag_offset[0]               # Definere x værdien til kortet
            y = mouse_y - self.drag_offset[1]               # Definere y værdien til kortet

            image = pygame.image.load(f"assets/playingCard/{self.dragged_card.pic}").convert_alpha()    # Laver stien til billedet
            image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))                            # Skalerer billedet til kortets størrelse
            screen.blit(image, (x, y))                                                                  # Tegner billedet på skærmen    

            font = pygame.font.Font(None, 24)                                                           # Definere en font
            mana_text = font.render(str(self.dragged_card.mana_cost), True, (255, 255, 255))            # (font, tekst, antialiasing = True, farve, position)
            screen.blit(mana_text, (x + 81, y + 9))                                                     # Tegner mana cost på kortet

            # Tjekker om kortets kategori er en minion, hvis ja, så tegnes attack og hp
            if hasattr(self.dragged_card, "category") and self.dragged_card.category == "minion":
                screen.blit(font.render(str(self.dragged_card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(self.dragged_card.current_hp), True, (255, 255, 255)), (x + 81, y + 119))
            # Tjekker om kortets kategori er et våben, hvis ja, så tegnes attack og durability
            elif hasattr(self.dragged_card, "category") and self.dragged_card.category == "weapon":
                screen.blit(font.render(str(self.dragged_card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(self.dragged_card.durability), True, (255, 255, 255)), (x + 81, y + 119)) 
                        
    # Funktion der der gives slip på musen
    def handle_mouse_up(self, event):
        # Hvis spilleren holder et kort så forsætter vi
        if self.dragged_card:
            mouse_x, mouse_y = event.pos        # Gemmer musens position
            
            # Hvis kortet har en kategori
            if hasattr(self.dragged_card, 'category'):
                # Hvis kortet er et våben
                if self.dragged_card.category == 'weapon':
                    # Prøver at bruge våbnet, hvis det lykkedes så bruges manaen og kortet slettes fra dragged_card
                    if use_weapon(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost) 
                        self.dragged_card = None
                    # Ellers returneres kortet til hånden
                    else:
                        self.return_card_to_hand(mouse_x)
                # Hvis kortet er et spell
                elif self.dragged_card.category == 'spell':
                    # Prøver at bruge spell kortet, hvis det lykkedes så bruges manaen og kortet tilføjes til discard pile
                    if use_spell(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost)
                        self.dragged_card = None
                    # Ellers returneres kortet til hånden
                    else:
                        self.return_card_to_hand(mouse_x)
                # Hvis kortet er en minion
                elif self.dragged_card.category == 'minion':
                    # Prøver at placere minionen
                    if use_minion(self.dragged_card, mouse_x, mouse_y, self.battle_state, 
                                self.player_front_row_zone, self.player_back_row_zone):
                        # Hvis det lykkedes at placere minionen, så bruges manaen og kortet slettes fra dragged_card
                        self.turn_manager.spend_mana(self.dragged_card.mana_cost)
                        self.dragged_card = None
                    # Ellers returneres kortet til hånden
                    else:
                        self.return_card_to_hand(mouse_x)