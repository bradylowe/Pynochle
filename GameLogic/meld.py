from GameLogic.cards import Card
from termcolor import colored

import os
os.system('color')


class Meld:

    marriage = ['Q', 'K']
    family = ['J', 'Q', 'K', '10', 'A']

    # Todo: Move these values to GAME SETTINGS
    nine_of_trump_worth = 1
    card_around_meld_worth = {'J': 4, 'Q': 6, 'K': 8, 'A': 10}
    family_meld_worth = {0: 0, 1: 11, 2: 110, 3: 1100, 4: 11000}
    pinochle_meld_worth = {0: 0, 1: 4, 2: 30, 3: 90, 4: 1000}
    marriage_meld_worth = 2

    def __init__(self, hand, trump=None):
        self.hand = hand
        self.counts = self.count_cards()
        self.min_counts = self.calculate_min_counts()

        # Set the total meld once trump is called
        self.trump = None
        self.final = None

        # Meld that does not depend on trump
        self.marriage_melds = {suit: self.calculate_marriage_meld(suit) for suit in Card.suits}
        self.pinochle_meld = self.calculate_pinochle_meld()
        self.cards_around_meld = self.calculate_meld_for_aces_kings_queens_jacks()
        self.meld_without_trump = self.calculate_meld_without_trump()

        # Meld that depends on trump
        self.family_melds = {suit: self.calculate_family_meld(suit) for suit in Card.suits}
        self.nines_meld = {suit: self.calculate_nines_meld(suit) for suit in Card.suits}
        self.total_meld_given_trump = {suit: self.calculate_meld_with_trump(suit) for suit in Card.suits}

        self.power = {suit: self.calculate_suit_power(suit) for suit in Card.suits}
        self.rank = {suit: self.calculate_suit_rank(suit) for suit in Card.suits}

        # Set trump if it was given
        if trump is not None:
            self.set_trump(trump)

    @property
    def best_ranked_suit(self):
        best_suit, best_rank = Card.suits[0], 0
        for suit, rank in self.rank.items():
            if rank > best_rank:
                best_rank = rank
                best_suit = suit
        return best_suit

    def set_trump(self, trump):
        """Set the value of the final meld once trump is called"""
        self.trump = trump
        self.final = self.total_meld_given_trump[trump]

    def count_cards(self):
        """Count the number of cards in a 2D dictionary sorted by suit and then card value"""
        counts = {suit: {value: 0 for value in Card.values}
                  for suit in Card.suits}

        for card in self.hand:
            counts[card.suit][card.value] += 1

        return counts

    def calculate_min_counts(self):
        """Find the min number of Aces, Kings, Queens, etc. in each suit"""
        return {val: min([self.counts[suit][val] for suit in Card.suits])
                for val in Card.values}

    def count_marriages(self, suit):
        return min([self.counts[suit][value] for value in Meld.marriage])

    def count_families(self, suit):
        return min([self.counts[suit][value] for value in Meld.family])

    def calculate_pinochle_meld(self):
        pinochle_count = min([self.counts['Spades']['Q'], self.counts['Diamonds']['J']])
        return Meld.pinochle_meld_worth[pinochle_count]

    def calculate_meld_for_aces_kings_queens_jacks(self):
        meld = 0
        for card_value in Meld.card_around_meld_worth:
            if card_value in Card.values:
                count = self.min_counts[card_value]
                if count:
                    meld += Meld.card_around_meld_worth[card_value] * 10 ** (count - 1)
        return meld

    def calculate_nines_meld(self, suit):
        if '9' not in Card.values:
            return 0
        return Meld.nine_of_trump_worth * self.counts[suit]['9']

    def calculate_marriage_meld(self, suit):
        return Meld.marriage_meld_worth * self.count_marriages(suit)

    def calculate_family_meld(self, suit):
        return Meld.family_meld_worth[self.count_families(suit)]

    def calculate_meld_without_trump(self):
        return sum(self.marriage_melds.values()) + self.pinochle_meld + self.cards_around_meld

    def calculate_meld_with_trump(self, suit):
        additional_trump_meld = self.marriage_melds[suit] + self.family_melds[suit] + self.nines_meld[suit]
        return self.meld_without_trump + additional_trump_meld

    def calculate_suit_power(self, suit):
        return sum([idx * idx * self.counts[suit][Card.values[idx]] for idx in range(len(Card.values))])

    def calculate_suit_rank(self, suit):
        # Cannot bid on suit without marriage
        if self.has_marriage(suit):
            return self.total_meld_given_trump[suit] * 5 + self.power[suit]
        else:
            return 0

    def has_marriage(self, suit: str) -> bool:
        return self.marriage_melds[suit] > 0

    def to_str(self, color=False):
        melds = []
        best_ranked_suit = self.best_ranked_suit
        for suit, meld in self.total_meld_given_trump.items():
            suit_meld = '{} - {}'.format(suit, meld)
            melds.append(colored(suit_meld, 'yellow') if (color and best_ranked_suit == suit) else suit_meld)
        return ' | '.join(melds)

    def __str__(self):
        return self.to_str(color=True)


if __name__ == "__main__":

    from GameLogic.cards import DoublePinochleDeck, Hand

    deck = DoublePinochleDeck()
    deck.shuffle()
    hands = deck.deal()

    hand = Hand(hands[0])
    print(hand)

    meld = Meld(hand)
    print(meld)
    print(' ')
    print('Power: ', meld.power)
    print('Ranks: ', meld.rank)
    print('Melds: ', meld.total_meld_given_trump)
    print('Best:  ', '{} - {}'.format(meld.best_ranked_suit, meld.total_meld_given_trump[meld.best_ranked_suit]))
    print()
    print('Nines meld: ', meld.nines_meld)
    print('Family melds: ', meld.family_melds)
    print('Marriage melds: ', meld.marriage_melds)
    print('Pinochle meld: ', meld.pinochle_meld)
    print('Cards around melds: ', meld.cards_around_meld)
    print('---')
    print('Meld without trump: ', meld.meld_without_trump)
