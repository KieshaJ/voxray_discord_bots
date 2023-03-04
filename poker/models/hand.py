from functools import total_ordering
from typing import List

from .card import Card
from utils.poker_constants import RANKS, Rank
from utils.ranking_constants import Ranking


@total_ordering
class Hand:
    cards: List[Card]
    duplicates: List[Card]

    def __init__(self, cards: List[Card]) -> None:
        self.cards = sorted(cards)
        
        duplicates = self.get_duplicates()

        if self.is_flush():
            if self.is_straight():
                self.rank = Ranking.STRAIGHT_FLUSH
            else:
                self.rank = Ranking.FLUSH
        elif self.is_straight():
            self.rank = Ranking.STRAIGHT
        elif duplicates:
            if len(duplicates) == 2:
                if len(duplicates[1]) == 3:
                    self.rank = Ranking.FULL_HOUSE
                else:
                    self.rank = Ranking.TWO_PAIR
            else:
                if len(duplicates[0]) == 4:
                    self.rank = Ranking.FOUR_OF_KIND
                elif len(duplicates[0]) == 3:
                    self.rank = Ranking.THREE_OF_KIND
                else:
                    self.rank = Ranking.PAIR
            self.rearrange_duplicates(duplicates)
        else:
            self.rank = Ranking.HIGH_CARD

    def __lt__(self, other):
        if self.rank < other.rank:
            return True
        if self.rank > other.rank:
            return False
        for self_card, other_card in zip(self.cards[::-1], other.cards[::-1]):
            if self_card < other_card:
                return True
            elif self_card > other_card:
                return False
        return False

    def __eq__(self, other):
        if self.rank != other.rank:
            return False
        for self_card, other_card in zip(self.cards, other.cards):
            if self_card != other_card:
                return False
        return True

    def __str__(self):
        if self.rank == Ranking.HIGH_CARD:
            return self.cards[4].name + " High"
        elif self.rank == Ranking.PAIR:
            return "Pair of " + self.cards[4].plural
        elif self.rank == Ranking.TWO_PAIR:
            return "Two pair, " + self.cards[4].plural + " and " + self.cards[2].plural
        elif self.rank == Ranking.THREE_OF_KIND:
            return "Three of a kind, " + self.cards[4].plural
        elif self.rank == Ranking.STRAIGHT:
            return self.cards[4].name + "-high Straight"
        elif self.rank == Ranking.FLUSH:
            return self.cards[4].name + "-high Flush"
        elif self.rank == Ranking.FULL_HOUSE:
            return "Full house, " + self.cards[4].plural + " over " + self.cards[1].plural
        elif self.rank == Ranking.FOUR_OF_KIND:
            return "Four of a kind, " + self.cards[4].plural
        elif self.rank == Ranking.STRAIGHT_FLUSH:
            if self.cards[4].rank == 'A':
                return "Royal Flush"
            else:
                return self.cards[4].name + "-high Straight Flush"

    def rearrange_duplicates(self, duplicates: List[List[Card]]) -> None:
        flat_duplicates = [card for cards in duplicates for card in cards]
        for duplicate in flat_duplicates:
            self.cards.pop(self.cards.index(duplicate))
        self.cards += flat_duplicates

    def is_straight(self) -> bool:
        ranks = [RANKS[card.rank].Value for card in self.cards]
        
        for i in range(1, 5):
            if ranks[i - 1] != ranks[i] - 1:
                break
        else:
            return True
        if ranks == [0, 1, 2, 3, 12]:
            self.cards = [self.cards[-1]] + self.cards[:-1]
            return True

        return False

    def is_flush(self) -> bool:
        suit = self.cards[0].suit

        for card in self.cards[1:]:
            if card.suit != suit:
                return False

        return True

    def get_duplicates(self) -> List[List[Card]]:
        duplicates: List[List[Card]] = []
        current_duplicates: List[Card] = [self.cards[0]]

        for card in self.cards[1:]:
            if current_duplicates[0] != card:
                if len(current_duplicates) > 1:
                    duplicates.append(current_duplicates)
                current_duplicates = [card]
            else:
                current_duplicates.append(card)

        if len(current_duplicates) > 1:
            duplicates.append(current_duplicates)

        if len(duplicates) == 2 and len(duplicates[0]) > len(duplicates[1]):
            duplicates[0], duplicates[1] = duplicates[1], duplicates[0]

        return duplicates

