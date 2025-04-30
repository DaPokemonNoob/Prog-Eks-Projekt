import random

class Level:
    def __init__(self, id, level_number, encounter_type=None):
        self.id = id
        self.level_number = level_number
        self.encounter_type = encounter_type
        self.next_level = []

def generate_map(level_count=6):
    encounter_types = ["battle", "treasure", "shop", "heal"]
    level_id_counter = 0
    map_levels = []

    for level_number in range(level_count):
        num_levels = random.randint(2, 4) # antal forskellige grener i en gruppe
        levels_in_group = []
        for _ in range(num_levels):
            encounter_type = random.choice(encounter_types)
            level = Level(level_id_counter, level_number, encounter_type)
            levels_in_group.append(level)
            level_id_counter += 1   
        map_levels.append(levels_in_group)

    boss_level = Level(level_id_counter, level_count, "boss")
    map_levels.append([boss_level])

    for i in range(len(map_levels) - 1):
        current_level_group = map_levels[i]
        next_level_group = map_levels[i + 1]

        for level in current_level_group:
            connections = random.sample(next_level_group, k = random.randint(1, min(2, len(next_level_group))))
            level.next_level.extend(connections)

    for i, level_group in enumerate(map_levels):
        print(f"\nLevel {i}:")
        for level in level_group:
            next_level_ids = [next_level.id for next_level in level.next_level]
            print(f"{level.id} ({level.encounter_type}) -> connects to: {next_level_ids}")

generate_map()