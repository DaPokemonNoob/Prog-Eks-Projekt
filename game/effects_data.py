def armor(amount):                  # Armor effekt - kan tage x skade før minionen mister hp
    return amount

def taunt():                        # Taunt effekt - enemy minions kan kun angribe minionen med taunt
    return True

def increase(attack, current_hp):   # increase effekt - giver en minion +x i attack og +x i hp
    return attack, current_hp