from collections import namedtuple


SUITS = ('♠', '♥', '♦', '♣')

Rank = namedtuple("Rank", ["Name", "Plural", "Value"])

RANKS = {
    "2": Rank("Deuce", "Deuces", 0),
    "3": Rank("Three", "Threes", 1),
    "4": Rank("Four", "Fours", 2),
    "5": Rank("Five", "Fives", 3),
    "6": Rank("Six", "Sixes", 4),
    "7": Rank("Seven", "Sevens", 5),
    "8": Rank("Eight", "Eights", 6),
    "9": Rank("Nine", "Nines", 7),
    "10": Rank("Ten", "Tens", 8),
    "J": Rank("Jack", "Jacks", 9),
    "Q": Rank("Queen", "Queens", 10),
    "K": Rank("King", "Kings", 11),
    "A": Rank("Ace", "Aces", 12)
}