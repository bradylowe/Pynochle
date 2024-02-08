from uuid import uuid4
import numpy as np
from GameLogic.cards import Card, Hand, PinochleDeck
from GameLogic.meld import Meld


class PinochlePlayer:

    def __init__(self, name, balance=0, user_name=None):
        self.id = str(uuid4())
        self.name = name
        self.balance = balance
        self.user_name = user_name or name
        self.score = 0

        self.index = None
        self.tricks = []
        self.took_last_trick = None
        self.hand = Hand()
        self.meld = Meld(self.hand)
        self.is_high_bidder = None
        self.partner = None
        self.trump = None
        self.position = None

    def add_points(self, points):
        self.score += points

    def remove_points(self, points):
        self.score -= points

    def get_state(self):
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance,
            'user_name': self.user_name,
            'score': self.score,
            'player_type': self.__class__.__name__,

            'index': self.index,
            'tricks': [t.get_state() for t in self.tricks],
            'took_last_trick': self.took_last_trick,
            'hand': self.hand.get_state(),
            'meld': self.meld.final,
            'is_high_bidder': self.is_high_bidder,
            'partner': None if self.partner is None else self.partner.index,
        }

    def get_shared_state(self):
        return {
            'user_name': self.user_name,
            'score': self.score,
            'player_type': self.__class__.__name__,

            'index': self.index,
            'tricks': [t.get_state() for t in self.tricks],
            'took_last_trick': self.took_last_trick,
            'meld': self.meld.final,
            'is_high_bidder': self.is_high_bidder,
            'partner': self.partner.index,
            'trump': self.trump,
            'position': self.position,
        }

    def reset_hand_state(self):
        self.tricks = []
        self.took_last_trick = None
        self.hand = Hand()
        self.meld = Meld(self.hand)
        self.is_high_bidder = None
        self.partner = None
        self.trump = None
        self.position = None

    def take_cards(self, cards):
        self.hand.add_cards(cards)
        self.meld = Meld(self.hand)

    def place_bid(self, current_bid, bid_increment):
        pass

    def play_card(self, trick):
        # Todo: improve card choice algorithm to account for who played what in the trick (pay partner)
        # Todo: players should keep track of how many Aces and trump have been played (observe)
        # Todo: players should know which other players are out of which suit (observe)
        pass

    def choose_trump(self):
        pass

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
        pass

    def discard(self, n: int = 0) -> List[Card]:
        cards = self._choose_cards_to_discard(n=n)
        for card in cards:
            self.hand.discard(card)
        self.meld = Meld(self.hand)
        return cards

    def should_pay_trick(self, trick):
        pass

    def counters(self, last_trick_value: int) -> int:
        counters = sum([1 for trick in self.tricks for card in trick if card.is_counter])
        return counters + last_trick_value if self.took_last_trick else counters

    def __str__(self):
        return self.user_name or self.name

    def __bool__(self):
        return bool(self.name)


class SimplePinochlePlayer(PinochlePlayer):

    def __init__(self, name, balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def place_bid(self, current_bid, bid_increment):
        best_suit = self.meld.best_ranked_suit
        max_bid = self.meld.total_meld_given_trump[best_suit] + 20
        new_bid = current_bid + bid_increment
        if new_bid <= max_bid:
            return new_bid

    def play_card(self, trick):
        options = trick.legal_plays(self.hand)
        if self.should_pay_trick(trick):
            counters = sorted(PinochleDeck.get_counters(options))
            card = counters[0] if counters else options[-1]
        elif trick.can_beat_winning_card([options[0]]) and options[0].value == Card.values[-1]:
            card = options[0]
        else:
            non_counters = sorted(PinochleDeck.get_non_counters(options), reverse=True)
            card = non_counters[0] if non_counters else options[-1]

        return self.hand.play(card)

    def choose_trump(self):
        return self.meld.best_ranked_suit

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
        return self.hand.cards[:n]

    def should_pay_trick(self, trick):
        if len(trick) == 0:
            return False
        if self.partner is trick.winner():
            return True
        if self.partner in trick.card_players and trick.card_to_beat.value is not 'A':
            return True
        return False


class SkilledPinochlePlayer(SimplePinochlePlayer):

    def __init__(self, name, balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def place_bid(self, current_bid, bid_increment):
        # Decide when to bet big
        # Decide when to drop the bid on someone
        pass

    def play_card(self, trick):
        # Decide whether to take the trick
        # Decide what to play into partner (back-seat)
        # Decide what to play into non-partner
        # Decide when to pay trick
        pass

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
        # Do not discard meld, trump, aces
        # Discard counters
        pass

    def should_pay_trick(self, trick):
        # Do not pay trick if someone is trumping this suit
        # Pay trick if partner is trumping this suit
        pass


class RandomPinochlePlayer(SimplePinochlePlayer):

    def __init__(self, name, balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def play_card(self, trick):
        options = trick.legal_plays(self.hand)
        return self.hand.play(np.random.choice(options))

    def choose_trump(self):
        trump = None
        while trump is None or not self.hand.has_suit(trump):
            trump = Card.suits[np.random.randint(4)]
        return trump

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
        return np.random.choice(self.hand.cards, n, replace=False)

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
        print(f'Please enter a bid amount. The minimum bid is {current_bid + bid_increment}.')
        print(f'The bid must increase in increments of {bid_increment}.')
        bid = input('Bid (press Enter to pass):  ')
        try:
            return int(bid)
        except ValueError:
            return None

    def play_card(self, trick):
        print(' ')
        legal = Hand(trick.legal_plays(self.hand))
        print('Please choose a card to play.')
        print('Hand: ', self.hand)
        enumerated = legal.enumerate()
        choices_string = ', '.join(['{}: {}'.format(idx, card) for idx, card in enumerated.items()])
        print('Legal plays:', choices_string)
        print('Position:', self.position)
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

    def choose_trump(self):
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

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
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

        return [enumerated[idx] for idx in discard_idxs]


class Kitty(PinochlePlayer):

    def __init__(self, name='Kitty', balance=0, user_name=None):
        super().__init__(name, balance, user_name)

    def take_cards(self, cards):
        self.hand.add_cards(cards)

    def place_bid(self, current_bid, bid_increment):
        pass

    def play_card(self, trick):
        pass

    def choose_trump(self):
        pass

    def _choose_cards_to_discard(self, n: int = 0) -> List[Card]:
        return self.hand.cards[:n]
