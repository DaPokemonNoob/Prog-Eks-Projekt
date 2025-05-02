import pygame, sys
from cards import Deck
import os
from screen import MainMenu, PlayMenu, OptionsMenu, MapMenu
from level import generate_map, assign_level_positions, draw_map

# starter pygame
pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("test")

# map ting
font = pygame.font.Font(None, 36)
map_data = generate_map()
assign_level_positions(map_data)

def switch_screen(name):
    global current_screen
    current_screen = screens[name]

current_screen = None

screens = {
    "main_menu": MainMenu(switch_screen),
    "play_menu": PlayMenu(switch_screen),
    "options_menu": OptionsMenu(switch_screen, SCREEN),
    "map_menu": MapMenu(switch_screen, SCREEN)
}

switch_screen("main_menu")

deck = Deck()               # opretter en ny kortbunke
deck.shuffle()              # blander kortene i bunken          
last_drawn_card = None      # initialiserer last_drawn_card

suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
hand = []               # opretter en tom hånd
discard = []           # opretter en tom discard bunke

# === Main loop ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        current_screen.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                map_data = generate_map() # genererer et nyt kort når R trykkes
                assign_level_positions(map_data)

    current_screen.draw(SCREEN)
    if current_screen == screens['map_menu']:
        draw_map(map_data, SCREEN, font) # tegner kortet
    pygame.display.update()
    clock.tick(60)