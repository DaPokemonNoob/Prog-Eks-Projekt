# Biblioteker
import pygame
import sys
import os
from cards import Deck

SCREEN = pygame.display.set_mode((1280, 720))
suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'} # Oversætter kort symboler til filnavne som bruges til at finde det korrekte billede

# Funktion der indlæser et billede af et kort
def load_card_image(rank, suit):
    suit_name = suit_map[suit]
    filename = f"{rank}_of_{suit_name}.png"                 # Laver et filename ud fra typen og navnet af et kort
    path = os.path.join("assets", "card", filename)         # Laver en path til filen
    try:
        image = pygame.image.load(path).convert_alpha()     # Laver et billede med pygame og bevarer de gennemsigtige områder
        return pygame.transform.scale(image, (80, 120))     # Skalere billede
    except pygame.error as e:
        print(f"Failed to load {path}: {e}")
        return None

# Klasse der opretter knapper som objekter
class Button:
    def __init__(self, pos, color, size):                                                   # Initialisere en knap, som skal have en position, farve og størelse.
        self.size = size
        self.pos = pos
        self.color = color
        self.original_color = color                                                         # Gemmer den originale farve, så knappen kan returnere til den
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])      # Opretter et rektangel ud fra x og y koordinater til hhv. position og størelse.  

    # Funktion der tegner knappen
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.image)

    # Funktion der tjekker om musen er over knappen
    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)           # Returnerer True hvis musen er over knappen

    # Funktion der skifter farven på knappen
    def hover_color(self, hover_color):
        if self.check_hover():
            self.color = hover_color
        else:
            self.color = self.original_color

    # Tegner knappen
    def run(self):
        self.hover_color("green")
        self.draw(SCREEN)

# En super klasse som bliver nedarvet af alle andre
class Screen:
    def __init__(self):
        self.buttons = []           # Tom liste til knapper
        self.actions = {}           # Et dictionary der matcher knapper med deres effekt
        self.bg_color = "black"

    # funktion der håndtere klik
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for button, action in self.actions.items():         # Tjekker om musen er over en knap
                if button.image.collidepoint(pos):              # Hvis ja så udføre den en handling
                    action()

    # Funktion der tegner skærmen
    def draw(self, screen):
        screen.fill(self.bg_color)
        # Tegner alle knapperne på en skærm
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

    # Tom funktion som underklasser kan overskrive
    def draw_labels(self, screen):
        pass

# skærm til hovedmenuen
class MainMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.bg_color = "salmon"
        self.switch_screen = switch_screen  

        # Laver 3 knapper
        self.play_button = Button((480, 200), "red", (300, 100))
        self.options_button = Button((480, 380), "red", (300, 100))
        self.quit_button = Button((480, 560), "red", (300, 100))

        self.buttons = [self.play_button, self.options_button, self.quit_button]    # Ligger knapperne i self.buttons listen
        
        # Giver hver knap en effekt
        self.actions = {
            self.play_button: lambda: self.switch_screen("play_menu"),
            self.options_button: lambda: self.switch_screen("options_menu"),
            self.quit_button: lambda: sys.exit()
        }

    # Overskrider den tome draw_labels og tegner teksten på menuen og knapperne
    def draw_labels(self, screen):
        font_large = pygame.font.Font("assets/font/impact.ttf", 70)
        font_play = pygame.font.Font("assets/font/impact.ttf", 65)
        font_options = pygame.font.Font("assets/font/impact.ttf", 45)
        font_quit = pygame.font.Font("assets/font/impact.ttf", 35)

        screen.blit(font_large.render("MAIN MENU", True, "black"), (360, 50))
        screen.blit(font_play.render("PLAY", True, "black"), (515, 210))
        screen.blit(font_options.render("OPTIONS", True, "black"), (495, 403))
        screen.blit(font_quit.render("QUIT GAME", True, "black"), (490, 590))

# skærm til optionsmenu
class OptionsMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "black"
        self.switch_screen = switch_screen
        self.screen_ref = screen_ref

        self.fullscreen_button = Button((480, 200), "red", (300, 100))
        self.mute_button = Button((480, 380), "red", (300, 100))
        self.back_button = Button((480, 560), "red", (300, 100))

        self.buttons = [self.fullscreen_button, self.mute_button, self.back_button]
        self.actions = {
            self.fullscreen_button: self.toggle_fullscreen,
            self.mute_button: self.toggle_mute,
            self.back_button: lambda: self.switch_screen("main_menu")
        }

    # Funktion der skifter til mellem vhcaindue og fuldskærm
    def toggle_fullscreen(self):
        # Hvis der er fuldskærm skiftes der til vindue ellers forbliver den fuld
        if self.screen_ref.get_flags() & pygame.FULLSCREEN:                                 # bruger get_flags til at vise hvilke visningstilstand der er aktiv
            self.screen_ref = pygame.display.set_mode((1280, 720))
        else:
            self.screen_ref = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

    # Funktion der vælger om der skal være lyd til
    def toggle_mute(self):
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        else:
            pygame.mixer.init()

    # Funktion der tegner tekst
    def draw_labels(self, screen):
        font_big = pygame.font.Font("assets/font/impact.ttf", 70)
        font_small = pygame.font.Font("assets/font/impact.ttf", 30)
        screen.blit(font_big.render("OPTIONS", True, "white"), (420, 50))
        screen.blit(font_small.render("FULLSCREEN", True, "white"), (487, 230))
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 45).render("MUTE", True, "white"), (540, 403))
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 60).render("BACK", True, "white"), (520, 575))

