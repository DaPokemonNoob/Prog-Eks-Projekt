import pygame
import sys
from settings import *

class Button:
    # skabelon til knapper for pygame skærme
    def __init__(self, pos, color, size, image_path=None, hover_image_path=None):
        self.size = size                  # størrelse på knappen (bredde, højde)
        self.pos = pos                    # position på knappen (x, y)
        self.color = color                # farve på knappen (f.eks. "red")
        self.original_color = color       # gemmer den originale farve på knappen
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1]) # rektangel til knappen
        self.button_image = None          # billede til knappen
        self.hover_image = None           # billede til hover tilstand - når musen er over knappen
        if image_path:                    # hvis der er et billede til knappen så load det, udskift det med hover billedet hvis musen er over knappen
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

    # funktion til at tegne knappen på skærmen
    def draw(self, screen):
        if self.check_hover() and self.hover_image: # hvis musen er over knappen og der er et hover billede så tegn det
            screen.blit(self.hover_image, self.pos)
        elif self.button_image:                     # hvis musen ikke er over knappen og der er et billede til knappen så tegn det
            screen.blit(self.button_image, self.pos)
        else:
            pygame.draw.rect(screen, self.color, self.image) # hvis der ikke er billeder så tegn knappen som en rektangel

    # funktion til at tjekke om musen er over knappen
    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.image.collidepoint(mouse_pos)

    # funktion til at ændre farven på knappen når musen er over den hvis der ikke er billeder til knappen
    def hover_color(self, hover_color):
        if not self.button_image and not self.hover_image:
            if self.check_hover():
                self.color = hover_color
            else:
                self.color = self.original_color

    # funktion der kører draw og hover_color funktionerne - tegner knappen og ændrer farven hvis musen er over den
    def run(self):
        self.hover_color("green")
        self.draw(SCREEN)

class Screen:
    # skabelon til pygame skærme
    def __init__(self):
        self.buttons = []          # liste til knapper på skærmen
        self.actions = {}          # dictionary til handlinger der skal udføres når knappen trykkes
        self.bg_color = "black"    # baggrundsfarve på skærmen

    # funktion til at initialisere knapperne og deres handlinger
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for button, action in self.actions.items():
                if button.image.collidepoint(pos):
                    action()

    # funktion til at tegne skærmen og knapperne på den
    def draw(self, screen):
        screen.fill(self.bg_color)
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)

    # funktion til at tegne labels på skærmen - skal overskrives i de enkelte skærme
    def draw_labels(self, screen):
        pass

'''skærme i spillet: main menu, map menu, pause menu, win/lose menu, options menu - skærme fra levels: heal menu, shop menu, boss menu'''

# main menu
class MainMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.bg_color = "salmon"                                      # baggrundsfarve til main menuen
        self.switch_screen = switch_screen                            # funktion til at skifte skærm

        self.play_button = Button((480, 200), "red", (300, 100))      # knap til at skifte til play menuen
        self.options_button = Button((480, 380), "red", (300, 100))   # knap til at skifte til options menuen
        self.quit_button = Button((480, 560), "red", (300, 100))      # knap til at quit spillet

        self.buttons = [self.play_button, self.options_button, self.quit_button] # liste til knapperne på skærmen

        self.actions = {
            self.play_button: lambda: self.switch_screen("play_menu"),       # handling til play knappen    - skifter til play menuen 
            self.options_button: lambda: self.switch_screen("options_menu"), # handling til options knappen - skifter til options menuen
            self.quit_button: lambda: sys.exit()                             # handling til quit knappen    - lukker spillet
        }

    # funktion til at tegne tekst på skærmen
    def draw_labels(self, screen):
        font_large = pygame.font.Font("assets/font/impact.ttf", 70)    # stor tekst til main menuen
        font_play = pygame.font.Font("assets/font/impact.ttf", 65)     # tekst til play knappen
        font_options = pygame.font.Font("assets/font/impact.ttf", 45)  # tekst til options knappen
        font_quit = pygame.font.Font("assets/font/impact.ttf", 35)     # tekst til quit knappen
  
        screen.blit(font_large.render("MAIN MENU", True, "black"), (360, 50))  # tegn "MAIN MENU" teksten
        screen.blit(font_play.render("PLAY", True, "black"), (515, 210))       # tegn "PLAY" teksten
        screen.blit(font_options.render("OPTIONS", True, "black"), (495, 403)) # tegn "OPTIONS" teksten
        screen.blit(font_quit.render("QUIT GAME", True, "black"), (490, 590))  # tegn "QUIT GAME" teksten

# map menu
class MapMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "white"                     # baggrundsfarve til map menuen
        self.switch_screen = switch_screen          # funktion til at skifte skærm
        self.screen_ref = screen_ref                # reference til skærmen - hvilken skærm mappet skal tegnes på

