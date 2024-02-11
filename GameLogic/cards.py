from typing import Iterable, List
import copy
import numpy as np
from itertools import product
from termcolor import colored

import os
os.system('color')


class Card:

    values = ['9', '10', 'J', 'Q', 'K', 'A']
    counter_values = {'K', '10', 'A'}
    suits = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    suit_symbols = {'Spades': '♠', 'Hearts': '♥', 'Clubs': '♣', 'Diamonds': '♦'}

    red = 'red'
    not_red = 'cyan'  # Can be one of ['blue', 'cyan', 'grey', 'green', 'white', 'yellow', 'magenta']
    suit_colors = {'Spades': not_red, 'Hearts': red, 'Clubs': not_red, 'Diamonds': red}

    def __init__(self, suit, value):
        assert suit in Card.suits, 'Invalid suit "{}" for Card'.format(suit)
        assert value in Card.values, 'Invalid value "{}" for Card'.format(value)
        self.suit = suit
        self.value = value

    @property
    def is_counter(self):
        return self.value in self.counter_values

    @staticmethod
    def one_of_each():
        return [Card(suit, value) for suit, value in product(Card.suits, Card.values)]

    @staticmethod
    def set_not_red_color(color):
        Card.not_red = color
        Card.suit_colors = {'Spades': Card.not_red, 'Hearts': Card.red, 'Clubs': Card.not_red, 'Diamonds': Card.red}

    @staticmethod
    def random_suit():
        return np.random.choice(Card.suits)

    @staticmethod
    def random_value():
        return np.random.choice(Card.values)

    @staticmethod
    def random():
        return Card(Card.random_suit(), Card.random_value())

    def get_state(self):
        return {'suit': self.suit, 'value': self.value}

    def to_str(self, color=False, symbol=False):
        if symbol:
            card_str = '{}{}'.format(self.value, Card.suit_symbols[self.suit])
        else:
            card_str = '{} of {}'.format(self.value, self.suit)

        return colored(card_str, Card.suit_colors[self.suit]) if color else card_str

    def copy(self):
        return Card(self.suit, self.value)

    def __str__(self):
        return self.to_str(color=True, symbol=True)

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.suit}", "{self.value}")'

    def __lt__(self, other):
        return Card.values.index(self.value) < Card.values.index(other.value)

    def __gt__(self, other):
        return Card.values.index(self.value) > Card.values.index(other.value)

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash(self.suit + self.value)


class PartialDeck:

    def __init__(self, cards):
        self.cards = cards

    def add_card(self, card: Card):
        self.cards.append(card)

    def add_cards(self, cards: Iterable[Card]):
        self.cards.extend(list(cards))

    def discard(self, card: Card):
        self.cards.remove(card)

    def discard_many(self, cards: Iterable[Card]):
        for card in cards:
            self.discard(card)

    def shuffle(self):
        np.random.shuffle(self.cards)

    def has_suit(self, suit):
        for card in self.cards:
            if card.suit == suit:
                return True
        return False

    def has_card(self, card):
        for this_card in self.cards:
            if this_card.suit == card.suit and this_card.value == card.value:
                return True
        return False

    def choose_random_card(self):
        if len(self.cards) == 0:
            raise AttributeError('Cannot choose a random card, no cards in the deck')
        return np.random.choice(self.cards)

    def to_str(self, color=False, symbol=False):
        return ', '.join([card.to_str(color, symbol) for card in self.cards])

    def get_state(self):
        return {
            'deck_type': self.__class__.__name__,
            'cards': [card.get_state() for card in self.cards],
        }

    def __str__(self):
        return self.to_str(color=True, symbol=True)

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, key):
        return self.cards[key]

    def __contains__(self, item):
        return item in self.cards


class Deck(PartialDeck):

    values = Card.values

    def __init__(self):
        super().__init__(self.build_deck())

    def get_state(self):
        return {
            **super().get_state(),
            'values': self.values,
        }

    def build_deck(self):
        return [Card(s, v) for s, v in product(Card.suits, Card.values)]

    def deal(self):
        pass


