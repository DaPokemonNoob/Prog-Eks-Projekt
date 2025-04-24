import pygame, sys

# starter pygame
pygame.init()

# viser hvor stort spillet skal være og sætter navn og icon til spillet
SCREEN = pygame.display.set_mode((1280, 720))
SCREEN.fill("salmon")
clock = pygame.time.Clock()

pygame.display.set_caption("test")

def main_menu():
    # while true loop der laver "main menu" delen af spillet
    while True:
        # viser baggrunden på skærmen

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # button to quit the game
        QUIT_BUTTON = pygame.Rect(100, 100, 200, 50)
        pygame.draw.rect(SCREEN, "red", QUIT_BUTTON)
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if QUIT_BUTTON.collidepoint(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        clock.tick(60)
        pygame.display.update()
        
# starter spillet på main menuen
main_menu() 