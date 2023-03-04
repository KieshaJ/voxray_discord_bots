from collections import namedtuple
from enum import Enum
from typing import Dict


Option = namedtuple("Option", ["Description", "Default"])

GAME_OPTIONS: Dict[str, Option] = {
    "Blind": Option("The current price of the small blind", 5),
    "Buy-in": Option("The amount of chips all players start out with", 500),
    "Raise-delay": Option("The number of minutes before blinds double", 30),
    "Starting-blind": Option("The starting price of the small blind", 5)
}

class GameState(Enum):
    NO_GAME = 1
    WAITING = 2
    NO_HANDS = 3
    HANDS_DEALT = 4
    FLOP_DEALT = 5
    TURN_DEALT = 6
    RIVER_DEALT = 7

