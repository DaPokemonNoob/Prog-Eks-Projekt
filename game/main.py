import pygame, sys
from settings import *
from screen import MainMenu, OptionsMenu, MapMenu, PauseMenu, HealMenu, BattleMenu, ShopMenu, BossMenu, WinMenu, LoseMenu, SCREEN
from playmenu import PlayMenu
from level import generate_map, assign_level_positions, draw_map, handle_click, Level
from game_logic import hero_death, enemy_death
from game_logic import battle_start
import random
from card_data import slimeling, knight, fireball, chaosCrystal

# starter pygame
pygame.init()

clock = pygame.time.Clock()
pygame.display.set_caption("Arcane Clash")

all_cards = [slimeling(), knight(), fireball(), chaosCrystal()]

# map ting
font = pygame.font.Font(None, 36)
map_data = generate_map()
assign_level_positions(map_data)

def switch_screen(name):
    global current_screen, previous_screen
    if name == "resume":
        current_screen = previous_screen
    if name == "play_menu":
        battle_start(screens["play_menu"])
        current_screen = screens[name]
    else:
        if current_screen != screens.get("pause_menu"):
            previous_screen = current_screen
        current_screen = screens[name]

current_screen = None
previous_screen = None
screens = {}
screens.update({
    "main_menu": MainMenu(switch_screen),
    "play_menu": PlayMenu(switch_screen, clock),
    "options_menu": OptionsMenu(switch_screen, SCREEN),
    "map_menu": MapMenu(switch_screen, SCREEN),
    "pause_menu": PauseMenu(switch_screen),
    "battle_menu": BattleMenu(switch_screen),
    "shop_menu": ShopMenu(switch_screen),
    "boss_menu": BossMenu(switch_screen),
    "win_menu": WinMenu(switch_screen),
    "lose_menu": LoseMenu(switch_screen),

})

screens.update({"heal_menu": HealMenu(switch_screen, screens["play_menu"].battle_state.player_hero)})

switch_screen("map_menu")

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
                assign_level_positions(map_data)
                Level.current_level = None
        current_screen.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == screens["map_menu"]:
                encounter_type = handle_click(mouse_pos, map_data)
                if encounter_type == "battle":
                    switch_screen("play_menu")
                elif encounter_type == "shop":
                    switch_screen("shop_menu")
                elif encounter_type == "heal":
                    switch_screen("heal_menu")
                elif encounter_type == "boss":
                    switch_screen("boss_menu")
                elif encounter_type == "treasure":
                    # Add a random card to the deck
                    random_card = random.choice(all_cards)
                    screens["play_menu"].playerDeckPile.append(random_card)
                    print(f"Added {random_card.name} to deck!")

    if hero_death(screens["play_menu"].battle_state.player_hero, screens["play_menu"]):
        switch_screen("lose_menu")
        if current_screen == screens["lose_menu"]:
            previous_screen = screens["play_menu"]
            current_screen = screens["lose_menu"]
            previous_screen.draw(SCREEN)
            current_screen.draw(SCREEN)
    
    if enemy_death(screens["play_menu"].battle_state.enemy_hero, screens["play_menu"]):
        switch_screen("win_menu")
        if current_screen == screens["win_menu"]:
            previous_screen = screens["play_menu"]
            current_screen = screens["win_menu"]
            previous_screen.draw(SCREEN)
            current_screen.draw(SCREEN)

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