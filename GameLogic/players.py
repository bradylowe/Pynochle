from typing import Union, List
from uuid import uuid4
import numpy as np
from GameLogic.cards import Card, Hand, PinochleDeck
from GameLogic.meld import Meld
from GameLogic.tricks import Trick


class PinochlePlayer:

    type_from_str = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PinochlePlayer.type_from_str[cls.__name__] = cls

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
        self.partner = None
        self.trump = None
        self.position = None
        self.is_high_bidder = False

    def add_points(self, points):
        self.score += points

    def remove_points(self, points):
        self.score -= points

    @staticmethod
    def restore_state(state: dict) -> 'PinochlePlayer':
        player_type = PinochlePlayer.type_from_str[state['player_type']]
        player = player_type(state['name'])
        for key in state:
            if key == 'player_type':
                continue
            player.__setattr__(key, state[key])

        player.tricks = [Trick.restore_state(t) for t in state['tricks']]
        player.hand = Hand.restore_state(state['hand'])
        player.meld = Meld(player.hand)

        return player

    def replace_player_index_with_player(self, player_index_map: dict):
        if self.tricks:
            for trick in self.tricks:
                trick.replace_player_index_with_player(player_index_map)
        if self.partner is not None and isinstance(self.partner, int):
            self.partner = player_index_map[self.partner]

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
            'partner': None if self.partner is None else self.partner.index,
            'trump': self.trump,
            'position': self.position,
            'is_high_bidder': self.is_high_bidder,
        }

    def get_shared_state(self):
        state = self.get_state()
        del state['id']
        del state['balance']
        del state['hand']
        return state

    def reset_hand_state(self):
        self.tricks = []
        self.took_last_trick = None
        self.hand = Hand()
        self.meld = Meld(self.hand)
        self.partner = None
        self.trump = None
        self.position = None

    def take_cards(self, cards):
        self.hand.add_cards(cards)
        self.meld = Meld(self.hand)

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        pass

    def choose_trump(self):
        pass

    def choose_card_to_play(self, trick: Trick) -> Card:
        # Todo: improve card choice algorithm to account for who played what in the trick (pay partner)
        # Todo: players should keep track of how many Aces and trump have been played (observe)
        # Todo: players should know which other players are out of which suit (observe)
        pass

    def play_card(self, card: Card) -> Card:
        return self.discard(card)

    def discard(self, cards: Union[Card, List[Card]]):
        if isinstance(cards, Card):
            self.hand.discard(cards)
        else:
            for card in cards:
                self.hand.discard(card)
        return cards

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        pass

    def pass_cards(self, n: int = 0) -> List[Card]:
        cards = self._choose_cards_to_pass(n=n)
        self.discard(cards)
        return cards

    def should_pay_trick(self, trick):
        pass

    def counters(self, last_trick_value: int) -> int:
        counters = sum([1 for trick in self.tricks for card in trick if card.is_counter])
        return counters + last_trick_value if self.took_last_trick else counters

    def __str__(self):
        return self.user_name or self.name

    def __bool__(self):
        return True


class RandomPinochlePlayer(PinochlePlayer):

    def choose_card_to_play(self, trick: Trick) -> Card:
        options = trick.legal_plays(self.hand)
        return np.random.choice(options)

    def choose_trump(self):
        trump = None
        while trump is None or not self.hand.has_suit(trump):
            trump = Card.suits[np.random.randint(4)]
        return trump

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        return np.random.choice(self.hand.cards, n, replace=False)

    def should_pay_trick(self, trick):
        return bool(np.random.randint(2))


class SimplePinochlePlayer(RandomPinochlePlayer):

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        best_suit = self.meld.best_ranked_suit
        max_bid = self.meld.total_meld_given_trump[best_suit] + 20
        new_bid = current_bid + bid_increment
        if new_bid <= max_bid:
            return new_bid

    def choose_card_to_play(self, trick: Trick) -> Card:
        options = trick.legal_plays(self.hand)
        if self.should_pay_trick(trick):
            counters = sorted(PinochleDeck.get_counters(options))
            card = counters[0] if counters else options[-1]
        elif trick.can_beat_winning_card([options[0]]) and options[0].value == Card.values[-1]:
            card = options[0]
        else:
            non_counters = sorted(PinochleDeck.get_non_counters(options), reverse=True)
            card = non_counters[0] if non_counters else options[-1]

        return card

    def choose_trump(self):
        return self.meld.best_ranked_suit

    def should_pay_trick(self, trick):
        if len(trick) == 0:
            return False
        if self.partner is trick.winner():
            return True
        if self.partner in trick.card_players and trick.card_to_beat.value is not 'A':
            return True
        return False


class SkilledPinochlePlayer(SimplePinochlePlayer):

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        # Decide when to bet big
        # Decide when to drop the bid on someone
        pass

    def choose_card_to_play(self, trick: Trick) -> Card:
        # Decide whether to take the trick
        # Decide what to play into partner (back-seat)
        # Decide what to play into non-partner
        # Decide when to pay trick
        pass

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        # Do not discard meld, trump, aces
        # Discard counters
        pass

    def should_pay_trick(self, trick):
        # Do not pay trick if someone is trumping this suit
        # Pay trick if partner is trumping this suit
        pass


class MonteCarloPinochlePlayer(SimplePinochlePlayer):

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        # Decide when to bet big
        # Decide when to drop the bid on someone
        pass

    def choose_card_to_play(self, trick: Trick) -> Card:
        # Decide whether to take the trick
        # Decide what to play into partner (back-seat)
        # Decide what to play into non-partner
        # Decide when to pay trick
        pass

    def choose_trump(self):
        pass

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        # Do not discard meld, trump, aces
        # Discard counters
        pass


class HumanPinochlePlayer(PinochlePlayer):

    def __init__(self, name=None, balance=0, user_name=None):
        if name is None:
            print(' ')
            name = input('What is your name?  ')
        super().__init__(name, balance, user_name)

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        print(' ')
        print(f'Please enter a bid amount. The minimum bid is {current_bid + bid_increment}.')
        print(f'The bid must increase in increments of {bid_increment}.')
        bid = input('Bid (press Enter to pass):  ')
        try:
            return int(bid)
        except ValueError:
            return None

    def choose_card_to_play(self, trick: Trick) -> Card:
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
        return card

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

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
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
        self.index = -1

    def take_cards(self, cards):
        self.hand.add_cards(cards)

    def counters(self, last_trick_value: int) -> int:
        counters = sum([1 for card in self.hand if card.is_counter])
        return counters + last_trick_value if self.took_last_trick else counters

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        pass

    def choose_card_to_play(self, trick: Trick) -> Card:
        pass

    def choose_trump(self):
        pass

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        return self.hand.cards[:n]
