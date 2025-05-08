# Brugte biblioteker
import pygame
from settings import CARD_WIDTH, CARD_HEIGHT

# Funktion der animerer korttræk
def play_card_draw_and_flip_animation(screen, clock, card_back, card_front, deck_pos, hand_pos, playmenu_draw_function, flip_speed=0.05, slide_speed=0.02, delay_after_flip=500):
    flip_progress = 0                           # Hvor langt kortet er i flip-animationen (0-1)
    slide_progress = 0                          # Hvor langt kortet er i træk-animationen (0-1)       
    flip_started = False                        # Om flip-animationen er startet
    current_image = card_back                   # Billede der vises under animationen (start med kortets bagside)
    card_pos = list(deck_pos)                   # Positionen af kortet under animationen
    drawing_card = True                         # Om kortet bliver trukket  
    flipping = False                            # Om kortet bliver flip'et
    card_width = card_back.get_width()          # Bredde af kortet
    card_height = card_back.get_height()        # Højde af kortet

    # Bezier-kontrolpunkt for korttræk-animation
    control_point = (screen.get_width() // 2, screen.get_height() // 2 - 300)

    # Starter løkke der kører animationen
    running = True
    while running:
        # Tegner PlayMenu som baggrund hvert frame
        playmenu_draw_function(screen)

        # Gør det muligt at lukke vinduet under animationen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Tjekker om kortet bliver trukket
        if drawing_card:
            slide_progress += slide_speed       # Kortet bevæger sig mod midten af skærmen
            # Hvis den når slutningen af sliden
            if slide_progress >= 1:
                slide_progress = 1
                drawing_card = False            
                flipping = True                 # Når kortet er trukket, skift til flip-animation

            # Beregner kortets position langs en Bezier-kurve
            card_pos = list(quadratic_bezier(deck_pos, control_point, hand_pos, slide_progress))

            # Beregn vinkel (rejser sig op fra 45° til 0°)
            angle = lerp(45, 0, slide_progress)                                                # (lerp er lineær interpolation, altså en glidende overgang mellem 2 kendte værdier)
            rotated_image = pygame.transform.rotate(current_image, angle)                                                       # Roterer billedet                               
            rotated_rect = rotated_image.get_rect(center=(card_pos[0] + card_width // 2, card_pos[1] + card_height // 2))
            screen.blit(rotated_image, rotated_rect.topleft)                                                                    # Tegner det roterede billede på skærmen                           

        # Hvis kortet skal flip'es
        elif flipping:
            flip_progress += flip_speed
            # Hvis flip-animationen er færdig
            if flip_progress >= 1:
                flip_progress = 1
                flipping = False

                # Sørger for at billedet er det rigtige (forsiden af kortet)
                pygame.display.flip()

                # Tilføj en forsinkelse for at vise forsiden af kortet
                delay_running = True
                delay_start_time = pygame.time.get_ticks()
                # Imens der er delay
                while delay_running:
                    playmenu_draw_function(screen)              # Tegn PlayMenu som baggrund hvert frame

                    # Tegn det aktuelle kort
                    screen.blit(current_image, (card_pos[0], card_pos[1]))

                    # Opdater skærmen
                    pygame.display.flip()

                    # Gør det muligt at lukke vinduet under forsinkelsen
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            delay_running = False
                            running = False

                    # Stop forsinkelsen efter den angivne tid
                    if pygame.time.get_ticks() - delay_start_time >= delay_after_flip:
                        delay_running = False

                # Afslut animationen
                running = False

            # Hvis flippet et mindre end halvejs
            if flip_progress < 0.5:
                scale = 1 - (flip_progress * 2)     # så beregnes skaleringen
            # Hvis flippet er over halvejs
            else:
                if not flip_started:
                    current_image = card_front      # Skift til forsiden af kortet
                    flip_started = True             # Flip startes
                scale = (flip_progress - 0.5) * 2   # så beregnes skaleringen

            width = int(current_image.get_width() * scale)          # Beregner bredden af billedet udfra skaleringen
            height = current_image.get_height()                     # Højden forbliver den samme
            # Hvis bredden er større end 0 (for at undgå negative værdier)
            if width > 0:
                # Skaler billedet og beregn offset for at centrere det
                scaled_image = pygame.transform.scale(current_image, (width, height))   # Skalerer billedet
                offset_x = (current_image.get_width() - width) // 2                     # Beregn offset for at centrere billedet
                screen.blit(scaled_image, (card_pos[0] + offset_x, card_pos[1]))        # Tegner det skalerede billede på skærmen

        # Opdater skærmen og begrænser FPS
        pygame.display.flip()
        clock.tick(60)

# Funktion der beregner lineær interpolation mellem 2 værdier
def lerp(start, end, t):
    return start + (end - start) * t

# Værdierne for en Bezier-kurve
def quadratic_bezier(p0, p1, p2, t):
    return (
        (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1],
    )

# Funktion der animerer kortangreb
def play_attack_animation(screen, clock, attacker_pos, target_pos, card_image, playmenu_draw_function, attack_speed=0.05, delay_after_attack=500):
    # Skalere kortbilledet til den rigtige størrelse
    card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
    attack_progress = 0                 # Hvor langt angrebet er i animationen (0-1)
    returning = False                   # Om kortet er på vej tilbage til sin oprindelige position
    current_pos = list(attacker_pos)    # Den nuværende position af kortet under animationen

    # Animationen kører
    running = True
    while running:
        # Gør det muligt at lukke vinduet under animationen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Tegner PlayMenu som baggrund hvert frame
        playmenu_draw_function(screen)

        # Hvis kortet ikke er på vej tilbage, så opdaterer angrebsfremdriften
        if not returning:
            attack_progress += attack_speed
            # Hvis angrebsfremdriften er over eller = 1, så skift til tilbagevenden
            if attack_progress >= 1:
                attack_progress = 1
                returning = True
        # Hvis kortet er på vej tilbage, så opdaterer angrebsfremdriften med - speed
        else:
            attack_progress -= attack_speed
            if attack_progress <= 0:
                attack_progress = 0
                running = False

        # Beregner positionen af kortet under animation
        if not returning:
            current_pos[0] = lerp(attacker_pos[0], target_pos[0], attack_progress)          # Lerp mellem angriberens og målets positioner
            current_pos[1] = lerp(attacker_pos[1], target_pos[1], attack_progress)
        else:
            current_pos[0] = lerp(target_pos[0], attacker_pos[0], 1 - attack_progress)
            current_pos[1] = lerp(target_pos[1], attacker_pos[1], 1 - attack_progress)

        # Tegner kortet under animationen
        screen.blit(card_image, current_pos)

        # Opdaterer skærmen og begrænser FPS
        pygame.display.flip()
        clock.tick(60)

    # Laver et delay efter angrebet
    pygame.time.delay(delay_after_attack)