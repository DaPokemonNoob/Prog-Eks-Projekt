import random
import pygame

class Level: 
    # definerer en klasse til at repræsentere et level i spillet

    current_level = None # definerer en klassevariabel til at holde styr på det nuværende level

    def __init__(self, id, level_number, encounter_type=None):
        # parametre til at initialisere et level
        # id: unikt id for levelet
        # level_number: nummeret på levelet i kortet
        # encounter_type: typen af encounter (battle, shop, heal, treasure, boss)

        self.id = id
        self.level_number = level_number
        self.encounter_type = encounter_type
        self.next_level = []
        self.radius = 20

    def is_clickable(self):
        # definerer en funktion til at håndtere klik på leveler
        mouse_x, mouse_y = pygame.mouse.get_pos() # henter musens position
        distance = ((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2) ** 0.5 # beregner afstanden mellem musen og levelet med Pythagoras sætning
        # tjekker om musen er inden for radius af levelet

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
    # definerer en funktion til at verificere kortet - sikre at alle leveler er tilgængelige
    start_levels = map_levels[0]
    tilgængelige_levels = set(start_levels) # opretter et sæt af tilgængelige leveler

    def find_næste_level(level): # definerer en indre funktion til at finde næste level
        if level.id not in tilgængelige_levels:
            tilgængelige_levels.add(level.id)
            for next_level in level.next_level:
                find_næste_level(next_level) # kalder dfs funktionen for at finde næste level - distributed file system

    for level in start_levels:
        find_næste_level(level)

    alle_levels = {level.id: level for group in map_levels for level in group} # opretter et dictionary af alle leveler

    utilgængelig = set(alle_levels.keys()) - tilgængelige_levels # finder de utilgængelige leveler

    # sørger for at forbinde de utilgængelige leveler med de tilgængelige leveler
    if utilgængelig:
        for level_id in utilgængelig:
            utilgængelig_level = alle_levels[level_id]
            level_gruppe = utilgængelig_level.level_number

            if level_gruppe > 0:
                tidligere_gruppe = map_levels[level_gruppe - 1]
                random_tidligere_level = random.choice(tidligere_gruppe) # vælger et tilfældigt level fra den tidligere gruppe
                random_tidligere_level.next_level.append(utilgængelig_level) # tilføjer det utilgængelige level til den tidligere gruppe
        
def handle_click(mouse_pos, map_levels):
    # definerer en funktion til at håndtere klik på kortet
    for level_group in map_levels:
        for level in level_group:
            if level.is_clickable():
                Level.set_current_level(level) # levelet kunne klikkes, så gør det til det nuværende level
                print(f"Moved to level {level.id}")
                return True and ("battle" if level.encounter_type == "boss" else level.encounter_type) # returner encounter type til at skifte skærm
    return False

def generate_map(level_count=6):
    # definerer en funktion til at generere kortet
    # step 1: generere leveler og grupper
    level_id_counter = 0
    
    # lav første gruppe af leveler
    first_group = []
    num_first_levels = random.randint(2, 3)
    
    # lav et level med encounter type "battle" i første gruppe
    # det første level i første gruppe er altid en battle encounter
    battle_level = Level(level_id_counter, 0, "battle")
    level_id_counter += 1
    first_group.append(battle_level)
    
    # tilføj flere forskellige leveler til første gruppe
    for _ in range(num_first_levels - 1):
        encounter_type = random.choice(["battle", "shop", "heal", "treasure"]) # vælger en tilfældig encounter type
        level = Level(level_id_counter, 0, encounter_type)                     # opretter et level med encounter type
        first_group.append(level)                                              # tilføjer levelet til første gruppe
        level_id_counter += 1                                                  # opdaterer id counter
    
    map_levels = [first_group]
    
    # alle forskellige encounter typer, flere battle encounters for højere chance
    encounter_types = ["battle", "battle", "battle", "shop", "heal", "treasure"]

    # lav de resterende grupper af leveler
    for level_number in range(1, level_count): # starter fra 1 da 0 allerede er brugt, og slutter før level_count
        num_levels = random.randint(2, 3) # vælger et tilfældigt antal leveler i gruppen
        levels_in_group = []

        for _ in range(num_levels):
            encounter_type = random.choice(encounter_types)
            level = Level(level_id_counter, level_number, encounter_type)
            levels_in_group.append(level)
            level_id_counter += 1
        map_levels.append(levels_in_group)

    # laver et boss level i den sidste gruppe
    boss_level = Level(level_id_counter, level_count, "boss")
    map_levels.append([boss_level])

    # step 2: forbinder levelerne i grupperne med hinanden
    for i in range(len(map_levels) - 1): # går igennem alle grupper undtagen den sidste
        current_level_group = map_levels[i] # vælger den nuværende gruppe
        next_level_group = map_levels[i + 1] # vælger den næste gruppe

        for level in current_level_group:
            connections = random.sample(next_level_group, k = random.randint(1, min(2, len(next_level_group)))) # vælger et tilfældigt antal forbindelser til næste gruppe, k = antallet af connections
            level.next_level.extend(connections) # tilføjer forbindelserne til levelets next_level liste

    # step 3: tilføj flere typer af encounters hvis nødvendigt
    all_levels = [level for group in map_levels for level in group] # flader listen af leveler fra en liste af lister til en enkelt liste
    fighting_levels = sum(1 for level in all_levels if level.encounter_type == "battle") # tæller antallet af battle encounters

    if fighting_levels <= 3: # hvis der er færre end 3 battle encounters, tilføj flere
        fighting_levels_needed = 3 - fighting_levels
        not_fighting_levels = [level for level in all_levels if level.encounter_type != "battle"]

        for _ in range(fighting_levels_needed):
            level_to_change = random.choice(not_fighting_levels) # vælger et tilfældigt level der ikke er en battle encounter
            level_to_change.encounter_type = "battle" # ændrer encounter type til battle
            not_fighting_levels.remove(level_to_change) # fjerner level fra listen af ikke-kamp levels

    shop_levels = sum(1 for level in all_levels if level.encounter_type == "shop") # ligesom før, tæller antallet af shop encounters
    if shop_levels <= 1: 
        shop_levels_needed = 2 - shop_levels
        not_shop_levels = [level for level in all_levels if level.encounter_type != "shop"]

        for _ in range(shop_levels_needed):
            level_to_change = random.choice(not_shop_levels)
            level_to_change.encounter_type = "shop" 
            not_shop_levels.remove(level_to_change) 

    if shop_levels >= 6: # hvis der er flere end 6 shop encounters, fjern nogle
        shop_levels_to_remove = shop_levels - 5

        for _ in range(shop_levels_to_remove):
            level_to_change = random.choice([level for level in all_levels if level.encounter_type == "shop"])
            level_to_change.encounter_type = "battle" # ændrer encounter type til battle
            all_levels.remove(level_to_change) 

    heal_levels = sum(1 for level in all_levels if level.encounter_type == "heal") 
    if heal_levels <= 1: 
        heal_levels_needed = 2 - heal_levels
        not_heal_levels = [level for level in all_levels if level.encounter_type != "heal"]

        for _ in range(heal_levels_needed):
            level_to_change = random.choice(not_heal_levels)
            level_to_change.encounter_type = "heal" 
            not_heal_levels.remove(level_to_change) 

    if heal_levels >= 6: 
        heal_levels_to_remove = heal_levels - 5

        for _ in range(heal_levels_to_remove):
            level_to_change = random.choice([level for level in all_levels if level.encounter_type == "heal"])
            level_to_change.encounter_type = "battle"
            all_levels.remove(level_to_change) 
        
    verificer_map(map_levels)

    return map_levels # returnerer listen af leveler

def assign_level_positions(map_levels, screen_width=920, level_height=100):
    # definerer en funktion til at tildele positioner til alle leveler
    total_levels = len(map_levels)
    for level_index, level in enumerate(map_levels):                       # går igennem alle leveler (enumerate giver både index og level, eks. (0, level1))
        num_levels = len(level)
        spacing = screen_width // num_levels                               # beregner afstanden mellem levelerne

        for i, level in enumerate(level):
            level.x = spacing * (i + 1)                                    # beregner x-positionen baseret på indexet
            level.y = (total_levels - level_index - 1) * level_height + 50 # beregner y-positionen baseret på niveauet i kortet

def draw_map(map_levels, screen, font):
    # definerer en funktion til at tegne mappet
    for level_group in map_levels:              # går igennem grupperne af leveler
        for level in level_group:               # går igennem alle leveler i gruppen
            for next_level in level.next_level: # går igennem alle næste leveler i gruppen
                pygame.draw.line(screen, (200, 200, 200), (level.x, level.y), (next_level.x, next_level.y), 2) # tegner linjer mellem levelerne
            
    for level_group in map_levels:
        for level in level_group:
            # definerer farven baseret på encounter type
            # battle = rød, shop = blå, heal = grøn, treasure = gul, boss = lilla
            color = {
                "battle": (255, 0, 0),
                "shop": (0, 0, 255),
                "heal": (0, 255, 0),
                "treasure": (255, 255, 0),
                "boss": (255, 0, 255)
            }.get(level.encounter_type, (255, 255, 255))

            if level.is_clickable():
                pygame.draw.circle(screen, (255, 165, 0), (level.x, level.y), level.radius + 5) # hvis levelet kan klikkes, tegner en orange cirkel omkring det

            pygame.draw.circle(screen, color, (level.x, level.y), level.radius)                 # tegner cirkler for levelerne

            if level == Level.current_level:
                pygame.draw.circle(screen, (0, 0, 0), (level.x, level.y), level.radius + 2, 5)  # laver en sort cirkel omkring det nuværende level

            text = font.render(str(level.id), True, (0, 0, 0))                                  # tegner teksten inde i cirklen - level id
            screen.blit(text, (level.x - text.get_width() // 2, level.y - text.get_height() // 2))

generate_map()