# skærm til spillet
class PlayMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.bg_color = "blue"
        self.switch_screen = switch_screen

        self.deck = Deck()          # Laver en bunke kort
        self.deck.shuffle()         # Blander kortene
        self.hand = []              # Laver en liste til kort på hånden
        self.discard = []           # Laver en liste til discarded kort

        self.dragged_card = None
        self.drag_offset = (0,0)
        self.lock_zone = pygame.Rect(1000, 400, 120, 160)  # x, y, width, height
        self.locked_card = None  # Liste til kort som er låst fast

        self.menu_button = Button((100, 100), "red", (200, 50))
        self.next_turn_button = Button((400, 200), "gray", (200, 50))

        self.buttons = [self.menu_button, self.next_turn_button]
        self.actions = {
            self.menu_button: lambda: self.switch_screen("main_menu"),
            self.next_turn_button: self.draw_card
        }

    # Funktion der tegner kort på skærmen
    def draw_card(self):        
        try:                                                    # Prøver at tegne et kort 
            card = self.deck.drawCard()                     
            image = load_card_image(*card)
            if image:
                if len(self.hand) < 7:                          # Hvis der er mindre end 7 kort i hånden trækkes der et kort ellers bliver det puttet i discard bunken
                    self.hand.append((*card, image))
                else:
                    self.discard.append((*card, image))
                    print(f"Drew card: {card}")
        except IndexError:                                      # Hvis der ikke er flere kort i bunken
            print("No more cards to draw.")

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for i in range(len(self.hand)-1, -1, -1):
                _, _, img = self.hand[i]
                card_rect = pygame.Rect(50 + i * 90, 400, 80, 120)
                if card_rect.collidepoint(mouse_x, mouse_y):
                    self.dragged_card = self.hand.pop(i)
                    offset_x = mouse_x - card_rect.x
                    offset_y = mouse_y - card_rect.y
                    self.drag_offset = (offset_x, offset_y)
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_card:
                mouse_x, mouse_y = event.pos
                if self.lock_zone.collidepoint(mouse_x, mouse_y):
                    if self.locked_card is None:
                        # Lås kortet i zonen
                        self.locked_card = (
                            self.lock_zone.x + (self.lock_zone.width - 80) // 2,
                            self.lock_zone.y + (self.lock_zone.height - 120) // 2,
                            self.dragged_card[2]
                        )
                    else:
                        # Der ligger allerede et kort, så returnér det til hånden
                        new_index = (mouse_x - 50) // 90
                        new_index = max(0, min(len(self.hand), new_index))
                        self.hand.insert(new_index, self.dragged_card)
                else:
                    new_index = (mouse_x - 50) // 90
                    new_index = max(0, min(len(self.hand), new_index))
                    self.hand.insert(new_index, self.dragged_card)
                self.dragged_card = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_card:
                # Optional: could update live position here
                pass



    # funktion der tegner alt på skærmen
    def draw(self, screen):
        super().draw(screen)

        pygame.draw.rect(screen, (160, 32, 240), self.lock_zone, border_radius=10)

        x, y = 50, 400
        for i, (_, _, img) in enumerate(self.hand):             # Tegner alle kortene på hånden og forskyder dem med 90
            screen.blit(img, (x + i * 90, y))

        if self.locked_card:
            lx, ly, img = self.locked_card
            screen.blit(img, (lx, ly))

        if self.dragged_card:
            _, _, img = self.dragged_card
            mouse_x, mouse_y = pygame.mouse.get_pos()
            offset_x, offset_y = self.drag_offset
            screen.blit(img, (mouse_x - offset_x, mouse_y - offset_y))

        x_d, y_d = 50, 550
        for i, (_, _, img) in enumerate(self.discard[-5:]):     # Tegner de fem seneste kort i discard bunken
            screen.blit(img, (x_d + i * 60, y_d))

class MapMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "white"
        self.switch_screen = switch_screen
        self.screen_ref = screen_ref