class PinochleDeck(Deck):

    n_players = 4
    values = ['9', 'J', 'Q', 'K', '10', 'A']
    card_instances = 2
    cards_per_hand = 12

    def __init__(self):
        Card.values = self.values
        super().__init__()

    def get_state(self):
        return {
            **super().get_state(),
            'n_players': self.n_players,
        }

    def build_deck(self):
        Card.values = self.values
        return self.card_instances * Deck.build_deck(self)

    def deal_hand(self) -> List[Card]:
        cards = self.cards[:self.cards_per_hand]
        self.cards = self.cards[self.cards_per_hand:]
        return cards

    @staticmethod
    def get_counters(cards):
        return [card for card in cards if card.is_counter]

    @staticmethod
    def get_non_counters(cards):
        return [card for card in cards if not card.is_counter]

    @classmethod
    def get_random_hand(cls):
        deck = cls()
        deck.shuffle()
        return Hand(deck.deal_hand())


class DoublePinochleDeck(PinochleDeck):

    values = ['J', 'Q', 'K', '10', 'A']
    card_instances = 4
    cards_per_hand = 20

    def __init__(self):
        super().__init__()


class FirehousePinochleDeck(DoublePinochleDeck):

    n_players = 3
    cards_per_hand = 25
    cards_in_kitty = 5

    def __init__(self):
        super().__init__()

    def deal_kitty(self) -> List[Card]:
        cards = self.cards[:self.cards_in_kitty]
        self.cards = self.cards[self.cards_in_kitty:]
        return cards


class Hand(PartialDeck):

    def __init__(self, cards=None):
        super().__init__(cards or [])
        self.sorted_by_suit = {}
        self.sort()

    def set(self, cards):
        self.cards = cards
        self.sort()

    def discard(self, card: Card):
        for this_card in self.sorted_by_suit[card.suit]:
            if this_card == card:
                self.cards.remove(this_card)
                self.sorted_by_suit[card.suit].remove(this_card)
                return

        raise ValueError(f'{card} is not in the hand')

    def play(self, card: Card) -> Card:
        self.discard(card)
        return card

    def add_card(self, card: Card):
        super().add_card(card)
        self.sort()

    def add_cards(self, cards: Iterable[Card]):
        super().add_cards(cards)
        self.sort()

    def sort(self):
        self.sorted_by_suit = {key: [] for key in Card.suits}
        for card in self.cards:
            self.sorted_by_suit[card.suit].append(card)
        for cards in self.sorted_by_suit.values():
            cards.sort(reverse=True)

    def has_suit(self, suit):
        return len(self.sorted_by_suit[suit]) > 0

    def has_marriage(self, suit):
        k, q = Card(suit, 'K'), Card(suit, 'Q')
        return k in self.sorted_by_suit[suit] and q in self.sorted_by_suit[suit]

    def choose_random_card(self, suit=None):
        if len(self.cards) == 0:
            raise AttributeError('Cannot choose a random card, no cards in the hand')
        if suit is None:
            return np.random.choice(self.cards)
        elif self.has_suit(suit):
            return np.random.choice(self.sorted_by_suit[suit])
        else:
            raise IndexError('Hand does not contain suit {}'.format(suit))

    def choose_random_suit(self):
        if len(self.cards) == 0:
            raise AttributeError('Cannot choose a random card, no cards in the hand')
        suit = Card.random_suit()
        while not self.has_suit(suit):
            suit = Card.random_suit()
        return suit

    def enumerate(self):
        enumerated = {idx: None for idx in range(len(self))}
        idx = 0
        for suit in self.sorted_by_suit:
            for card in self.sorted_by_suit[suit]:
                enumerated[idx] = card
                idx += 1
        return enumerated

    def to_str(self, color=False, symbol=False):
        return ' | '.join([', '.join([card.to_str(color, symbol) for card in suit]) or 'None'
                           for suit in self.sorted_by_suit.values()])

    def copy(self):
        return Hand([card.copy() for card in self.cards])

    @staticmethod
    def one_of_each():
        return Hand(Card.one_of_each())

    def __str__(self):
        return self.to_str(color=True, symbol=True)

    def __getitem__(self, key):
        if key in Card.suits:
            return self.sorted_by_suit[key]
        else:
            return super().__getitem__(key)

    def __bool__(self):
        return len(self.cards) > 0

    def __add__(self, other):
        # Todo: test add works as expected
        # Todo: test that new hand cards are not entangled to other hand cards
        return Hand(self.cards + other.cards)

    def __sub__(self, other):
        # Todo: test sub works as expected
        result = copy.deepcopy(self)
        for card in other:
            try:
                result.discard(card)
            except ValueError:
                pass
        return result


