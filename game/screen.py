import pygame
import sys
import os
from playingCards import Deck
import card_data as card
from card_classes import BoardState, Hero
from enemy import Enemy
import random
from animations import play_card_draw_and_flip_animation
from game_logic import (minion_death, draw_card, cast_spell, 
                       use_weapon, can_attack_target, TurnManager, use_minion, use_spell)

width, height = 1280, 720
SCREEN = pygame.display.set_mode((width, height))
suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}

# Card size constants
CARD_WIDTH = 80
CARD_HEIGHT = 120
HERO_SCALE = 2
HERO_CARD_WIDTH = int(CARD_WIDTH * HERO_SCALE)
HERO_CARD_HEIGHT = int(CARD_HEIGHT * HERO_SCALE)

def load_card_image(rank, suit):
    suit_name = suit_map[suit]
    filename = f"{rank}_of_{suit_name}.png"
    path = os.path.join("assets", "card", filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (100, 140))
    except pygame.error as e:
        print(f"Failed to load {path}: {e}")
        return None

class Button:
    def __init__(self, pos, color, size, image_path=None, hover_image_path=None):
        self.size = size
        self.pos = pos
        self.color = color
        self.original_color = color
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.button_image = None
        self.hover_image = None
        if image_path:
            try:
                self.button_image = pygame.image.load(image_path).convert_alpha()
                self.button_image = pygame.transform.scale(self.button_image, size)
            except pygame.error as e:
                print(f"Failed to load button image {image_path}: {e}")
        if hover_image_path:
            try:
                self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
                self.hover_image = pygame.transform.scale(self.hover_image, size)
            except pygame.error as e:
                print(f"Failed to load hover image {hover_image_path}: {e}")

    def draw(self, screen):
        if self.check_hover() and self.hover_image:
            screen.blit(self.hover_image, self.pos)
        elif self.button_image:
            screen.blit(self.button_image, self.pos)
        else:
            pygame.draw.rect(screen, self.color, self.image)

    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    def hover_color(self, hover_color):
        if not self.button_image and not self.hover_image:
            if self.check_hover():
                self.color = hover_color
            else:
                self.color = self.original_color

    def run(self):
        self.hover_color("green")
        self.draw(SCREEN)

class Screen:
    def __init__(self):
        self.buttons = []
        self.actions = {}
        self.bg_color = "black"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for button, action in self.actions.items():
                if button.image.collidepoint(pos):
                    action()

    def draw(self, screen):
        screen.fill(self.bg_color)
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

    def draw_labels(self, screen):
        pass

class MainMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.bg_color = "salmon"
        self.switch_screen = switch_screen

        self.play_button = Button((480, 200), "red", (300, 100))
        self.options_button = Button((480, 380), "red", (300, 100))
        self.quit_button = Button((480, 560), "red", (300, 100))

        self.buttons = [self.play_button, self.options_button, self.quit_button]

        self.actions = {
            self.play_button: lambda: self.switch_screen("play_menu"), #AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
            self.options_button: lambda: self.switch_screen("options_menu"),
            self.quit_button: lambda: sys.exit()
        }

    def draw_labels(self, screen):
        font_large = pygame.font.Font("assets/font/impact.ttf", 70)
        font_play = pygame.font.Font("assets/font/impact.ttf", 65)
        font_options = pygame.font.Font("assets/font/impact.ttf", 45)
        font_quit = pygame.font.Font("assets/font/impact.ttf", 35)

        screen.blit(font_large.render("MAIN MENU", True, "black"), (360, 50))
        screen.blit(font_play.render("PLAY", True, "black"), (515, 210))
        screen.blit(font_options.render("OPTIONS", True, "black"), (495, 403))
        screen.blit(font_quit.render("QUIT GAME", True, "black"), (490, 590))

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

    def toggle_fullscreen(self):
        if self.screen_ref.get_flags() & pygame.FULLSCREEN:
            self.screen_ref = pygame.display.set_mode((1280, 720))
        else:
            self.screen_ref = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

    def toggle_mute(self):
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        else:
            pygame.mixer.init()

    def draw_labels(self, screen):
        font_big = pygame.font.Font("assets/font/impact.ttf", 70)
        font_small = pygame.font.Font("assets/font/impact.ttf", 30)
        screen.blit(font_big.render("OPTIONS", True, "white"), (420, 50))
        screen.blit(font_small.render("FULLSCREEN", True, "white"), (487, 230))
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 45).render("MUTE", True, "white"), (540, 403))
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 60).render("BACK", True, "white"), (520, 575))

