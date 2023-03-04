from typing import Dict, List, Set
from .card import Card
from .player import Player
from .pot import Pot


class PotManager:
    pots: List[Pot]

    def __init__(self) -> None:
        self.pots = []

    def new_hand(self, players: List[Player]) -> None:
        self.pots = [Pot(set(players))]

    @property
    def current_bet(self) -> int:
        return sum(pot.current_bet for pot in self.pots)

    @property
    def value(self) -> int:
        return sum(pot.total for pot in self.pots)

    def increase_bet(self, new_amount: int) -> None:
        accumulated_bet = 0

        while self.pots[-1].max_bet < new_amount:
            self.pots[-1].current_bet = self.pots[-1].max_bet - accumulated_bet
            accumulated_bet += self.pots[-1].current_bet
            self.pots.append(self.pots[-1].create_side_pot())

        new_bet = min(self.pots[-1].max_bet, new_amount)
        self.pots[-1].current_bet = new_bet - accumulated_bet

    def players_in_pot(self) -> Set[Player]:
        return self.pots[0].players

    def debug_print(self):
        for i, pot in enumerate(self.pots):
            print(f"Pot #{i}. Bet: ${pot.current_bet} (Max: {pot.max_bet}). "
                  f"Amount: ${pot.total}.")
            for player in pot.players:
                print(f"{player.name}: {player.balance}")
            print("-----")

    def handle_fold(self, player: Player) -> None:
        for pot in self.pots:
            if player in pot.players:
                pot.players.remove(player)

    def handle_call(self, player: Player) -> None:
        new_amount = player.bet(min(player.max_bet, self.current_bet))
        old_bet = player.current_bet - new_amount
        pot_index = 0

        while new_amount > 0:
            current_pot = self.pots[pot_index]
            old_bet -= current_pot.current_bet

            if old_bet < 0:
                current_pot.total -= old_bet
                new_amount += old_bet
                old_bet = 0

            pot_index += 1

        player.placed_bet = True

    def handle_raise(self, player: Player, new_amount: int) -> None:
        self.increase_bet(self.current_bet + new_amount)
        self.handle_call(player)

    def pay_blind(self, player: Player, blind: int) -> bool:
        self.increase_bet(blind)
        self.handle_call(player)
        player.placed_bet = False
        return player.balance == 0

    def round_over(self) -> bool:
        if self.betting_over():
            return True

        for player in self.pots[0].players:
            if player.balance == 0:
                continue
            elif not player.placed_bet or player.current_bet < self.current_bet:
                return False

        return True

    def betting_over(self) -> bool:
        players_left_betting = False

        for player in self.pots[0].players:
            if player.balance > 0:
                if players_left_betting or not player.placed_bet:
                    return False
                if player.current_bet < self.current_bet:
                    return False
                players_left_betting = True

        return True

    def get_winners(self, table_cards: List[Card]) -> Dict[Player, int]:
        winners: Dict[Player, int] = {}

        for pot in self.pots:
            pot_winners = pot.get_winners(table_cards)

            if len(pot_winners) == 0:
                continue

            pot_won = pot.total // len(pot_winners)

            if pot_won > 0:
                for winner in pot_winners:
                    winners.setdefault(winner, 0)
                    winners[winner] += pot_won

        return winners

    def next_round(self) -> None:
        for pot in self.pots:
            pot.current_bet = 0
            pot.max_bet = 0

        for player in self.pots[-1].players:
            player.placed_bet = False
            player.current_bet = 0

        self.pots[-1].max_bet = min(player.max_bet for player in self.pots[-1].players)

