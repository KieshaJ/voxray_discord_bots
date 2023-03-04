import random
from typing import Set

from .card import Card
from utils.poker_constants import RANKS, SUITS


class Deck:
    cards: Set[Card]

    def __init__(self) -> None:
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

