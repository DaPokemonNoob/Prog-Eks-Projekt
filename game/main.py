import pygame, sys
import os
from screen import MainMenu, PlayMenu, OptionsMenu, MapMenu, PauseMenu
from level import generate_map, assign_level_positions, draw_map, handle_click, Level

# starter pygame
pygame.init()

width, height = 1280, 720
SCREEN = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption("test")

# map ting
font = pygame.font.Font(None, 36)
map_data = generate_map()
assign_level_positions(map_data)

def switch_screen(name):
    global current_screen, previous_screen
    if name == "resume":
        current_screen = previous_screen
    else:
        if current_screen != screens.get("pause_menu"):
            previous_screen = current_screen
        current_screen = screens[name]

current_screen = None
previous_screen = None

screens = {
    "main_menu": MainMenu(switch_screen),
    "play_menu": PlayMenu(switch_screen),
    "options_menu": OptionsMenu(switch_screen, SCREEN),
    "map_menu": MapMenu(switch_screen, SCREEN),
    "pause_menu": PauseMenu(switch_screen)
}

switch_screen("main_menu")

# === Main loop ===
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_screen in [screens["play_menu"], screens["map_menu"]]:
                switch_screen("pause_menu")
            elif event.key == pygame.K_r:
                map_data = generate_map()
                Level.current_level = None
                assign_level_positions(map_data)
        current_screen.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(mouse_pos, map_data)

    # Draw the current screen
    if current_screen == screens["pause_menu"]:
        previous_screen.draw(SCREEN)  # Draw the game state in the background
        current_screen.draw(SCREEN)   # Draw the pause menu overlay
    else:
        current_screen.draw(SCREEN)
        if current_screen == screens["map_menu"]:
            draw_map(map_data, SCREEN, font)
    
    pygame.display.update()
    clock.tick(60)