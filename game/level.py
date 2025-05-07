import random
import pygame

class Level: 
    current_level = None # definerer en klassevariabel til at holde styr på det nuværende level
    # definerer en klasse til at repræsentere et level i spillet
    def __init__(self, id, level_number, encounter_type=None):
        self.id = id
        self.level_number = level_number
        self.encounter_type = encounter_type
        self.next_level = []
        self.radius = 20

    def is_clickable(self):
        # definerer en funktion til at håndtere klik på leveler
        mouse_x, mouse_y = pygame.mouse.get_pos() # henter musens position
        distance = ((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2) ** 0.5 # beregner afstanden mellem musen og levelet

        if distance <= self.radius:
            if Level.current_level is None:
                # laver første gruppe af levels clickable hvis intet level er valgt
                return self.level_number == 0
            return self in Level.current_level.next_level
        
        return False

    @classmethod
    def set_current_level(cls, level):
        # definerer en klassemetode til at sætte det nuværende level
        cls.current_level = level

def verificer_map(map_levels):
    # definerer en funktion til at verificere kortet
    start_levels = map_levels[0]
    tilgængelige_levels = set(start_levels) # opretter et sæt af tilgængelige leveler

    def find_næste_level(level): # definerer en indre funktion til at finde næste level
        if level.id not in tilgængelige_levels:
            tilgængelige_levels.add(level.id)
            for next_level in level.next_level:
                find_næste_level(next_level) # kalder dfs funktionen for at finde næste level

    for level in start_levels:
        find_næste_level(level)

    alle_levels = {level.id: level for group in map_levels for level in group} # opretter et dictionary af alle leveler

    utilgængelig = set(alle_levels.keys()) - tilgængelige_levels # finder de utilgængelige leveler

    if utilgængelig:
        for level_id in utilgængelig:
            utilgængelig_level = alle_levels[level_id]
            level_gruppe = utilgængelig_level.level_number

            if level_gruppe > 0:
                tidligere_gruppe = map_levels[level_gruppe - 1]
                random_tidligere_level = random.choice(tidligere_gruppe) # vælger et tilfældigt level fra den tidligere gruppe
                random_tidligere_level.next_level.append(utilgængelig_level) # tilføjer det utilgængelige level til den tidligere gruppe
        
def handle_click(mouse_pos, map_levels):
    for level_group in map_levels:
        for level in level_group:
            if level.is_clickable():
                # levelet kunne klikkes, så gør det til det nuværende level
                Level.set_current_level(level)
                print(f"Moved to level {level.id}")
                return True and level.encounter_type
    return False

def generate_map(level_count=6):
    encounter_types = ["battle", "battle", "battle", "shop", "heal"] # de forskellige typer af encounters
    level_id_counter = 0 # initialiserer id tælleren til håndtering af leveler
    map_levels = [] # opretter en tom liste til at gemme leveler

    # step 1: opretter leveler og grupperer dem i en liste
    for level_number in range(level_count):
        num_levels = random.randint(2, 3) # antal forskellige grener i en gruppe
        levels_in_group = []
        for _ in range(num_levels):
            # opretter et level med et id, levelnummer og en tilfældig encounter type
            encounter_type = random.choice(encounter_types) 
            level = Level(level_id_counter, level_number, encounter_type) # opretter et level objekt
            levels_in_group.append(level) 
            level_id_counter += 1   
        map_levels.append(levels_in_group)

    boss_level = Level(level_id_counter, level_count, "boss") # opretter et boss level med et id og levelnummer
    map_levels.append([boss_level])

    # step 2: forbinder levelerne i grupperne med hinanden
    for i in range(len(map_levels) - 1):
        current_level_group = map_levels[i]
        next_level_group = map_levels[i + 1]

        for level in current_level_group:
            connections = random.sample(next_level_group, k = random.randint(1, min(2, len(next_level_group)))) # vælger et tilfældigt antal forbindelser til næste gruppe
            level.next_level.extend(connections) # tilføjer forbindelserne til levelets next_level liste

    all_levels = [level for group in map_levels for level in group] # flader listen af leveler
    fighting_levels = sum(1 for level in all_levels if level.encounter_type == "battle") # tæller antallet af battle encounters
    if fighting_levels <= 3: # hvis der er færre end 3 battle encounters, tilføj flere
        fighting_levels_needed = 3 - fighting_levels
        not_fighting_levels = [level for level in all_levels if level.encounter_type != "battle"]
        for _ in range(fighting_levels_needed):
            level_to_change = random.choice(not_fighting_levels) # vælger et tilfældigt level der ikke er en battle encounter
            level_to_change.encounter_type = "battle" # ændrer encounter type til battle
            not_fighting_levels.remove(level_to_change) # fjerner level fra listen af ikke-kamp levels

    shop_levels = sum(1 for level in all_levels if level.encounter_type == "shop") # tæller antallet af shop encounters
    if shop_levels <= 1: # hvis der er færre end 2 shop encounters, tilføj flere
        shop_levels_needed = 2 - shop_levels
        not_shop_levels = [level for level in all_levels if level.encounter_type != "shop"]
        for _ in range(shop_levels_needed):
            level_to_change = random.choice(not_shop_levels)
            level_to_change.encounter_type = "shop" # ændrer encounter type til shop
            not_shop_levels.remove(level_to_change) # fjerner level fra listen af ikke-shop levels

    if shop_levels >= 6: # hvis der er flere end 6 shop encounters, fjern nogle
        shop_levels_to_remove = shop_levels - 5
        for _ in range(shop_levels_to_remove):
            level_to_change = random.choice([level for level in all_levels if level.encounter_type == "shop"])
            level_to_change.encounter_type = "battle" # ændrer encounter type til battle
            all_levels.remove(level_to_change) # fjerner level fra listen af shop levels

    heal_levels = sum(1 for level in all_levels if level.encounter_type == "heal") # tæller antallet af heal encounters
    if heal_levels <= 1: # hvis der er færre end 2 heal encounters, tilføj flere
        heal_levels_needed = 2 - heal_levels
        not_heal_levels = [level for level in all_levels if level.encounter_type != "heal"]
        for _ in range(heal_levels_needed):
            level_to_change = random.choice(not_heal_levels)
            level_to_change.encounter_type = "heal" # ændrer encounter type til heal
            not_heal_levels.remove(level_to_change) # fjerner level fra listen af ikke-heal levels

    if heal_levels >= 6: # hvis der er flere end 6 heal encounters, fjern nogle
        heal_levels_to_remove = heal_levels - 5
        for _ in range(heal_levels_to_remove):
            level_to_change = random.choice([level for level in all_levels if level.encounter_type == "heal"])
            level_to_change.encounter_type = "battle"
            all_levels.remove(level_to_change) # fjerner level fra listen af heal levels
        

    verificer_map(map_levels)


    return map_levels # returnerer listen af leveler

def assign_level_positions(map_levels, screen_width=920, level_height=100):
    # definerer en funktion til at tildele positioner til alle leveler
    total_levels = len(map_levels)
    for level_index, level in enumerate(map_levels):
        num_levels = len(level)
        spacing = screen_width // num_levels # beregner afstanden mellem levelerne
        for i, level in enumerate(level):
            level.x = spacing * (i + 1)
            level.y = (total_levels - level_index - 1) * level_height + 50

def draw_map(map_levels, screen, font):
    # definerer en funktion til at tegne kortet
    for level_group in map_levels:
        for level in level_group:
            for next_level in level.next_level:
                pygame.draw.line(screen, (200, 200, 200), (level.x, level.y), (next_level.x, next_level.y), 2) # tegner linjer mellem levelerne
            
    for level_group in map_levels:
        for level in level_group:
            color = {
                "battle": (255, 0, 0),
                "shop": (0, 0, 255),
                "heal": (0, 255, 0),
                "boss": (255, 0, 255)
            }.get(level.encounter_type, (255, 255, 255))

            if level.is_clickable():
                pygame.draw.circle(screen, (255, 255, 0), (level.x, level.y), level.radius + 5)

            pygame.draw.circle(screen, color, (level.x, level.y), level.radius) # tegner cirkler for levelerne

            if level == Level.current_level:
                pygame.draw.circle(screen, (0, 0, 0), (level.x, level.y), level.radius + 2, 5)

            text = font.render(str(level.id), True, (0, 0, 0))
            screen.blit(text, (level.x - text.get_width() // 2, level.y - text.get_height() // 2))


generate_map()