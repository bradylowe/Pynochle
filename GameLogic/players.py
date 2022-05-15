import numpy as np
from GameLogic.cards import Card, Hand, PinochleDeck
from GameLogic.meld import Meld


class PinochlePlayer:

    def __init__(self, name, balance=0, user_name=None):
        self.name = name
        self.balance = balance
        self.user_name = user_name or name

        self.is_high_bidder = False
        self.partner = None

        self.counters = 0
        self.score = 0

        self.hand = Hand()
        self.meld = Meld(self.hand)

    def add_points(self, points):
        self.score += points

    def remove_points(self, points):
        self.score -= points

    def add_counters(self, counters):
        self.counters += counters

    def reset(self):
        self.counters = 0
        self.is_high_bidder = False
        self.partner = None

    def new_hand(self, cards):
        self.hand.set(cards)
        self.meld = Meld(self.hand)

    def take_cards(self, cards):
        self.hand.add(cards)
        self.meld = Meld(self.hand)

    def place_bid(self, current_bid, bid_increment):
        pass

    def play_card(self, trick, remaining_players=None):
        # Todo: improve card choice algorithm to account for who played what in the trick (pay partner)
        # Todo: players should keep track of how many Aces and trump have been played (observe)
        # Todo: players should know which other players are out of which suit (observe)
        pass

    def call_trump(self):
        pass

    def discard(self, n=0):
        pass

    def should_pay_trick(self, trick, remaining_players=None):
        pass

    def __str__(self):
        return self.user_name or self.name

    def __bool__(self):
        return bool(self.name)


class AutoPinochlePlayer(PinochlePlayer):

    def __init__(self, name, balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def place_bid(self, current_bid, bid_increment):
        max_bid = self.meld.meld_of_best_suit + 20
        new_bid = current_bid + bid_increment
        if new_bid <= max_bid:
            return new_bid

    def play_card(self, trick, remaining_players=None):
        options = trick.legal_plays(self.hand)
        if self.should_pay_trick(trick, remaining_players):
            counters = PinochleDeck.get_counters(options)
            card = counters[-1] if counters else options[-1]
        elif trick.can_beat_winning_card([options[0]]) and options[0].value == Card.values[-1]:
            card = options[0]
        else:
            non_counters = PinochleDeck.get_non_counters(options)
            card = non_counters[-1] if non_counters else options[-1]
        return self.hand.play(card)

    def call_trump(self):
        return self.meld.best_ranked_suit

    def discard(self, n=0):
        cards = [self.hand.play(card) for card in self.hand.cards[:n]]
        self.meld = Meld(self.hand)
        return cards

    def should_pay_trick(self, trick, remaining_players=None):
        return trick.winner() is self.partner or (remaining_players and remaining_players[0] is self.partner)


class RandomPinochlePlayer(AutoPinochlePlayer):

    def __init__(self, name, balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def play_card(self, trick, remaining_players=None):
        options = trick.legal_plays(self.hand)
        if self.should_pay_trick(trick, remaining_players):
            options = PinochleDeck.get_counters(options) or options
        else:
            options = PinochleDeck.get_non_counters(options) or options
        return self.hand.play(np.random.choice(options))

    def call_trump(self):
        trump = None
        while trump is None or not self.hand.has_suit(trump):
            trump = Card.suits[np.random.randint(4)]
        return trump

    def discard(self, n=0):
        cards = []
        while len(cards) < n:
            cards.append(self.hand.play(self.hand.choose_random_card()))
        self.meld = Meld(self.hand)
        return cards

    def should_pay_trick(self, trick, remaining_players=None):
        return bool(np.random.randint(2))


class HumanPinochlePlayer(PinochlePlayer):

    def __init__(self, name=None, balance=0, user_name=None):
        if name is None:
            print(' ')
            name = input('What is your name?  ')
        super().__init__(name, balance, user_name)

    def place_bid(self, current_bid, bid_increment):
        print(' ')
        print('Please enter a bid amount. The minimum bid is {}.'.format(current_bid + bid_increment))
        print('The bid must increase in increments of {}.'.format(bid_increment))
        bid = input('Bid (press Enter to pass):  ')
        try:
            return int(bid)
        except ValueError:
            return None

    def play_card(self, trick, remaining_players=None):
        print(' ')
        legal = Hand(trick.legal_plays(self.hand))
        print('Please choose a card to play.')
        print('Hand: ', self.hand)
        enumerated = legal.enumerate()
        choices_string = ', '.join(['{}: {}'.format(idx, card) for idx, card in enumerated.items()])
        print('Legal plays:', choices_string)
        card = None
        while card is None:
            print('Trick: ', str(trick))
            try:
                card = int(input('Choice:  '))
                card = enumerated[card]
            except ValueError:
                print('Invalid choice of card.')
                card = None
            except KeyError:
                print('Invalid choice of card.')
                card = None
        return self.hand.play(card)

    def call_trump(self):
        print(' ')
        enumerated_choices = ', '.join(['{}: {}'.format(idx, suit) for idx, suit in enumerate(Card.suits)])
        print('Please choose trump  ({})'.format(enumerated_choices))
        while True:
            choice = input('Choice: ')
            try:
                return Card.suits[int(choice)]
            except ValueError:
                print('Please enter an integer with no spaces')
            except IndexError:
                print('Invalid choice')

    def discard(self, n=0):
        print(' ')
        discard_idxs = []

        print('Please choose {} cards to discard'.format(n))
        enumerated = self.hand.enumerate()
        choices_string = ', '.join(['{}: {}'.format(idx, card) for idx, card in enumerated.items()])
        print(choices_string)

        # Let the user choose cards one at a time
        while len(discard_idxs) < n:
            card = None
            while card is None:
                try:
                    card = int(input('Choice (one at a time, please):  '))
                except ValueError:
                    print('Invalid choice of card')
                    card = None
                if card in discard_idxs:
                    print('Cannot choose the same card twice')
                    card = None
                elif not isinstance(card, int):
                    print('Please enter an integer with no spaces')
                    card = None
                elif card < 0 or card >= len(self.hand.cards):
                    print('Invalid choice of card')
                    card = None
                else:
                    discard_idxs.append(card)

        cards = [self.hand.play(enumerated[idx]) for idx in discard_idxs]
        self.meld = Meld(self.hand)
        return cards
