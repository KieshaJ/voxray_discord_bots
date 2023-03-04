import discord
from datetime import datetime, timedelta
from typing import Dict, List
from .card import Card
from .deck import Deck
from .player import Player
from .pot_manager import PotManager
from utils.game_constants import GAME_OPTIONS, GameState, Option
from utils.hand_utils import get_best_possible_hand


class Game:
    options: Dict[str, Option]
    state: GameState
    players: List[Player]
    players_in_hand: List[Player]
    dealer_index: int
    first_better: int
    current_deck: Deck
    table_cards: List[Card]
    pot: PotManager
    turn_index: int
    last_raise: datetime

    def __init__(self) -> None:
        self.init_game()
        self.options = {key: value.Default for key, value in GAME_OPTIONS.items()}

    def init_game(self) -> None:
        self.state = GameState.NO_GAME
        self.players = []
        self.players_in_hand = []
        self.dealer_index = 0
        self.first_better = 0
        self.current_deck = None
        self.table_cards = []
        self.pot = PotManager()
        self.turn_index = -1
        self.last_raise = None

    def add_player(self, user: discord.User) -> bool:
        if self.is_player(user):
            return False

        self.players.append(Player(user))

        return True

    def is_player(self, user: discord.User) -> bool:
        for player in self.players:
            if player.user == user:
                return True

        return False

    def leave_hand(self, player_to_remove: Player) -> None:
        for i, player in enumerate(self.players_in_hand):
            if player == player_to_remove:
                index = i
                break
        else:
            return

        self.players_in_hand.pop(index)

        if index < self.first_better:
            self.first_better -= 1
        if self.first_better >= len(self.players_in_hand):
            self.first_better = 0
        if self.turn_index >= len(self.players_in_hand):
            self.turn_index = 0

    def get_status_between_rounds(self) -> List[str]:
        messages = []

        for player in self.players:
            messages.append(f"{player.user.name} has ${player.balance}.")

        messages.append(f"{self.dealer.user.name} is the current dealer. "
                        "Message !pkr-deal to deal when you're ready.")

        return messages

    def next_dealer(self) -> None:
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    @property
    def dealer(self) -> Player:
        return self.players[self.dealer_index]

    @property
    def current_bet(self) -> int:
        return self.pot.current_bet

    @property
    def current_player(self) -> Player:
        return self.players_in_hand[self.turn_index]

    def start(self) -> List[str]:
        self.state = GameState.NO_HANDS
        self.dealer_index = 0

        for player in self.players:
            player.balance = self.options["Buy-in"]

        self.options["Blind"] = self.options["Starting-blind"]
        return ["The game has begun!"] + self.get_status_between_rounds()

    def deal_hands(self) -> List[str]:
        self.current_deck = Deck()
        self.table_cards = []
        self.players_in_hand = []

        for player in self.players:
            player.cards = (self.current_deck.draw(), self.current_deck.draw())
            player.current_bet = 0
            player.placed_bet = False
            self.players_in_hand.append(player)

        self.state = GameState.HANDS_DEALT
        messages = ["The hands have been dealt!"]

        self.pot.new_hand(self.players)

        if self.options["Blind"] > 0:
            messages += self.pay_blinds()

        self.turn_index -= 1

        return messages + self.next_turn()

    def pay_blinds(self) -> List[str]:
        messages: List[str] = []

        raise_delay = self.options["Raise-delay"]
        if raise_delay == 0:
            self.last_raise = None
        elif self.last_raise is None:
            self.last_raise = datetime.now()
        elif datetime.now() - self.last_raise > timedelta(minutes=raise_delay):
            messages.append("**Blinds are being doubled this round!**")
            self.options["Blind"] *= 2
            self.last_raise = datetime.now()

        blind = self.options["Blind"]

        if len(self.players) > 2:
            small_player = self.players[(self.dealer_index + 1) % len(self.players_in_hand)]
            big_player = self.players[(self.dealer_index + 2) % len(self.players_in_hand)]
            self.turn_index = (self.dealer_index + 3) % len(self.players_in_hand)
            self.first_better = (self.dealer_index + 1) % len(self.players)
        else:
            small_player = self.players[self.dealer_index]
            big_player = self.players[self.dealer_index - 1]
            self.turn_index = self.dealer_index
            self.first_better = self.dealer_index - 1

        messages.append(f"{small_player.name} has paid the small blind "
                        f"of ${blind}.")

        if self.pot.pay_blind(small_player, blind):
            messages.append(f"{small_player.name} is all in!")
            self.leave_hand(small_player)

        messages.append(f"{big_player.name} has paid the big blind "
                        f"of ${blind * 2}.")
        if self.pot.pay_blind(big_player, blind * 2):
            messages.append(f"{big_player.name} is all in!")
            self.leave_hand(big_player)

        return messages

    def get_current_options(self) -> List[str]:
        messages = [f"It is {self.current_player.name}'s turn. "
                    f"{self.current_player.user.name} currently has "
                    f"${self.current_player.balance}. "
                    f"The pot is currently ${self.pot.value}."]

        if self.pot.current_bet > 0:
            messages.append(f"The current bet to meet is ${self.current_bet}, "
                            f"and {self.current_player.name} has bet "
                            f"${self.current_player.current_bet}.")
        else:
            messages.append(f"The current bet to meet is ${self.current_bet}.")
        if self.current_player.current_bet == self.current_bet:
            messages.append("Message !pkr-check, !pkr-raise or !pkr-fold.")
        elif self.current_player.max_bet > self.current_bet:
            messages.append("Message !pkr-call, !pkr-raise or !pkr-fold.")
        else:
            messages.append("Message !pkr-all-in or !pkr-fold.")

        return messages

    def next_round(self) -> List[str]:
        messages: List[str] = []

        if self.state == GameState.HANDS_DEALT:
            messages.append("Dealing the flop:")
            self.table_cards.append(self.current_deck.draw())
            self.table_cards.append(self.current_deck.draw())
            self.table_cards.append(self.current_deck.draw())
            self.state = GameState.FLOP_DEALT
        elif self.state == GameState.FLOP_DEALT:
            messages.append("Dealing the turn:")
            self.table_cards.append(self.current_deck.draw())
            self.state = GameState.TURN_DEALT
        elif self.state == GameState.TURN_DEALT:
            messages.append("Dealing the river:")
            self.table_cards.append(self.current_deck.draw())
            self.state = GameState.RIVER_DEALT
        elif self.state == GameState.RIVER_DEALT:
            return self.showdown()

        messages.append("  ".join(str(card) for card in self.table_cards))
        self.pot.next_round()
        self.turn_index = self.first_better

        return messages + self.get_current_options()

    def next_turn(self) -> List[str]:
        if self.pot.round_over():
            if self.pot.betting_over():
                return self.showdown()
            else:
                return self.next_round()
        else:
            self.turn_index = (self.turn_index + 1) % len(self.players_in_hand)
            return self.get_current_options()

    def showdown(self) -> List[str]:
        while len(self.table_cards) < 5:
            self.table_cards.append(self.current_deck.draw())

        messages = ["We have reached the end of betting. "
                    "All cards will be revealed."]

        messages.append("  ".join(str(card) for card in self.table_cards))

        for player in self.pot.players_in_pot():
            messages.append(f"{player.name}'s hand: "
                            f"{player.cards[0]}  {player.cards[1]}")

        winners = self.pot.get_winners(self.table_cards)
        
        for winner, winnings in sorted(winners.items(), key=lambda item: item[1]):
            hand_name = str(get_best_possible_hand(self.table_cards, winner.cards))
            messages.append(f"{winner.name} wins ${winnings} with a {hand_name}.")
            winner.balance += winnings

        i = 0

        while i < len(self.players):
            player = self.players[i]
            if player.balance > 0:
                i += 1
            else:
                messages.append(f"{player.name} has been knocked out of the game!")
                self.players.pop(i)
                if len(self.players) == 1:
                    messages.append(f"{self.players[0].user.name} wins the game! "
                                    "Congratulations!")
                    self.state = GameState.NO_GAME
                    return messages
                if i <= self.dealer_index:
                    self.dealer_index -= 1

        self.state = GameState.NO_HANDS
        self.next_dealer()
        messages += self.get_status_between_rounds()

        return messages

    def check(self) -> List[str]:
        self.current_player.placed_bet = True
        return [f"{self.current_player.name} checks."] + self.next_turn()

    def raise_bet(self, amount: int) -> List[str]:
        self.pot.handle_raise(self.current_player, amount)
        messages = [f"{self.current_player.name} raises by ${amount}."]

        if self.current_player.balance == 0:
            messages.append(f"{self.current_player.name} is all in!")
            self.leave_hand(self.current_player)
            self.turn_index -= 1

        return messages + self.next_turn()

    def call(self) -> List[str]:
        self.pot.handle_call(self.current_player)
        messages = [f"{self.current_player.name} calls."]

        if self.current_player.balance == 0:
            messages.append(f"{self.current_player.name} is all in!")
            self.leave_hand(self.current_player)
            self.turn_index -= 1

        return messages + self.next_turn()

    def all_in(self) -> List[str]:
        if self.pot.current_bet > self.current_player.max_bet:
            return self.call()
        else:
            return self.raise_bet(self.current_player.max_bet - self.current_bet)

    def fold(self) -> List[str]:
        messages = [f"{self.current_player.name} has folded."]
        self.pot.handle_fold(self.current_player)
        self.leave_hand(self.current_player)

        if len(self.pot.players()) == 1:
            winner = list(self.pot.players())[0]
            messages += [f"{winner.name} wins ${self.pot.value}!"]
            winner.balance += self.pot.value
            self.state = GameState.NO_HANDS
            self.next_dealer()
            return messages + self.get_status_between_rounds()

        if not self.pot.betting_over():
            self.turn_index -= 1
            return messages + self.next_turn()

        return self.showdown()

    async def tell_hands(self, client: discord.Client) -> None:
        for player in self.players:
            embed = discord.Embed(
                description=str(player.cards[0]) + " " + str(player.cards[1]),
                color=0x00ff00
            )

            await player.user.send(embed=embed)

