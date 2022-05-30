from GameLogic.cards import Card, PinochleDeck
from termcolor import colored

import os
os.system('color')


class Meld:

    marriage = ['Q', 'K']
    family = ['J', 'Q', 'K', '10', 'A']

    nine_of_trump_worth = 1
    card_around_meld_worth = {'J': 4, 'Q': 6, 'K': 8, 'A': 10}
    family_meld_worth = {0: 0, 1: 11, 2: 110, 3: 1100, 4: 11000}
    pinochle_meld_worth = {0: 0, 1: 4, 2: 30, 3: 90, 4: 1000}
    marriage_meld_worth = 2

    def __init__(self, hand):
        self.hand = hand
        self.counts = self.count_cards()
        self.min_counts = self.calculate_min_counts()
        self.counters = {suit: sum([self.counts[suit][value] for value in PinochleDeck.counters])
                         for suit in Card.suits}

        # Meld that does not depend on trump
        self.nines_meld = {suit: Meld.nine_of_trump_worth * len(self.counts[suit]['9']) if '9' in Card.values else 0
                           for suit in Card.suits}
        self.marriage_melds = {suit: Meld.marriage_meld_worth * self.count_marriages(suit)
                               for suit in Card.suits}
        self.pinochle_meld = self.calculate_pinochle_meld()
        self.cards_around_meld = self.calculate_meld_for_aces_kings_queens_jacks()
        self.meld = self.calculate_meld_without_trump()

        # Meld that DOES depend on trump
        self.meld_with_trump = {suit: self.calculate_meld_with_trump(suit) for suit in Card.suits}

        self.power = {suit: self.calculate_suit_power(suit) for suit in Card.suits}
        self.rank = {suit: self.calculate_suit_rank(suit) for suit in Card.suits}

        self.best_ranked_suit = self.calculate_best_ranked_suit()
        self.meld_of_best_suit = self.meld_with_trump[self.best_ranked_suit] if self.best_ranked_suit else 0
        self.counters_of_best_suit = self.counters[self.best_ranked_suit] if self.best_ranked_suit else 0

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

    def calculate_family_meld(self, suit):
        family_count = min([self.counts[suit][value] for value in Meld.family])
        return Meld.family_meld_worth[family_count]

    def calculate_meld_without_trump(self):
        return sum(self.marriage_melds.values()) + self.pinochle_meld + self.cards_around_meld

    def calculate_meld_with_trump(self, suit):
        return self.meld + self.marriage_melds[suit] + self.calculate_family_meld(suit) + self.nines_meld[suit]

    def calculate_suit_power(self, suit):
        return sum([idx * idx * self.counts[suit][Card.values[idx]] for idx in range(len(Card.values))])

    def calculate_suit_rank(self, suit):
        if self.marriage_melds[suit] > 0:
            return self.meld_with_trump[suit] * 5 + self.power[suit]
        else:
            return 0

    def calculate_best_ranked_suit(self):
        best_suit, best_rank = 'Spades', 0
        for suit, rank in self.rank.items():
            if rank > best_rank:
                best_rank = rank
                best_suit = suit
        return best_suit

    def to_str(self, color=False):
        melds = []
        for suit, meld in self.meld_with_trump.items():
            suit_meld = '{} - {}'.format(suit, meld)
            melds.append(colored(suit_meld, 'yellow') if (color and self.best_ranked_suit == suit) else suit_meld)
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
    print('Melds: ', meld.meld_with_trump)
    print('Best:  ', '{} - {}'.format(meld.best_ranked_suit, meld.meld_of_best_suit))
