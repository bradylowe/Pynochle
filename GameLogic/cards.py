import copy
import numpy as np
from itertools import product
from termcolor import colored

import os
os.system('color')


class Card:

    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
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

    @staticmethod
    def unique_cards():
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

    def __str__(self):
        return colored('{}{}'.format(self.value, Card.suit_symbols[self.suit]), Card.suit_colors[self.suit])

    def __repr__(self):
        return Card.__str__(self)

    def __lt__(self, other):
        return Card.values.index(self.value) < Card.values.index(other.value)

    def __gt__(self, other):
        return Card.values.index(self.value) > Card.values.index(other.value)

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash(self.suit + self.value + str(id(self)))


class PartialDeck:

    def __init__(self, cards):
        self.cards = cards

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
        assert len(self.cards), 'Cannot choose a random card, no cards in the deck'
        return np.random.choice(self.cards)

    def enumerate(self):
        return {idx: card for idx, card in enumerate(self.cards)}

    def __str__(self):
        return ', '.join([str(card) for card in self.cards])

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return DeckIterator(self)

    def __getitem__(self, key):
        return self.cards[key]


class DeckIterator:
    """
    This class allows us to iterate through our cards.
    """

    def __init__(self, deck):
        self._deck = deck
        self._index = 0

    def __next__(self):
        if self._index < len(self._deck):
            card = self._deck.cards[self._index]
            self._index += 1
            return card
        else:
            raise StopIteration


class Deck(PartialDeck):

    values = Card.values

    def __init__(self):
        super().__init__(self.build_deck())

    def build_deck(self):
        return [Card(s, v) for s, v in product(Card.suits, Card.values)]

    def deal(self):
        pass


class PinochleDeck(Deck):

    n_players = 4
    values = ['9', 'J', 'Q', 'K', '10', 'A']
    counters = ['K', '10', 'A']
    is_counter_dict = {}

    def __init__(self):
        Card.values = self.values
        super().__init__()
        PinochleDeck.is_counter_dict = {key: key in PinochleDeck.counters for key in PinochleDeck.values}

    def build_deck(self):
        Card.values = self.values
        return 2 * Deck.build_deck(self)

    def deal(self):
        return self.cards[0:12], self.cards[12:24], self.cards[24:36], self.cards[36:48]

    @staticmethod
    def is_counter(card):
        return PinochleDeck.is_counter_dict[card.value]

    @staticmethod
    def get_counters(cards):
        return sorted([card for card in cards if PinochleDeck.is_counter(card)], reverse=True)

    @staticmethod
    def get_non_counters(cards):
        return sorted([card for card in cards if not PinochleDeck.is_counter(card)], reverse=True)


class DoublePinochleDeck(PinochleDeck):

    values = ['J', 'Q', 'K', '10', 'A']

    def __init__(self):
        super().__init__()

    def build_deck(self):
        return 2 * PinochleDeck.build_deck(self)

    def deal(self):
        return self.cards[0:20], self.cards[20:40], self.cards[40:60], self.cards[60:80]


class FirehousePinochleDeck(DoublePinochleDeck):

    n_players = 3

    def __init__(self):
        super().__init__()

    def deal(self):
        return self.cards[0:25], self.cards[25:50], self.cards[50:75], self.cards[75:80]


class Hand(PartialDeck):

    def __init__(self, cards=None):
        super().__init__(cards or [])
        self.sorted_cards = {}
        self.sort()

    def set(self, cards):
        self.cards = cards
        self.sort()

    def play(self, card):
        for this_card in self.sorted_cards[card.suit]:
            if this_card == card:
                self.cards.remove(this_card)
                self.sorted_cards[card.suit].remove(this_card)
                return card
        raise ValueError('Cannot play {}, it is not in the hand'.format(str(card)))

    def add(self, cards):
        if hasattr(cards, '__iter__'):
            self.cards.extend(cards)
        else:
            self.cards.append(cards)
        self.sort()

    def sorted_by_suit(self):
        sorted_by_suit = {key: [] for key in Card.suits}
        for card in self.cards:
            sorted_by_suit[card.suit].append(card)
        return sorted_by_suit

    def sort(self):
        self.sorted_cards = {suit: sorted(cards, reverse=True) for suit, cards in self.sorted_by_suit().items()}

    def has_suit(self, suit):
        return len(self.sorted_cards[suit]) > 0

    def choose_random_card(self, suit=None):
        assert len(self.cards), 'Cannot choose a random card, no cards in the hand'
        if suit is None:
            return PartialDeck.choose_random_card(self)
        elif self.has_suit(suit):
            return np.random.choice(self.sorted_cards[suit])
        else:
            raise IndexError('Hand does not contain suit {}'.format(suit))

    def choose_random_suit(self):
        assert len(self.cards), 'Cannot choose a random suit, no cards in the hand'
        suit = Card.random_suit()
        while not self.has_suit(suit):
            suit = Card.random_suit()
        return suit

    def enumerate(self, sorted=True):
        if sorted:
            enumerated = {idx: None for idx in range(len(self))}
            idx = 0
            for suit in self.sorted_cards:
                for card in self.sorted_cards[suit]:
                    enumerated[idx] = card
                    idx += 1
            return enumerated
        else:
            return PartialDeck.enumerate(self)

    def __str__(self):
        return ' | '.join([', '.join([str(card) for card in suit]) or 'None'
                           for suit in self.sorted_cards.values()])

    def __getitem__(self, key):
        if key in Card.suits:
            return self.sorted_cards[key]
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
                result.play(card)
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
    card_1, card_2 = Card('Clubs', '8'), Card('Clubs', '7')
    assert card_1 > card_2, '{} is not greater than {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '8'), Card('Diamonds', '7')
    assert card_1 > card_2, '{} is not greater than {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '7'), Card('Clubs', '7')
    assert card_1 == card_2, '{} is not equal to {}'.format(card_1, card_2)
    card_1, card_2 = Card('Clubs', '7'), Card('Diamonds', '7')
    assert card_1 != card_2, '{} is erroneously equal to {}'.format(card_1, card_2)
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
        hand.play(card)
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
