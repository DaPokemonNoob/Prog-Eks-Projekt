import pygame

def play_card_draw_and_flip_animation(screen, clock, card_back, card_front, deck_pos, hand_pos, playmenu_draw_function, flip_speed=0.05, slide_speed=0.02, delay_after_flip=500):
    # Initialiser variabler
    flip_progress = 0
    slide_progress = 0
    flip_started = False
    current_image = card_back
    card_pos = list(deck_pos)
    drawing_card = True
    flipping = False
    card_width = card_back.get_width()
    card_height = card_back.get_height()

    # Bezier-kontrolpunkt for korttræk-animation
    control_point = (screen.get_width() // 2, screen.get_height() // 2 - 300)

    running = True
    while running:
        # Tegn PlayMenu som baggrund
        playmenu_draw_function(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if drawing_card:
            # Korttræk-animation
            slide_progress += slide_speed
            if slide_progress >= 1:
                slide_progress = 1
                drawing_card = False
                flipping = True

            # Beregn Bezier-position
            card_pos = list(quadratic_bezier(deck_pos, control_point, hand_pos, slide_progress))

            # Beregn vinkel (rejser sig op fra 45° til 0°)
            angle = lerp(45, 0, slide_progress)
            rotated_image = pygame.transform.rotate(current_image, angle)
            rotated_rect = rotated_image.get_rect(center=(card_pos[0] + card_width // 2, card_pos[1] + card_height // 2))
            screen.blit(rotated_image, rotated_rect.topleft)

        elif flipping:
            # Kortflip-animation
            flip_progress += flip_speed
            if flip_progress >= 1:
                flip_progress = 1
                flipping = False

                # Sørg for, at forsiden vises
                pygame.display.flip()

                # Tilføj en forsinkelse for at vise forsiden af kortet
                delay_running = True
                delay_start_time = pygame.time.get_ticks()
                while delay_running:
                    # Tegn PlayMenu som baggrund
                    playmenu_draw_function(screen)

                    # Tegn det aktuelle kort
                    screen.blit(current_image, (card_pos[0], card_pos[1]))

                    # Opdater skærmen
                    pygame.display.flip()

                    # Tjek for events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            delay_running = False
                            running = False

                    # Stop forsinkelsen efter den angivne tid
                    if pygame.time.get_ticks() - delay_start_time >= delay_after_flip:
                        delay_running = False

                # Afslut animationen
                running = False

            if flip_progress < 0.5:
                # Første halvdel af flip: kortet bliver smallere
                scale = 1 - (flip_progress * 2)
            else:
                # Anden halvdel af flip: skift billede og udvid kortet igen
                if not flip_started:
                    current_image = card_front
                    flip_started = True
                scale = (flip_progress - 0.5) * 2

            # Beregn bredde og højde baseret på skaleringsfaktoren
            width = int(current_image.get_width() * scale)
            height = current_image.get_height()
            if width > 0:
                # Skaler billedet og beregn offset for at centrere det
                scaled_image = pygame.transform.scale(current_image, (width, height))
                offset_x = (current_image.get_width() - width) // 2
                screen.blit(scaled_image, (card_pos[0] + offset_x, card_pos[1]))

        # Opdater skærmen og begræns FPS
        pygame.display.flip()
        clock.tick(60)

# Hjælpefunktioner til animation
def lerp(start, end, t):
    return start + (end - start) * t

def quadratic_bezier(p0, p1, p2, t):
    return (
        (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1],
    )