# pause menu
class PauseMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen          # funktion til at skifte skærm
        self.bg_color = None                        # transparent baggrund
        
        # Knap variabler
        button_width = 550
        button_height = 100
        center_x = WIDTH // 2 - button_width // 2
        
        self.resume_button = Button((center_x, 200), "red", (button_width, button_height))     # knap til at resume spillet
        self.main_menu_button = Button((center_x, 350), "red", (button_width, button_height))  # knap til at skifte til main menuen
        self.quit_button = Button((center_x, 500), "red", (button_width, button_height))       # knap til at quit spillet
        
        self.buttons = [self.resume_button, self.main_menu_button, self.quit_button]
        self.actions = {
            self.resume_button: lambda: self.switch_screen("resume"),                          # handling til resume knappen - starter spillet igen
            self.main_menu_button: lambda: self.switch_screen("main_menu"),                    # handling til main menu knappen - skifter til main menuen
            self.quit_button: lambda: self.switch_screen("quit"),                              # handling til quit knappen - lukker spillet
            self.quit_button: lambda: sys.exit()
        }
    
    # funktion til at tegne baggrunden og knapper på skærmen
    def draw(self, screen):
        # lav semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128) # sæt alpha til 128 for at gøre det semi-transparent
        screen.blit(overlay, (0, 0))
        
        # tegn knapper
        for button in self.buttons:
            button.run()
        self.draw_labels(screen)
    
    # funktion til at tegne tekst på skærmen
    def draw_labels(self, screen):
        font = pygame.font.Font("assets/font/impact.ttf", 50)
    
        resume_text = font.render("RESUME", True, "white")      # tegn "RESUME" teksten
        menu_text = font.render("QUIT TO MENU", True, "white")  # tegn "QUIT TO MENU" teksten
        quit_text = font.render("QUIT GAME", True, "white")     # tegn "QUIT GAME" teksten
        
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

# map menus (heal, shop, boss)

# heal menu
class HealMenu(Screen):
    def __init__(self, switch_screen, player_hero=None):
        super().__init__()
        self.switch_screen = switch_screen     # funktion til at skifte skærm
        self.bg_color = "green"                # baggrundsfarve til heal menuen
        self.player_hero = player_hero         # spillerens hero objekt - bruges til at heale spilleren

        # knap variabler
        button_width = 400
        button_height = 100
        
        left_x = WIDTH // 4 - button_width // 2
        right_x = (WIDTH * 3) // 4 - button_width // 2
        middle_y = HEIGHT // 2 - button_height // 2
        
        # laver knapperne til heal
        self.heal_50_button = Button((left_x, middle_y), "red", (button_width, button_height))  # knap til at heale 50% af max hp
        self.max_hp_button = Button((right_x, middle_y), "red", (button_width, button_height))  # knap til at øge max hp med 5
        
        self.buttons = [self.heal_50_button, self.max_hp_button]
        self.actions = {
            self.heal_50_button: self.heal_50_percent,               # handling til heal knappen   - heale 50% af max hp
            self.max_hp_button: self.increase_max_hp                 # handling til max hp knappen - øge max hp med 5
        }
        self.initialize_ui_elements(SCREEN)

    # funktion til at heale heroen 50% af max hp
    def heal_50_percent(self):
        if self.player_hero:
            heal_amount = self.player_hero.max_hp * 0.5 # beregn 50% af max hp
            self.player_hero.current_hp = min( 
                self.player_hero.current_hp + heal_amount,
                self.player_hero.max_hp
            ) # sæt heroens nuværende hp til max hp hvis det er højere end max hp
            print(f"Healed {heal_amount} HP. Current HP: {self.player_hero.current_hp}") # udskriv hvor meget der er healet og den nuværende hp
            self.switch_screen("map_menu") # skift tilbage til map menuen

    # funktion til at øge max hp med 5
    def increase_max_hp(self):
        if self.player_hero:
            self.player_hero.max_hp += 5     # øg max hp med 5
            self.player_hero.current_hp += 5 # øg nuværende hp med 5
            print(f"Increased max HP by 5. New max HP: {self.player_hero.max_hp}")
            self.switch_screen("map_menu") 

    # funktion til at tegne baggrunden og knapperne på skærmen
    def draw(self, screen):
            # tegn baggrundsbilledet
            screen.blit(self.background_image, (0, 0))
            
            # tegn knapperne
            for button in self.buttons:
                button.run()

            # tegn knap tekst
            font = pygame.font.Font("assets/font/impact.ttf", 30)
            heal_text = font.render("HEAL 50% HP", True, "white")
            max_hp_text = font.render("GAIN 5 MAX HP", True, "white")
            
            # placer teksten i midten af knappen
            for button, text in [
                (self.heal_50_button, heal_text),
                (self.max_hp_button, max_hp_text)
            ]:
                text_rect = text.get_rect()
                button_center_x = button.pos[0] + button.size[0] // 2
                button_center_y = button.pos[1] + button.size[1] // 2
                text_rect.center = (button_center_x, button_center_y)
                screen.blit(text, text_rect)

    # funktion til at initialisere baggrunden på skærmen
    def initialize_ui_elements(self, screen):
        self.background_image = pygame.image.load("assets/background/heal_site.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

# shop menu - blev ikke færdiggjort i denne version
class ShopMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen    # funktion til at skifte skærm
        self.bg_color = "blue"                # baggrundsfarve til shop menuen
        self.buttons = []                     # liste til knapperne på skærmen
        self.initialize_ui_elements()

    # funktion til at tegne baggrunden på skærmen
    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

    # funktion til at initialisere baggrunden på skærmen
    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

# boss menu - blev ikke færdiggjort/brugt i denne version
class BossMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen   # funktion til at skifte skærm
        self.bg_color = "purple"             # baggrundsfarve til boss menuen
        self.buttons = []                     # liste til knapperne på skærmen
        self.initialize_ui_elements()

    # funktion til at tegne baggrunden på skærmen
    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)

    # funktion til at initialisere baggrunden på skærmen
    def initialize_ui_elements(self):
        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