def test_card(print_func=print):
    print_func(' ')
    print_func(' ')
    print_func('Testing Card')
    print_func('............')
    print_func('Card suits:', Card.suits)
    print_func('Card values:', Card.values)
    print_func('...')
    print_func('Here is the seven of Clubs')
    card = Card(suit='Clubs', value='7')
    print_func(card)
    print_func('Here is the Ace of Diamonds')
    card = Card(suit='Diamonds', value='A')
    print_func(card)
    card_1, card_2 = Card('Clubs', '7'), Card('Clubs', '8')
    assert card_1 < card_2, '{} is not less than {}'.format(card_1, card_2)
    assert card_1 != card_2, '{} is equal to {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '8'), Card('Clubs', '7')
    assert card_1 > card_2, '{} is not greater than {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '8'), Card('Diamonds', '7')
    assert card_1 > card_2, '{} is not greater than {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '7'), Card('Clubs', '7')
    assert card_1 == card_2, '{} is not equal to {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '7'), Card('Diamonds', '7')
    assert card_1 != card_2, '{} is equal to {}'.format(card_1, card_2)
    print_func('------------')


def test_decks(print_func=print):
    print_func(' ')
    print_func(' ')
    print_func('Testing Decks')
    print_func('.............')
    print_func('Here is a Deck')
    deck = Deck()
    print_func(deck)
    print_func('Length of the deck is', len(deck))
    print_func('...')
    print_func('Here is a PinochleDeck')
    deck = PinochleDeck()
    print_func(deck)
    print_func('Length of the deck is', len(deck))
    print_func('Shuffled and dealt:')
    deck.shuffle()
    for hand in deck.deal():
        print_func(hand)
    print_func('...')
    print_func('Here is a DoublePinochleDeck')
    deck = DoublePinochleDeck()
    print_func(deck)
    print_func('Length of the deck is', len(deck))
    print_func('Shuffled and dealt:')
    deck.shuffle()
    for hand in deck.deal():
        print_func(hand)
    print_func('...')
    print_func('Here is a FirehousePinochleDeck')
    deck = FirehousePinochleDeck()
    print_func(deck)
    print_func('Length of the deck is', len(deck))
    print_func('Shuffled and dealt:')
    deck.shuffle()
    for hand in deck.deal():
        print_func(hand)
    print_func('-------------')


def test_hand(print_func=print):
    print_func(' ')
    print_func(' ')
    print_func('Testing Hand')
    print_func('............')
    deck = PinochleDeck()
    deck.shuffle()
    hands = deck.deal()
    hand = Hand(cards=hands[0])
    print_func('Here is a hand from a PinochleDeck')
    print_func(hand)
    print_func('...')
    count = len(hand)
    while len(hand):
        card = hand.choose_random_card()
        print_func('Here is the hand after playing', card)
        hand.discard(card)
        print_func(hand)
        count -= 1
        assert len(hand) == count, 'Hand has {} cards when {} were expected'.format(len(hand), count)
    print_func('------------')


def test_hand_100x():
    def do_nothing(*args):
        pass

    for _ in range(100):
        test_hand(print_func=do_nothing)

    print('100 successes!')


def test():
    test_card()
    test_decks()
    test_hand()
    test_hand_100x()


if __name__ == "__main__":
    test()
