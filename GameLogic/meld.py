from GameLogic.cards import Card, Hand
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

    def __init__(self, hand: Hand, trump: str = None):
        self.hand = hand
        self.counts = self.count_cards()
        self.min_counts = self.minimum_value_counts()

        # Set the total meld once trump is called
        self.trump = None
        self.final = None

        # Meld that does not depend on trump
        self.cards_used_in_meld = {suit: {value: 0 for value in Card.values} for suit in Card.suits}
        self.marriage_melds = {suit: self.calculate_marriage_meld(suit) for suit in Card.suits}
        self.pinochle_meld = self.calculate_pinochle_meld()
        self.cards_around_meld = self.calculate_meld_for_aces_kings_queens_jacks_around()
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

    @property
    def has_double_jacks(self):
        return self.min_counts['J'] >= 2

    @property
    def has_double_queens(self):
        return self.min_counts['Q'] >= 2

    @property
    def has_double_kings(self):
        return self.min_counts['K'] >= 2

    @property
    def has_double_pinochle(self):
        return self.count_pinochles() >= 2

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

    def minimum_value_counts(self):
        """Find the min number of Aces, Kings, Queens, etc. in each suit"""
        return {val: min([self.counts[suit][val] for suit in Card.suits])
                for val in Card.values}

    def count_marriages(self, suit):
        return min([self.counts[suit][value] for value in Meld.marriage])

    def count_families(self, suit):
        return min([self.counts[suit][value] for value in Meld.family])

    def count_pinochles(self):
        return min([self.counts['Spades']['Q'], self.counts['Diamonds']['J']])

    def calculate_pinochle_meld(self):
        count = self.count_pinochles()
        self.cards_used_in_meld['Spades']['Q'] = max(count, self.cards_used_in_meld['Spades']['Q'])
        self.cards_used_in_meld['Diamonds']['J'] = max(count, self.cards_used_in_meld['Diamonds']['J'])
        return Meld.pinochle_meld_worth[count]

    def calculate_meld_for_aces_kings_queens_jacks_around(self):
        meld_around = 0

        # Check each value that we can have around (A, K, Q, J)
        for value in Meld.card_around_meld_worth:
            if value not in Card.values:
                continue

            # See if we have one (or more) in each suit
            if self.min_counts[value]:
                count = self.min_counts[value]
                meld_around += Meld.card_around_meld_worth[value] * 10 ** (count - 1)

                # Update the record of cards used in the meld
                for suit in Card.suits:
                    self.cards_used_in_meld[suit][value] = max(count, self.cards_used_in_meld[suit][value])

        return meld_around

    def calculate_nines_meld(self, suit):
        if '9' not in Card.values:
            return 0
        count = self.counts[suit]['9']
        self.cards_used_in_meld[suit]['9'] = max(count, self.cards_used_in_meld[suit]['9'])
        return count * Meld.nine_of_trump_worth

    def calculate_marriage_meld(self, suit):
        count = self.count_marriages(suit)
        for value in Meld.marriage:
            self.cards_used_in_meld[suit][value] = max(count, self.cards_used_in_meld[suit][value])
        return count * Meld.marriage_meld_worth

    def calculate_family_meld(self, suit):
        count = self.count_families(suit)
        for value in Meld.family:
            self.cards_used_in_meld[suit][value] = max(count, self.cards_used_in_meld[suit][value])
        return Meld.family_meld_worth[count]

    def calculate_meld_without_trump(self):
        return sum(self.marriage_melds.values()) + self.pinochle_meld + self.cards_around_meld

    def calculate_meld_with_trump(self, suit):
        additional_trump_meld = self.marriage_melds[suit] + self.family_melds[suit] + self.nines_meld[suit]
        return self.meld_without_trump + additional_trump_meld

    def calculate_suit_power(self, suit: str) -> int:
        if not self.hand:
            return 0

        n_suit = len(self.hand.sorted_by_suit[suit])
        return n_suit * sum([
            idx * idx * self.counts[suit][Card.values[idx]]
            for idx in range(len(Card.values))
        ])

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

    hand = DoublePinochleDeck.get_random_hand()
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