# win/lose screens
# win menu
class WinMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen    # funktion til at skifte skærm
        self.bg_color = None                  # Transparent baggrund
    
    # funktion til at tegne baggrunden og tekst på skærmen
    def draw(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128) # sæt alpha til 128 for at gøre det semi-transparent
        screen.blit(overlay, (0, 0))
        
        # tegn "YOU WIN!!!" text
        font = pygame.font.Font("assets/font/impact.ttf", 100)
        text = font.render("YOU WIN!!!", True, "green")
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)

# lose menu
class LoseMenu(Screen):
    def __init__(self, switch_screen):
        super().__init__()
        self.switch_screen = switch_screen    # funktion til at skifte skærm
        self.bg_color = None                  # Transparent baggrund
    
    # funktion til at tegne baggrunden og tekst på skærmen
    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128) # sæt alpha til 128 for at gøre det semi-transparent
        screen.blit(overlay, (0, 0))
        
        # Draw "YOU LOSE" text
        font = pygame.font.Font("assets/font/impact.ttf", 100)
        text = font.render("YOU LOSE", True, "red")
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)

# options menu
class OptionsMenu(Screen):
    def __init__(self, switch_screen, screen_ref):
        super().__init__()
        self.bg_color = "black"              # baggrundsfarve til options menuen
        self.switch_screen = switch_screen   # funktion til at skifte skærm
        self.screen_ref = screen_ref         # reference til skærmen - hvilken skærm options menuen skal tegnes på

        self.fullscreen_button = Button((480, 200), "red", (300, 100))  # knap til at skifte til fullscreen
        self.mute_button = Button((480, 380), "red", (300, 100))        # knap til at mute lyden
        self.back_button = Button((480, 560), "red", (300, 100))        # knap til at skifte tilbage til main menuen

        self.buttons = [self.fullscreen_button, self.mute_button, self.back_button]
        self.actions = {
            self.fullscreen_button: self.toggle_fullscreen,             # handling til fullscreen knappen - skifter til fullscreen
            self.mute_button: self.toggle_mute,                         # handling til mute knappen - muter lyden
            self.back_button: lambda: self.switch_screen("main_menu")   # handling til back knappen - skifter tilbage til main menuen
        }

    # funktion til at lave skærmen fullscreen eller vindue
    def toggle_fullscreen(self):
        if self.screen_ref.get_flags() & pygame.FULLSCREEN:
            self.screen_ref = pygame.display.set_mode((1280, 720))
        else:
            self.screen_ref = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN) # giver skærmen et fullscreen flag - det gør at den fylder hele skærmen

    # funktion til at mute lyden
    def toggle_mute(self):
        # tjekker om lyden er muted eller ej - hvis den er muted så unmute den og hvis den ikke er muted så mute den
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit() 
        else:
            pygame.mixer.init()

    # funktion til at tegne tekst på skærmen
    def draw_labels(self, screen):
        font_big = pygame.font.Font("assets/font/impact.ttf", 70)                                              # stor tekst til options menuen
        font_small = pygame.font.Font("assets/font/impact.ttf", 30)                                            # lille tekst til knapperne
        screen.blit(font_big.render("OPTIONS", True, "white"), (420, 50))                                      # tegn "OPTIONS" teksten
        screen.blit(font_small.render("FULLSCREEN", True, "white"), (487, 230))                                # tegn "FULLSCREEN" teksten
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 45).render("MUTE", True, "white"), (540, 403))  # tegn "MUTE" teksten
        screen.blit(pygame.font.Font("assets/font/impact.ttf", 60).render("BACK", True, "white"), (520, 575))  # tegn "BACK" teksten