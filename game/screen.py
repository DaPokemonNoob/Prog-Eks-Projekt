import pygame
import sys
from settings import *

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
            self.play_button: lambda: self.switch_screen("play_menu"),
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
        center_x = WIDTH // 2 - button_width // 2
        
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
        overlay = pygame.Surface((WIDTH, HEIGHT))
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

class HealMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = "green"
        self.buttons = []  # Initialize with an empty list of buttons
        self.initialize_ui_elements()

    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

class BattleMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = "red"
        self.buttons = []  # Initialize with an empty list of buttons
        self.initialize_ui_elements()

    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

class ShopMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = "blue"
        self.buttons = []  # Initialize with an empty list of buttons
        self.initialize_ui_elements()

    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

class BossMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = "purple"
        self.buttons = []  # Initialize with an empty list of buttons
        self.initialize_ui_elements()

    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

# win/lose screens

class WinMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = None  # Transparent background
    
    def draw(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw "YOU LOSE" text
        font = pygame.font.Font("assets/font/impact.ttf", 100)
        text = font.render("YOU WIN!!!", True, "green")
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)
class LoseMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen
        self.bg_color = None  # Transparent background
    
    def draw(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw "YOU LOSE" text
        font = pygame.font.Font("assets/font/impact.ttf", 100)
        text = font.render("YOU LOSE", True, "red")
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)

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