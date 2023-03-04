from itertools import combinations
from typing import List, Tuple

from models.card import Card
from models.hand import Hand


def get_best_possible_hand(table_cards: List[Card], player_cards: Tuple[Card, Card]) -> Hand:
    return max(Hand(list(hand)) for hand in combinations(tuple(table_cards) + player_cards, 5))