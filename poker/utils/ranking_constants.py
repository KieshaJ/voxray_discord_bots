from enum import Enum
from functools import total_ordering


@total_ordering
class Ranking(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9

    def __lt__(self, other) -> bool:
        return self.value < other.value

