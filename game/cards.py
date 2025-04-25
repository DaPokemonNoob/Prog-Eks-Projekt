import pygame
import random
import sys
from typing import List, Tuple

Card = Tuple[str, str]


class Deck:
    def __init__(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards: List[Card] = [(rank, suit) for suit in suits for rank in ranks]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self) -> Card:
        if not self.cards:
            raise IndexError("Cannot draw from an empty deck")
        return self.cards.pop(0)
    
    def __len__(self) -> int:
        return len(self.cards)