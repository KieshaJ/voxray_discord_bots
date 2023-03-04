from functools import total_ordering

from utils.poker_constants import RANKS


@total_ordering
class Card:
    suit: str
    rank: str

    def __init__(self, suit: str, rank: str) -> None:
        self.suit = suit
        self.rank = rank

    def __lt__(self, other) -> bool:
        return RANKS[self.rank].Value < RANKS[other.rank].Value

    def __eq__(self, other) -> bool:
        return self.rank == other.rank

    def __str__(self) -> str:
        return self.suit + self.rank

    @property
    def name(self):
        return RANKS[self.rank].Name

    @property
    def plural(self):
        return RANKS[self.rank].Plural