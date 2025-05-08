import pygame
import card_data as card
from card_classes import BoardState, Hero
from enemy import Enemy
from screen import Screen, Button
from settings import *
import random
from animations import play_card_draw_and_flip_animation
from game_logic import (TurnManager, use_weapon, use_minion, use_spell)

class PlayMenu(Screen):
    def __init__(self, switch_screen, clock):
        super().__init__()
        self.switch_screen = switch_screen
        self.clock = clock
              
        # Game state initialization
        self.battle_state = BoardState()
        self.battle_state.player_hero = card.adventurer()    # Player hero
        self.battle_state.enemy_hero = card.evilGuy()        # Enemy hero

        # Laver hero og enemy hero kort (Position: x,y og Størrelse: bredde, højde)
        self.player_hero_rect = pygame.Rect(20, HEIGHT//2 - HERO_CARD_HEIGHT//2, HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        self.enemy_hero_rect = pygame.Rect(WIDTH - 20 - HERO_CARD_WIDTH, HEIGHT//2 - HERO_CARD_HEIGHT//2, HERO_CARD_WIDTH, HERO_CARD_HEIGHT)
        
        # Create enemy instance and turn manager
        self.enemy = Enemy(self.battle_state)
        self.turn_manager = TurnManager(self, self.enemy)

    # denne funktion initialiserer spillerens dæk
        self.playerDeckPile = [card.knight(), card.slimeling(), card.chaosCrystal(), card.fireball(), card.sword()]    # Spillerens dæk
        random.shuffle(self.playerDeckPile)
        self.playerHand = []                                                            #Laver en tom liste til kortene i spillerens hånd
        self.playerDiscard = []                                                         #Laver en tom liste til kortene i spillerens discard pile

        self.dragged_card = None
        self.drag_offset = (0, 0)

        # Setup play zones
        self.player_front_row_zone = pygame.Rect(440, 87, 200, 300)
        self.player_back_row_zone = pygame.Rect(240, 25, 200, 450)
        self.enemy_front_row_zone = pygame.Rect(640, 87, 200, 300)
        self.enemy_back_row_zone = pygame.Rect(840, 25, 200, 450)

        self.background_image = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        
        self.menu_button = Button((100, 100), "red", (200, 50))
        self.next_turn_button = Button((993, 587), "gray", (240, 128), 
                                     image_path="assets/button/end_turn.png", 
                                     hover_image_path="assets/button/end_turn_hover.png")

        self.buttons = [self.menu_button, self.next_turn_button]
        self.actions = {
            self.menu_button: lambda: self.switch_screen("main_menu"),
            self.next_turn_button: self.end_turn
        }
        self.hand_card_rects = []

    def draw_hero_card(self, screen, hero, rect, is_enemy=False):
        # Draw card background
        color = (200, 0, 0) if is_enemy else (0, 200, 0)  # Red for enemy, green for player
        pygame.draw.rect(screen, color, rect)
        
        # Draw hero name
        font = pygame.font.Font(None, int(24 * 1.8))  # Scaled up font
        text = font.render(hero.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - rect.height//4))
        screen.blit(text, text_rect)
        
        # Draw HP
        hp_text = font.render(f"HP: {hero.hp}", True, (0, 0, 0))
        hp_rect = hp_text.get_rect(center=(rect.centerx, rect.centery + rect.height//4))
        screen.blit(hp_text, hp_rect)

    def end_turn(self):
        # Indlæs kortbilleder
        card_back = pygame.image.load("assets/playingCard/test.png").convert_alpha()

        # Dynamisk indlæsning af card_front baseret på card.pic
        card = self.playerDeckPile[0] if self.playerDeckPile else None  # Eksempel: Tag det øverste kort fra bunken
        card_front = None
        if card and card.pic:
            card_front_path = f"assets/playingCard/{card.pic}"
            card_front = pygame.image.load(card_front_path).convert_alpha()
        else:
            print("No card or card.pic is missing!")

        # Definer positioner
        draw_animation_start = (64, 525)  # Startposition (dækket)
        draw_animation_end = (WIDTH // 2 - card_back.get_width() // 2, HEIGHT // 2 - card_back.get_height() // 2)  # Slutposition (hånden)

        # Spil animationen oven på PlayMenu
        if card_front:
            play_card_draw_and_flip_animation(SCREEN, self.clock, card_back, card_front, draw_animation_start, draw_animation_end, self.draw, delay_after_flip=1000)

        # End turn using turn manager
        self.turn_manager.end_player_turn()

    def handle_event(self, event):
        super().handle_event(event)

        # Only handle card interactions if it's the player's turn
        if not self.turn_manager.is_player_turn:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check for card clicks in hand first
            for i, rect in enumerate(self.hand_card_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    card = self.playerHand[i]
                    if hasattr(card, 'category') and (card.category == 'minion' or card.category == 'spell' or card.category == 'weapon'):
                        self.dragged_card = self.playerHand.pop(i)
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

                # Handle weapon attacks
                if self.dragged_card.category == 'weapon':
                    use_weapon(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard)   
                    return

                # Handle spell casting
                elif self.dragged_card.category == 'spell':
                    if use_spell(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.dragged_card = None
                        return

                # Handle minion placement
                elif self.dragged_card.category == 'minion':
                    if self.player_front_row_zone.collidepoint(mouse_x, mouse_y):
                        if self.battle_state.add_minion(self.dragged_card, False, True):
                            self.battle_state.player_front_row.append(self.dragged_card)
                            self.dragged_card = None
                            return

                    elif self.player_back_row_zone.collidepoint(mouse_x, mouse_y):
                        if self.battle_state.add_minion(self.dragged_card, False, False):
                            self.battle_state.player_back_row.append(self.dragged_card)
                            self.dragged_card = None
                            return

                # If card wasn't used, return to hand
                self.return_card_to_hand(mouse_x)

    def return_card_to_hand(self, mouse_x):
        """Helper method to return a card to the player's hand."""
        insert_pos = 0
        for i, rect in enumerate(self.hand_card_rects):
            if mouse_x < rect.centerx:
                insert_pos = i
                break
            insert_pos = i + 1
        self.playerHand.insert(insert_pos, self.dragged_card)
        self.dragged_card = None

    # Drawing Methods
    def draw(self, screen):
        # Draw background
        screen.blit(self.background_image, (0, 0))
        
        # Draw heroes
        self.draw_hero_card(screen, self.battle_state.player_hero, self.player_hero_rect)
        self.draw_hero_card(screen, self.battle_state.enemy_hero, self.enemy_hero_rect, True)
        
        # Draw play zones
        pygame.draw.rect(screen, (100, 200, 100), self.player_front_row_zone, 2)
        pygame.draw.rect(screen, (100, 200, 100), self.player_back_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_front_row_zone, 2)
        pygame.draw.rect(screen, (200, 100, 100), self.enemy_back_row_zone, 2)

        # Draw minion rows
        self.draw_minion_row(screen, self.battle_state.player_front_row, self.player_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.player_back_row, self.player_back_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_front_row, self.enemy_front_row_zone)
        self.draw_minion_row(screen, self.battle_state.enemy_back_row, self.enemy_back_row_zone)

        # Draw hand and buttons
        self.draw_hand(screen)
        self.draw_dragged_card(screen)
        for button in self.buttons:
            button.run()

    def draw_minion_row(self, screen, row, zone_rect):
        spacing = 20
        x = zone_rect.x + (zone_rect.width - CARD_WIDTH) // 2
        y = zone_rect.y + spacing

        for minion in row:
            minion.image = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

            if hasattr(minion, 'pic') and minion.pic:
                image = pygame.image.load(f"assets/playingCard/{minion.pic}").convert_alpha()
                image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(image, (x, y))

            else:
                # Fallback: farvet rektangel
                color = (200, 0, 0) if minion.hp <= 0 else (200, 200, 0) if minion.is_selected_for_attack else (200, 200, 200)
                pygame.draw.rect(screen, color, minion.image)
            
            font = pygame.font.Font(None, 24)
            screen.blit(font.render(str(minion.manaCost), True, (255, 255, 255)), (x + 81, y + 9))
            screen.blit(font.render(str(minion.attack), True, (255, 255, 255)), (x + 11, y + 119))
            screen.blit(font.render(str(minion.hp), True, (255, 255, 255)), (x + 81, y + 119))
            
            
            y += 120 + spacing

    def draw_hand(self, screen):
        self.hand_card_rects = []
        x, y = 370, 570
        for card in self.playerHand:
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if card.pic:
                image = pygame.image.load(f"assets/playingCard/{card.pic}").convert_alpha()
                image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(image, (x, y))
            
            font = pygame.font.Font(None, 24)
            # ManaCost vises for alle kort
            screen.blit(font.render(str(card.manaCost), True, (255, 255, 255)), (x + 81, y + 9))

            # Attack og HP kun for minions
            if hasattr(card, "category") and card.category == "minion":
                screen.blit(font.render(str(card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(card.hp), True, (255, 255, 255)), (x + 81, y + 119))

            elif hasattr(card, "category") and card.category == "weapon":
                screen.blit(font.render(str(card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(card.durability), True, (255, 255, 255)), (x + 81, y + 119))

            else:
                None

            self.hand_card_rects.append(rect)
            x += 100

    def draw_dragged_card(self, screen):
        if self.dragged_card and self.dragged_card.pic:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            x = mouse_x - self.drag_offset[0]
            y = mouse_y - self.drag_offset[1]

            # Indlæs og skaler kortets billede
            image = pygame.image.load(f"assets/playingCard/{self.dragged_card.pic}").convert_alpha()
            image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(image, (x, y))

            # Vis manaCost
            font = pygame.font.Font(None, 24)
            mana_text = font.render(str(self.dragged_card.manaCost), True, (255, 255, 255))
            screen.blit(mana_text, (x + 81, y + 9))

            # Hvis kortet er en minion, vis også attack og hp
            if hasattr(self.dragged_card, "category") and self.dragged_card.category == "minion":
                screen.blit(font.render(str(self.dragged_card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(self.dragged_card.hp), True, (255, 255, 255)), (x + 81, y + 119))

            elif hasattr(self.dragged_card, "category") and self.dragged_card.category == "weapon":
                screen.blit(font.render(str(self.dragged_card.attack), True, (255, 255, 255)), (x + 11, y + 119))
                screen.blit(font.render(str(self.dragged_card.durability), True, (255, 255, 255)), (x + 81, y + 119)) 
                        

    def handle_mouse_up(self, event):
        if self.dragged_card:
            mouse_x, mouse_y = event.pos
            
            if hasattr(self.dragged_card, 'category'):
                if self.dragged_card.category == 'weapon':
                    if use_weapon(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)
                elif self.dragged_card.category == 'spell':
                    if use_spell(self.dragged_card, mouse_x, mouse_y, self.battle_state, self.enemy.discard, self.playerDiscard):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)
                elif self.dragged_card.category == 'minion':
                    if use_minion(self.dragged_card, mouse_x, mouse_y, self.battle_state, 
                                self.player_front_row_zone, self.player_back_row_zone):
                        self.dragged_card = None
                    else:
                        self.return_card_to_hand(mouse_x)

    def return_card_to_hand(self, mouse_x):
        insert_pos = 0
        for i, rect in enumerate(self.hand_card_rects):
            if mouse_x < rect.centerx:
                insert_pos = i
                break
            insert_pos = i + 1
        self.playerHand.insert(insert_pos, self.dragged_card)
        self.dragged_card = None