class PlayMenu(Screen):
    def __init__(self, switch_screen, clock):
        # Base initialization
        super().__init__()
        self.bg_color = "blue"
        self.switch_screen = switch_screen
        self.clock = clock
        
        # Game state initialization
        self.battle_state = BoardState()
        self.battle_state.player_hero = card.adventurer()    # Player hero
        self.battle_state.enemy_hero = card.evilGuy()        # Enemy hero

        # Hero card positioner - keep heroes on the sides
        self.player_hero_rect = pygame.Rect(20, height//2 - HERO_CARD_HEIGHT//2, 
                                          HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        self.enemy_hero_rect = pygame.Rect(width - 20 - HERO_CARD_WIDTH, 
                                         height//2 - HERO_CARD_HEIGHT//2,
                                         HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        
        # Create enemy instance and turn manager
        self.enemy = Enemy(self.battle_state)
        self.turn_manager = TurnManager(self, self.enemy)
        
        # Card management initialization
        self.initialize_card_collections()
        self.dragged_card = None
        self.drag_offset = (0, 0)
        self.hand_card_rects = []

        # UI zones initialization
        self.initialize_play_zones()
        self.initialize_ui_elements()

    def initialize_card_collections(self):
        self.playerDeckPile = [card.fireball(), card.someCoolGuy(), card.fireball(), 
                              card.fireball(), card.fireball(), card.fireball(), card.sword()]
        random.shuffle(self.playerDeckPile)
        self.playerHand = []
        self.playerDiscard = []

    def initialize_play_zones(self):
        self.player_front_row_zone = pygame.Rect(300, 87, 200, 300)
        self.player_back_row_zone = pygame.Rect(100, 25, 200, 450)
        self.enemy_front_row_zone = pygame.Rect(780, 87, 200, 300)
        self.enemy_back_row_zone = pygame.Rect(980, 25, 200, 450)

        # Setup play zones
        self.player_front_row_zone = pygame.Rect(440, 87, 200, 300)
        self.player_back_row_zone = pygame.Rect(240, 25, 200, 450)
        self.enemy_front_row_zone = pygame.Rect(640, 87, 200, 300)
        self.enemy_back_row_zone = pygame.Rect(840, 25, 200, 450)

        # Load background
    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (width, height))
        
        self.menu_button = Button((100, 100), "red", (200, 50))
        self.next_turn_button = Button((993, 587), "gray", (240, 128), 
                                     image_path="assets/button/end_turn.png", 
                                     hover_image_path="assets/button/end_turn_hover.png")

        self.buttons = [self.menu_button, self.next_turn_button]
        self.actions = {
            self.menu_button: lambda: self.switch_screen("main_menu"),
            self.next_turn_button: self.end_turn
        }
        self.hand_card_rects = []

    def draw_hero_card(self, screen, hero, rect, is_enemy=False):
        # Draw card background
        color = (200, 0, 0) if is_enemy else (0, 200, 0)  # Red for enemy, green for player
        pygame.draw.rect(screen, color, rect)
        
        # Draw hero name
        font = pygame.font.Font(None, int(24 * 1.8))  # Scaled up font
        text = font.render(hero.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - rect.height//4))
        screen.blit(text, text_rect)
        
        # Draw HP
        hp_text = font.render(f"HP: {hero.hp}", True, (0, 0, 0))
        hp_rect = hp_text.get_rect(center=(rect.centerx, rect.centery + rect.height//4))
        screen.blit(hp_text, hp_rect)

    def end_turn(self):
        # Indlæs kortbilleder
        card_back = pygame.image.load("assets/playingCard/test.png").convert_alpha()
        card_front = pygame.image.load("assets/playingCard/knight.png").convert_alpha()

        # Definer positioner
        deck_pos = (64, 525)  # Startposition (dækket)
        hand_pos = (width // 2 - card_back.get_width() // 2, height // 2 - card_back.get_height() // 2)  # Slutposition (hånden)

        # Spil animationen oven på PlayMenu
        play_card_draw_and_flip_animation(SCREEN, self.clock, card_back, card_front, deck_pos, hand_pos, self.draw, delay_after_flip=1000)

        # End turn using turn manager
        self.turn_manager.end_player_turn()

    def handle_event(self, event):
        super().handle_event(event)

        # Only handle card interactions if it's the player's turn
        if not self.turn_manager.is_player_turn:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check for card clicks in hand first
            for i, rect in enumerate(self.hand_card_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    card = self.playerHand[i]
                    if hasattr(card, 'category') and (card.category == 'minion' or card.category == 'spell' or card.category == 'weapon'):
                        self.dragged_card = self.playerHand.pop(i)
                        self.drag_offset = (mouse_x - rect.x, mouse_y - rect.y)
                    break

            # Only check minions if we didn't grab a card
            if not self.dragged_card:
                for row in [self.battle_state.enemy_front_row, self.battle_state.enemy_back_row,
                          self.battle_state.player_front_row, self.battle_state.player_back_row]:
                    for minion in row:
                        if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                            self.battle_state.handle_minion_click(minion)
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_card:
                mouse_x, mouse_y = event.pos

                # Handle weapon attacks
                if hasattr(self.dragged_card, 'category') and self.dragged_card.category == 'weapon':
                    self.handle_weapon_drop(mouse_x, mouse_y)
                    return

                # Handle spell casting
                elif self.dragged_card.category == 'spell':
                    self.handle_spell_drop(mouse_x, mouse_y)
                    return

                # Handle minion placement
                elif self.dragged_card.category == 'minion':
                    if self.player_front_row_zone.collidepoint(mouse_x, mouse_y):
                        if self.battle_state.add_minion(self.dragged_card, False, True):
                            self.dragged_card = None
                            return

                    elif self.player_back_row_zone.collidepoint(mouse_x, mouse_y):
                        if self.battle_state.add_minion(self.dragged_card, False, False):
                            self.dragged_card = None
                            return

                # If card wasn't used, return to hand
                self._return_card_to_hand(mouse_x)

    def _return_card_to_hand(self, mouse_x):
        """Helper method to return a card to the player's hand."""
        insert_pos = 0
        for i, rect in enumerate(self.hand_card_rects):
            if mouse_x < rect.centerx:
                insert_pos = i
                break
            insert_pos = i + 1
        self.playerHand.insert(insert_pos, self.dragged_card)
        self.dragged_card = None

    def draw_minion_row(self, screen, row, zone_rect):
        spacing = 20
        x = zone_rect.x + (zone_rect.width - CARD_WIDTH) // 2
        y = zone_rect.y + spacing

        for minion in row:
            minion.image = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            # Change color to red if minion is dying (hp <= 0) or yellow if selected for attack
            if minion.hp <= 0:
                color = (200, 0, 0)
            elif minion.is_selected_for_attack:
                color = (200, 200, 0)  # Yellow to indicate attack selection
            else:
                color = (200, 200, 200)
            pygame.draw.rect(screen, color, minion.image)
            
            # Draw minion name and stats
            font = pygame.font.Font(None, 24)
            text = font.render(minion.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + 40, y + 40))
            screen.blit(text, text_rect)
            
            # Add HP display
            hp_text = font.render(f"HP: {minion.hp}", True, (0, 0, 0))
            hp_rect = hp_text.get_rect(center=(x + 40, y + 80))
            screen.blit(hp_text, hp_rect)
            
            y += CARD_HEIGHT + spacing

    # Card Management Methods
    def draw_card(self):
        try:
            if len(self.playerDeckPile) > 0 and len(self.playerHand) < 7:
                minion = self.playerDeckPile.pop(0)
                self.playerHand.append(minion)
            else:
                print("No more cards to draw or hand is full")
        except IndexError:
            print("No more cards to draw.")

    def has_taunt_minion(self, rows):
        for row in rows:
            for minion in row:
                if (hasattr(minion, 'effect') and minion.effect and 
                    'Taunt' in minion.effect and 
                    (minion.name != 'Knight' or minion.is_front_row)):
                    return True
        return False

    # Turn Management Methods
    def end_turn(self):
        card_back = pygame.image.load("assets/playingCard/test.png").convert_alpha()
        card_front = pygame.image.load("assets/playingCard/knight.png").convert_alpha()
        deck_pos = (64, 525)
        hand_pos = (width // 2 - card_back.get_width() // 2, height // 2 - card_back.get_height() // 2)
        
        play_card_draw_and_flip_animation(SCREEN, self.clock, card_back, card_front, 
                                        deck_pos, hand_pos, self.draw, delay_after_flip=1000)
        
        self.draw_card()
        self.is_player_turn = False
        self.enemy.perform_turn()
        self.is_player_turn = True

    # Drawing Methods
    def draw(self, screen):
        # Draw background
        screen.blit(self.background_image, (0, 0))
        
        # Draw heroes
        self.draw_hero_card(screen, self.battle_state.player_hero, self.player_hero_rect)
        self.draw_hero_card(screen, self.battle_state.enemy_hero, self.enemy_hero_rect, True)
        
        # Draw play zones
        pygame.draw.rect(screen, (100, 200, 100), self.player_front_row_zone, 2)
        pygame.draw.rect(screen, (100, 200, 100), self.player_back_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_front_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_back_row_zone, 2)

        # Draw minion rows
        self.draw_minion_row(screen, self.battle_state.player_front_row, self.player_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.player_back_row, self.player_back_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_front_row, self.enemy_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_back_row, self.enemy_back_row_zone)

        # Draw hand and buttons
        self.draw_hand(screen)
        self.draw_dragged_card(screen)
        for button in self.buttons:
            button.run()

    def draw_minion_row(self, screen, row, zone_rect):
        spacing = 20
        x = zone_rect.x + (zone_rect.width - 80) // 2
        y = zone_rect.y + spacing

        for minion in row:
            minion.image = pygame.Rect(x, y, 80, 120)
            color = (200, 0, 0) if minion.hp <= 0 else (200, 200, 0) if minion.is_selected_for_attack else (200, 200, 200)
            pygame.draw.rect(screen, color, minion.image)
            
            font = pygame.font.Font(None, 24)
            text = font.render(minion.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + 40, y + 40))
            screen.blit(text, text_rect)
            
            hp_text = font.render(f"HP: {minion.hp}", True, (0, 0, 0))
            hp_rect = hp_text.get_rect(center=(x + 40, y + 80))
            screen.blit(hp_text, hp_rect)
            
            y += 120 + spacing

    def draw_hand(self, screen):
        self.hand_card_rects = []
        x = 20
        y = height - 150
        for card in self.playerHand:
            card_rect = pygame.Rect(x, y, 80, 120)
            color = self.get_card_color(card)
            pygame.draw.rect(screen, color, card_rect)
            
            font = pygame.font.Font(None, 24)
            text = font.render(card.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + 40, y + 60))
            screen.blit(text, text_rect)
            
            if hasattr(card, 'category') and card.category != 'minion':
                type_text = font.render(card.category.upper(), True, (0, 0, 0))
                type_rect = type_text.get_rect(center=(x + 40, y + 30))
                screen.blit(type_text, type_rect)
            
            self.hand_card_rects.append(card_rect)
            x += 90

    def draw_dragged_card(self, screen):
        if self.dragged_card:
            color = self.get_card_color(self.dragged_card)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(mouse_x - self.drag_offset[0], 
                                  mouse_y - self.drag_offset[1], 80, 120)
            pygame.draw.rect(screen, color, drag_rect)
            font = pygame.font.Font(None, 24)
            text = pygame.font.Font(None, 24).render(self.dragged_card.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(mouse_x - self.drag_offset[0] + 40, 
                                            mouse_y - self.drag_offset[1] + 60))
            screen.blit(text, text_rect)

    def get_card_color(self, card):
        if hasattr(card, 'category'):
            if card.category == 'minion':
                return (200, 200, 200)
            elif card.category == 'spell':
                return (150, 150, 255)
            elif card.category == 'weapon':
                return (255, 200, 200)
        return (200, 200, 200)

    # Event Handling
    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event)

    def handle_mouse_down(self, event):
        mouse_x, mouse_y = event.pos
        for i, rect in enumerate(self.hand_card_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                card = self.playerHand[i]
                if hasattr(card, 'category') and (card.category == 'minion' or card.category == 'spell' or card.category == 'weapon'):
                    self.dragged_card = self.playerHand.pop(i)
                    self.drag_offset = (mouse_x - rect.x, mouse_y - rect.y)
                break

        if not self.dragged_card:
            for row in [self.battle_state.enemy_front_row, self.battle_state.enemy_back_row,
                      self.battle_state.player_front_row, self.battle_state.player_back_row]:
                for minion in row:
                    if minion.image and minion.image.collidepoint(mouse_x, mouse_y):
                        self.battle_state.handle_minion_click(minion)
                        break

    def handle_mouse_up(self, event):
        if self.dragged_card:
            mouse_x, mouse_y = event.pos
            
            if hasattr(self.dragged_card, 'category'):
                if self.dragged_card.category == 'weapon':
                    if use_weapon(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)
                elif self.dragged_card.category == 'spell':
                    if use_spell(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)
                elif self.dragged_card.category == 'minion':
                    if use_minion(self.dragged_card, mouse_x, mouse_y, self.battle_state, 
                                self.player_front_row_zone, self.player_back_row_zone):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)

    def return_card_to_hand(self, mouse_x):
        insert_pos = 0
        for i, rect in enumerate(self.hand_card_rects):
            if mouse_x < rect.centerx:
                insert_pos = i
                break
            insert_pos = i + 1
        self.playerHand.insert(insert_pos, self.dragged_card)
        self.dragged_card = None


class MapMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "white"
        self.switch_screen = switch_screen
        self.screen_ref = screen_ref

class PauseMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = None  # We'll use a transparent overlay instead
        
        # Knap variabler
        button_width = 550
        button_height = 100
        center_x = width // 2 - button_width // 2
        
        self.resume_button = Button((center_x, 200), "red", (button_width, button_height))
        self.main_menu_button = Button((center_x, 350), "red", (button_width, button_height))
        self.quit_button = Button((center_x, 500), "red", (button_width, button_height))
        
        self.buttons = [self.resume_button, self.main_menu_button, self.quit_button]
        self.actions = {
            self.resume_button: lambda: self.switch_screen("resume"),
            self.main_menu_button: lambda: self.switch_screen("main_menu"),
            self.quit_button: lambda: sys.exit()
        }
    
    def draw(self, screen):
        # lav semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # tegn knapper
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)
    
    def draw_labels(self, screen):
        font = pygame.font.Font("assets/font/impact.ttf", 50)
    
        resume_text = font.render("RESUME", True, "white")
        menu_text = font.render("QUIT TO MENU", True, "white")
        quit_text = font.render("QUIT GAME", True, "white")
        
        # placer teksten i midten af knappen
        for button, text in [
            (self.resume_button, resume_text),
            (self.main_menu_button, menu_text),
            (self.quit_button, quit_text)
        ]:
            # udregn tekstens placering
            text_rect = text.get_rect()
            button_center_x = button.pos[0] + button.size[0] // 2
            button_center_y = button.pos[1] + button.size[1] // 2
            text_rect.center = (button_center_x, button_center_y)
            
            # skriv tekst
            screen.blit(text, text_rect)

# map menus (treasure, shop, heal)

class TreasureMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = None  # We'll use a transparent overlay instead
        self.buttons = []  # Initialize with an empty list of buttons

    def draw(self, screen):
        # lav semi-transparent overlay
        treasure_overlay = pygame.Surface((1280, 720))
        treasure_overlay.fill((0, 0, 0))
        treasure_overlay.set_alpha(128)
        screen.blit(treasure_overlay, (0, 0))
        
        # tegn knapper
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

class TreasureMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = None  # We'll use a transparent overlay instead
        self.buttons = []  # Initialize with an empty list of buttons

    def draw(self, screen):
        # lav semi-transparent overlay
        treasure_overlay = pygame.Surface((1280, 720))
        treasure_overlay.fill((0, 0, 0))
        treasure_overlay.set_alpha(128)
        screen.blit(treasure_overlay, (0, 0))
        
        # tegn knapper
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

    def draw_labels(self, screen):
        font = pygame.font.Font("assets/font/impact.ttf", 50)
        if None in self.buttons:
            treasure_text = font.render("You found a treasure!", True, "white")
        treasure_text = font.render("", True, "white")
        text_rect = treasure_text.get_rect(center=(width // 2, height // 2 - 100))
        screen.blit(treasure_text, text_rect)

        # Add more labels or buttons as needed