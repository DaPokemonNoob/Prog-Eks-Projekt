import pygame, sys

# starter pygame
pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("test")

# state to track which menu we're in
current_screen = "main_menu"

class Button:
    def __init__(self, pos, color, size):
        self.size = size
        self.pos = pos
        self.color = color
        self.image = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.image)

def show_play_menu():
    global current_screen  # <- this is important
    SCREEN.fill("blue")
    PLAY_MOUSE_POS = pygame.mouse.get_pos()

    MENU_BUTTON = Button((100, 100), "red", (200, 50))
    MENU_BUTTON.draw(SCREEN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if MENU_BUTTON.image.collidepoint(PLAY_MOUSE_POS):
                current_screen = "main_menu"
                print("Switched to main menu")

    pygame.display.update()


def show_main_menu():
    global current_screen
    SCREEN.fill("salmon")
    MENU_MOUSE_POS = pygame.mouse.get_pos()

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
            if PLAY_BUTTON.collidepoint(MENU_MOUSE_POS):
                current_screen = "play_menu"
                print("Switched to play menu")

    pygame.display.update()

# === Main loop ===
running = True
while running:
    if current_screen == "main_menu":
        show_main_menu()
    elif current_screen == "play_menu":
        show_play_menu()

    clock.tick(60)