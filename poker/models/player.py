from typing import Tuple
import discord
from .card import Card

class Player:
    balance: int
    user: discord.User
    cards: Tuple[Card, Card]
    current_bet: int
    placed_bet: bool

    def __init__(self, user: discord.User) -> None:
        self.balance = 0
        self.user = user
        self.cards = None
        self.current_bet = 0
        self.placed_bet = False

    @property
    def name(self) -> str:
        return self.user.name

    @property
    def max_bet(self) -> str:
        return self.current_bet + self.balance

    def bet(self, new_amount: int) -> int:
        money_lost = (new_amount - self.current_bet)
        self.balance -= money_lost
        self.current_bet = new_amount
        return money_lost

    def pay_blind(self, blind_amount: int) -> int:
        self.current_bet = min(self.balance, blind_amount)
        self.balance -= self.current_bet
        return self.current_bet

