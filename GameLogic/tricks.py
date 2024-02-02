from typing import Iterable
from GameLogic.cards import Card, Hand
from GameLogic.players import PinochlePlayer


class Trick:

    def __init__(self, n_players: int, trump: str):
        self.n_players = n_players
        self.trump = trump
        self.cards = []
        self.card_players = []
        self.card_to_beat = None

    @property
    def leading_card(self):
        return self.cards[0] if len(self.cards) else None

    @property
    def leading_suit(self):
        return self.leading_card.suit if len(self.cards) else None

    @property
    def trump_played(self):
        return self.card_to_beat.suit is self.trump

    @property
    def complete(self):
        return len(self) == self.n_players

    def add_card(self, card: Card, player: PinochlePlayer):
        self.cards.append(card)
        self.card_players.append(player)

        if not self.card_to_beat:
            self.card_to_beat = card
        elif card.suit is self.trump:
            if self.card_to_beat.suit is not self.trump or card > self.card_to_beat:
                self.card_to_beat = card
        elif card.suit is self.card_to_beat.suit and card > self.card_to_beat:
            self.card_to_beat = card

    def can_beat_winning_card(self, cards: Iterable[Card]):
        """This method assumes that 'cards' is already in the appropriate suit"""
        if self.card_to_beat is None:
            return cards
        else:
            return [card for card in cards if card > self.card_to_beat]

    def legal_plays(self, hand: Hand):

        # If this is the first card played, any card is legal
        if len(self.cards) == 0:
            return hand.cards

        # Player must follow suit
        elif hand.has_suit(self.leading_suit):
            if self.trump_played and self.trump != self.leading_suit:
                return hand[self.leading_suit]
            else:
                return self.can_beat_winning_card(hand[self.leading_suit]) or hand[self.leading_suit]

        # Player must trump if they cannot follow suit
        elif hand.has_suit(self.trump):
            if self.trump_played:
                return self.can_beat_winning_card(hand[self.trump]) or hand[self.trump]
            else:
                return hand[self.trump]

        # Player cannot trump or follow suit
        else:
            return hand.cards

    def winner(self):
        for card, player in zip(self.cards, self.card_players):
            if card == self.card_to_beat:
                return player

    def counters(self) -> int:
        return len([card for card in self.cards if card.is_counter])

    def have_played(self):
        return self.card_players

    def get_state(self):
        return {
            'n_players': self.n_players,
            'trump': self.trump,
            'cards': [c.get_state() for c in self.cards],
            'card_to_beat': self.card_to_beat.get_state(),
            'trump_played': self.trump_played,
            'card_players': [p.id for p in self.card_players],
            'winner': self.winner().id,
            'complete': self.complete,
        }

    def __str__(self):
        return ' | '.join([str(card) for card in self.cards])

    def __bool__(self):
        return len(self.cards) > 0

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)
