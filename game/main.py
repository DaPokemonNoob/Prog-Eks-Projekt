import pygame, sys
from cards import Deck
import os
from screen import MainMenu, PlayMenu, OptionsMenu

# starter pygame
pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("test")

def switch_screen(name):
    global current_screen
    current_screen = screens[name]

current_screen = None

screens = {
    "main_menu": MainMenu(switch_screen),
    "play_menu": PlayMenu(switch_screen),
    "options_menu": OptionsMenu(switch_screen, SCREEN)
}


switch_screen("main_menu")

# state to track which menu we're in

deck = Deck()               # opretter en ny kortbunke
deck.shuffle()              # blander kortene i bunken          
last_drawn_card = None      # initialiserer last_drawn_card

suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
hand = []               # opretter en tom hånd
discard = []           # opretter en tom discard bunke

# === Main loop ===
running = True
while running:
    """if current_screen == "main_menu":
        show_main_menu()
    elif current_screen == "play_menu":
        show_play_menu()
    elif current_screen == "options_menu":
        show_options_menu()"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        current_screen.handle_event(event)

    current_screen.draw(SCREEN)
    pygame.display.update()
    clock.tick(60)