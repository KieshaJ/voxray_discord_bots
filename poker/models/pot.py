from typing import List, Set
from .player import Player
from .card import Card
from .hand import Hand
from utils.hand_utils import get_best_possible_hand


class Pot:
    players: Set[Player]
    current_bet: int
    max_bet: int
    total: int

    def __init__(self, players: Set[Player]) -> None:
        self.players = players
        self.current_bet = 0
        self.total = 0

        if len(players) > 0:
            self.max_bet = min(player.max_bet for player in players)
        else:
            self.max_bet = 10000000000000000000000000000

    def get_winners(self, table_cards: List[Card]) -> List[Player]:
        winners: List[Player] = []
        best_hand: Hand = None

        for player in self.players:
            hand = get_best_possible_hand(table_cards, player.cards)
            if best_hand is None or hand > best_hand:
                winners = [player]
                best_hand = hand
            elif hand == best_hand:
                winners.append(player)

        return winners

    def create_side_pot(self):
        excluded_player = {player for player in self.players if player.max_bet == self.max_bet}
        return Pot(self.players - excluded_player)

