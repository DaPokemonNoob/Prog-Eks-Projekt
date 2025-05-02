import pygame, sys
from cards import Deck
import os
from screen import MainMenu, PlayMenu, OptionsMenu

# starter pygame
pygame.init()

width, height = 1280, 720
SCREEN = pygame.display.set_mode((width, height))
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

# === Main loop ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        current_screen.handle_event(event)

    current_screen.draw(SCREEN)
    pygame.display.update()
    clock.tick(60)