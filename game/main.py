import pygame, sys

# starter pygame
pygame.init()

# viser hvor stort spillet skal være og sætter navn og icon til spillet
SCREEN = pygame.display.set_mode((1280, 720))
SCREEN.fill("salmon")
clock = pygame.time.Clock()

pygame.display.set_caption("test")

class Button:
    def __init__(self, pos, color, size):
        self.size = size
        self.pos = pos
        self.color = color
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def draw(self, screen):
        # tegner knappen på skærmen
        pygame.draw.rect(screen, self.color, self.image)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.image.collidepoint(pygame.mouse.get_pos()):
                    SCREEN.fill("blue")

def play_menu():
    while True:
        # viser baggrunden på skærmen
        SCREEN.fill("green")

        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        # button to quit the game
        QUIT_BUTTON = Button((100,100), "red", (200, 50))
        QUIT_BUTTON.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)
        pygame.display.update()

def main_menu():
    # while true loop der laver "main menu" delen af spillet
    while True:
        # viser baggrunden på skærmen

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # button to quit the game
        QUIT_BUTTON = pygame.Rect(100, 100, 200, 50)
        pygame.draw.rect(SCREEN, "red", QUIT_BUTTON)

        PLAY_BUTTON = pygame.Rect(100, 200, 200, 50)
        pygame.draw.rect(SCREEN, "green", PLAY_BUTTON)
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if QUIT_BUTTON.collidepoint(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.collidepoint(MENU_MOUSE_POS):
                    play_menu()
                    

        clock.tick(60)
        pygame.display.update()
        
# starter spillet på main menuen
main_menu() 