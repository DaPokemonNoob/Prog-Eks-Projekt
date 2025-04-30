import pygame, sys
from cards import Deck
import webbrowser
import os

# starter pygame
pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("test")

# state to track which menu we're in
current_screen = "main_menu"

deck = Deck()               # opretter en ny kortbunke
deck.shuffle()              # blander kortene i bunken          
last_drawn_card = None      # initialiserer last_drawn_card

suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
hand = []               # opretter en tom hånd

def load_card_image(rank, suit):
    suit_name = suit_map[suit]
    filename = f"{rank}_of_{suit_name}.png"  # Finder de forskellige kort fra en fil
    path = os.path.join("assets", "card", filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (80, 120))  # Resize Ændre størrelsen på kortene
    except pygame.error as e:
        print(f"Failed to load {path}: {e}")
        return None


class Button:
    def __init__(self, pos, color, size):
        self.size = size
        self.pos = pos
        self.color = color
        self.original_color = color
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.mouse_pos = pygame.mouse.get_pos()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.image)
    
    def check_click(self):
        # tjekker om knappen er blevet klikket på
        if self.image.collidepoint(self.mouse_pos):
            return True
        return False

    def check_hover(self):
        # tjekker om musen er over knappen
        if self.image.collidepoint(self.mouse_pos):
            return True
        return False

    def hover_color(self, hover_color):
        # ændrer farven på knappen når musen er over den
        if self.check_hover():
            self.color = hover_color
        else:
            self.color = self.original_color

    def run(self):
        self.check_hover()
        self.hover_color("green")
        self.draw(SCREEN)

def show_play_menu():
    global current_screen  # <- this is important
    SCREEN.fill("blue")
    PLAY_MOUSE_POS = pygame.mouse.get_pos()

    MENU_BUTTON = Button((100, 100), "red", (200, 50))
    MENU_BUTTON.run()

    NEXT_TURN_BUTTON = Button((400, 200), "gray", (200, 50))
    NEXT_TURN_BUTTON.run()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if MENU_BUTTON.image.collidepoint(PLAY_MOUSE_POS):
                current_screen = "main_menu"
                print("Switched to main menu")
            if NEXT_TURN_BUTTON.image.collidepoint(PLAY_MOUSE_POS):                 # Tjekker om next_turn knappen er blevet klikket på
                try:
                    last_drawn_card = deck.drawCard()
                    image = load_card_image(*last_drawn_card)
                    if image:
                        hand.append((last_drawn_card[0], last_drawn_card[1], image))
                        print(f"Drew card: {last_drawn_card[0]}{last_drawn_card[1]}")
                except IndexError:
                    print("No more cards left to draw.")
                    last_drawn_card = ("No", "Cards")
    
    x, y = 50, 400
    for i, (_, _, img) in enumerate(hand[-10:]):
        SCREEN.blit(img, (x + i * 90, y))  # Tegner kortene

    pygame.display.update()

def show_options_menu():
    global current_screen, SCREEN # <- this is also important
    SCREEN.fill("black")
    OPTION_MOUSE_POS = pygame.mouse.get_pos()

    FULLSCREEN_BUTTON = Button((480, 200), "red", (300, 100))
    FULLSCREEN_BUTTON.run()

    MUTE_BUTTON = Button((480, 380), "red", (300, 100))
    MUTE_BUTTON.run()

    BACK_BUTTON = Button((480, 560), "red", (300, 100))
    BACK_BUTTON.run()

    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 70).render("OPTIONS", True, "white"), (420, 50)) # options tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 30).render("FULLSCREEN", True, "white"), (487, 230)) # fullscreen option tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 45).render("MUTE", True, "white"), (540, 403)) # mute option tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 60).render("BACK", True, "white"), (520, 575)) # back tekst

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if FULLSCREEN_BUTTON.image.collidepoint(OPTION_MOUSE_POS):
                if SCREEN.get_flags() & pygame.FULLSCREEN:
                    SCREEN = pygame.display.set_mode((1280, 720))
                else:
                    SCREEN = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
            if MUTE_BUTTON.image.collidepoint(OPTION_MOUSE_POS):
                if pygame.mixer.get_init() is not None:
                    pygame.mixer.quit()
                else:
                    pygame.mixer.init()
            if BACK_BUTTON.image.collidepoint(OPTION_MOUSE_POS):
                current_screen = "main_menu"

    pygame.display.update()


def show_main_menu():
    global current_screen # <- this is also important
    SCREEN.fill("salmon")
    MENU_MOUSE_POS = pygame.mouse.get_pos()

    PLAY_BUTTON = Button((480, 200), "red", (300, 100))
    PLAY_BUTTON.run()

    OPTIONS_BUTTON = Button((480, 380), "red", (300, 100))
    OPTIONS_BUTTON.run()

    QUIT_BUTTON = Button((480, 560), "red", (300, 100))
    QUIT_BUTTON.run()

    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 70).render("MAIN MENU", True, "black"), (360, 50)) # main menu tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 65).render("PLAY", True, "black"), (515, 210)) # play tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 45).render("OPTIONS", True, "black"), (495, 403)) # options tekst
    SCREEN.blit(pygame.font.Font("assets/font/impact.ttf", 35).render("QUIT GAME", True, "black"), (490, 590)) # quit tekst

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if PLAY_BUTTON.image.collidepoint(MENU_MOUSE_POS):
                current_screen = "play_menu"
            if OPTIONS_BUTTON.image.collidepoint(MENU_MOUSE_POS):
                current_screen = "options_menu"
            if QUIT_BUTTON.image.collidepoint(MENU_MOUSE_POS):
                pygame.quit()
                sys.exit()

    pygame.display.update()

# === Main loop ===
running = True
while running:
    if current_screen == "main_menu":
        show_main_menu()
    elif current_screen == "play_menu":
        show_play_menu()
    elif current_screen == "options_menu":
        show_options_menu()

    clock.tick(60)