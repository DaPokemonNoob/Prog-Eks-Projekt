import pygame, sys
from settings import *
from screen import MainMenu, OptionsMenu, MapMenu, PauseMenu, HealMenu, BattleMenu, ShopMenu, BossMenu, WinMenu, LoseMenu, SCREEN
from playmenu import PlayMenu
from level import generate_map, assign_level_positions, draw_map, handle_click, Level
from game_logic import hero_death, enemy_death
import random
from card_data import slimeling, knight, fireball, chaosCrystal

# starter pygame
pygame.init()

# alle forskellige typer af kort
# kortene er defineret i card_data.py og importeres her
all_cards = [slimeling(), knight(), fireball(), chaosCrystal()]

# map ting - map_data er en liste af level objekter
# level objekterne er defineret i level.py og importeres her
font = pygame.font.Font(None, 36)
map_data = generate_map()
assign_level_positions(map_data)

def switch_screen(name):
    global current_screen, previous_screen
    if name == "resume":
        current_screen = previous_screen
    if name == "play_menu":
        # extend playerDeckPile med kort fra playerDiscard og playerHand
        screens["play_menu"].playerDeckPile.extend(screens["play_menu"].playerDiscard)
        screens["play_menu"].playerDeckPile.extend(screens["play_menu"].playerHand)
        # clear playerDiscard og playerHand
        screens["play_menu"].playerDiscard.clear()
        screens["play_menu"].playerHand.clear()
        # shuffle playerDeckPile
        random.shuffle(screens["play_menu"].playerDeckPile)
        # træk 4 kort lige når kampen starter
        for i in range(4):
            if screens["play_menu"].playerDeckPile:
                card = screens["play_menu"].playerDeckPile.pop(0)
                screens["play_menu"].playerHand.append(card)
        current_screen = screens[name]
    else:
        if current_screen != screens.get("pause_menu"):
            previous_screen = current_screen
        current_screen = screens[name]

# variabler til at holde styr på den nuværende og forrige skærm
current_screen = None
previous_screen = None

# dictionary af alle de forskellige skærme - de er defineret i screen.py eller playmenu.py og importeres her
# dictionaryet består af skærmnavnene som nøgler og skærm objekterne som værdier
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
    "lose_menu": LoseMenu(switch_screen)
})

# heal_menu er en speciel skærm der kræver screens dictionaryet for at kunne fungere
screens.update({"heal_menu": HealMenu(switch_screen, screens["play_menu"].battle_state.player_hero)})

# sætter den nuværende skærm til mappet, som er den første skærm der vises
switch_screen("map_menu")

# === Main loop ===
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    # håndterer events som tastetryk og musse klik
    for event in pygame.event.get():
        current_screen.handle_event(event)
        if event.type == pygame.QUIT:                     # quit spillet
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:                  # skifter til pause menuen hvis escape trykkes
            if event.key == pygame.K_ESCAPE and current_screen in [screens["play_menu"], screens["map_menu"]]:
                switch_screen("pause_menu")
            elif event.key == pygame.K_r:                 # regenerer kortet hvis R trykkes
                map_data = generate_map()
                assign_level_positions(map_data)
                Level.current_level = None
    
        if event.type == pygame.MOUSEBUTTONDOWN:          # når et level på kortet trykkes skifter den til den relevante menu 
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
                elif encounter_type == "treasure":        # tilføjer et tilfældigt kort til spillerens deck
                    random_card = random.choice(all_cards)
                    screens["play_menu"].playerDeckPile.append(random_card)
                    print(f"Added {random_card.name} to deck!")

    # hvis spilleren er død skifter den til lose menuen
    if hero_death(screens["play_menu"].battle_state.player_hero, screens["play_menu"]):
        switch_screen("lose_menu")
        if current_screen == screens["lose_menu"]:
            previous_screen = screens["play_menu"]
            current_screen = screens["lose_menu"]
            previous_screen.draw(SCREEN)
            current_screen.draw(SCREEN)
    
    # hvis fjenden er død skifter den til win menuen
    if enemy_death(screens["play_menu"].battle_state.enemy_hero, screens["play_menu"]):
        switch_screen("win_menu")
        if current_screen == screens["win_menu"]:
            previous_screen = screens["play_menu"]
            current_screen = screens["win_menu"]
            previous_screen.draw(SCREEN)
            current_screen.draw(SCREEN)

    # tegner pause menuen oven på den nuværende skærm
    if current_screen == screens["pause_menu"]:
        previous_screen.draw(SCREEN)  # Draw the game state in the background
        current_screen.draw(SCREEN)   # Draw the pause menu overlay
    else:
        # tegner den nuværende skærm og kortet hvis det er kort menuen
        current_screen.draw(SCREEN)
        if current_screen == screens["map_menu"]:
            draw_map(map_data, SCREEN, font)

    # opdaterer skærmen og sætter framerate til 60 fps
    pygame.display.update()
    clock.tick(60)