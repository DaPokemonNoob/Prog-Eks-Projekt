import pygame
import sys
import os
from playingCards import Deck

width, height = 1280, 720
SCREEN = pygame.display.set_mode((width, height))
suit_map = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}

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
    def __init__(self, switch_screen):
        super().__init__()
        self.bg_color = "blue"
        self.switch_screen = switch_screen
        self.is_player_turn = True

        from card_data import someGuy, someCoolGuy, knight
        from card_classes import BoardState, Hero
        self.battle_state = BoardState()
        self.battle_state.player_hero = Hero("Adventurer", attack=1, hp=15)
        
        self.minion_deck = [someGuy(), someCoolGuy(), knight(), someGuy(), someCoolGuy(), knight()]
        self.enemy_deck = [someGuy(), someCoolGuy(), knight(), someGuy(), someCoolGuy(), knight()]
        self.hand = []
        self.discard = []
        self.enemy_hand = []
        self.enemy_discard = []

        self.dragged_card = None
        self.drag_offset = (0, 0)

        self.player_front_row_zone = pygame.Rect(300, 87, 200, 300) #top-right corner x-position, top-right corner y-position, width, height
        self.player_back_row_zone = pygame.Rect(100, 25, 200, 450)  #top-right corner x-position, top-right corner y-position, width, height
        self.enemy_front_row_zone = pygame.Rect(780, 87, 200, 300)  #top-right corner x-position, top-right corner y-position, width, height
        self.enemy_back_row_zone = pygame.Rect(980, 25, 200, 450)   #top-right corner x-position, top-right corner y-position, width, height

        self.background_image = pygame.image.load("assets/background/playscreen1.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (width, height))

        self.menu_button = Button((100, 100), "red", (200, 50))
        self.next_turn_button = Button((993, 587), "gray", (240, 128), image_path="assets/button/end_turn.png", hover_image_path="assets/button/end_turn_hover.png")

        self.buttons = [self.menu_button, self.next_turn_button]
        self.actions = {
            self.menu_button: lambda: self.switch_screen("main_menu"),
            self.next_turn_button: self.end_turn
        }
        self.hand_card_rects = []

    def end_turn(self):
        self.draw_card()
        self.is_player_turn = False
        self.enemy_turn()

    def enemy_turn(self):
        # Draw a card for enemy
        if len(self.enemy_deck) > 0 and len(self.enemy_hand) < 7:
            enemy_minion = self.enemy_deck.pop(0)
            self.enemy_hand.append(enemy_minion)
        
        # Place a minion if possible
        if len(self.battle_state.enemy_front_row) < 3 and len(self.enemy_hand) > 0:
            # Place first card from enemy hand
            enemy_minion = self.enemy_hand.pop(0)
            self.battle_state.add_minion(enemy_minion, True, True)
        
        # Attack with enemy minions
        for minion in self.battle_state.enemy_front_row:
            if not self.battle_state.player_front_row:
                self.battle_state.player_hero.hp -= minion.attack
            elif self.battle_state.player_front_row:
                target = self.battle_state.player_front_row[0]
                target.hp -= minion.attack
                if target.hp <= 0:
                    self.battle_state.player_front_row.remove(target)
                    self.discard.append(target)
        
        self.is_player_turn = True
    

    def draw_card(self):
        try:
            if len(self.minion_deck) > 0 and len(self.hand) < 7:
                minion = self.minion_deck.pop(0)
                self.hand.append(minion)
            else:
                print("No more cards to draw or hand is full")
        except IndexError:
            print("No more cards to draw.")

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check for card clicks in hand first
            for i, rect in enumerate(self.hand_card_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    self.dragged_card = self.hand.pop(i)
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

                if self.player_front_row_zone.collidepoint(mouse_x, mouse_y):
                    if self.battle_state.add_minion(self.dragged_card, False, True):
                        self.dragged_card = None
                        return

                elif self.player_back_row_zone.collidepoint(mouse_x, mouse_y):
                    if self.battle_state.add_minion(self.dragged_card, False, False):
                        self.dragged_card = None
                        return

                # If not placed in a valid zone, return to hand
                insert_pos = 0
                for i, rect in enumerate(self.hand_card_rects):
                    if mouse_x < rect.centerx:
                        insert_pos = i
                        break
                    insert_pos = i + 1
                self.hand.insert(insert_pos, self.dragged_card)
                self.dragged_card = None

    def draw_minion_row(self, screen, row, zone_rect):
        spacing = 20
        x = zone_rect.x + (zone_rect.width - 80) // 2
        y = zone_rect.y + spacing

        for minion in row:
            minion.image = pygame.Rect(x, y, 80, 120)
            # Change color to red if minion is dying (hp <= 0)
            color = (200, 0, 0) if minion.hp <= 0 else (200, 200, 200)
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
            
            y += 120 + spacing

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

        # Draw row zones
        pygame.draw.rect(screen, (100, 200, 100), self.player_front_row_zone, 2)
        pygame.draw.rect(screen, (100, 200, 100), self.player_back_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_front_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_back_row_zone, 2)

        self.draw_minion_row(screen, self.battle_state.player_front_row, self.player_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.player_back_row, self.player_back_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_front_row, self.enemy_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_back_row, self.enemy_back_row_zone)

        # Draw hand
        self.hand_card_rects = []
        x = 20
        y = height - 150
        for minion in self.hand:
            card_rect = pygame.Rect(x, y, 80, 120)
            pygame.draw.rect(screen, (200, 200, 200), card_rect)
            # Draw minion name
            font = pygame.font.Font(None, 24)
            text = font.render(minion.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + 40, y + 60))
            screen.blit(text, text_rect)
            self.hand_card_rects.append(card_rect)
            x += 90

        # Draw dragged card
        if self.dragged_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(mouse_x - self.drag_offset[0], 
                                  mouse_y - self.drag_offset[1], 80, 120)
            pygame.draw.rect(screen, (200, 200, 200), drag_rect)
            # Draw minion name
            font = pygame.font.Font(None, 24)
            text = font.render(self.dragged_card.name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(mouse_x - self.drag_offset[0] + 40, 
                                            mouse_y - self.drag_offset[1] + 60))
            screen.blit(text, text_rect)

class MapMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "white"
        self.switch_screen = switch_screen
        self.screen_ref = screen_ref