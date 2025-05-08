import pygame

# pygame initialisering
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcane Clash")
clock = pygame.time.Clock()
FPS = 60

# kort størrelses konstanter
CARD_WIDTH = 100
CARD_HEIGHT = 140
HERO_SCALE = 2
HERO_CARD_WIDTH = int(CARD_WIDTH * HERO_SCALE)
HERO_CARD_HEIGHT = int(CARD_HEIGHT * HERO_SCALE)