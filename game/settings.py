import pygame

WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Card size constants
CARD_WIDTH = 100
CARD_HEIGHT = 140
HERO_SCALE = 2
HERO_CARD_WIDTH = int(CARD_WIDTH * HERO_SCALE)
HERO_CARD_HEIGHT = int(CARD_HEIGHT * HERO_SCALE)