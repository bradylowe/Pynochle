import sys
import os
sys.path.append(os.path.abspath('./'))

here = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(here)

from typing import Optional, List
from uuid import uuid4
import json
from datetime import datetime

from GameLogic.cards import (
    Card,
    PinochleDeck,
    DoublePinochleDeck,
    FirehousePinochleDeck,
    Hand,
)
from GameLogic.players import (
    PinochlePlayer,
    SimplePinochlePlayer,
    RandomPinochlePlayer,
    HumanPinochlePlayer,
    Kitty,
)
from GameLogic.tricks import Trick


class Pinochle:

    # Settings
    last_trick_value = 1
    deck_type = PinochleDeck
    dropped_bid_amt = 25
    minimum_bid_amt = 30
    bid_increment_amt = 5
    n_players = 4
    n_cards_to_pass = 3
    winning_score = 350
    partner_gets_points = False

    def __init__(self, players=None, printing=False, logging=False):

        # Operational parameters
        self.game_id = str(uuid4())
        self._printing = printing
        self._logging = logging
        self._state_log = []

        # Game information
        self.deck = None
        self.players = []
        self.set_players(players)
        self.human_player = self.find_human_player()
        self.hand_count = -1
        self.scores = {p.id: p.score for p in self.players}

        # Hand information
        self.current_players = []
        self.cards_played = []

        # Bid information
        self.trump = None
        self.high_bid = None
        self.high_bidder = None
        self.current_bid = None
        self.dropped_bid = None
        self.saved_bid = None

        # Trick information
        self.trick = None
        self.trick_winner = None
        self.tricks_played = []
        self.remaining_cards = {suit: {val: self.deck_type.card_instances for val in Card.values} for suit in Card.suits}

        # Per-player hand information
        self.bids = {p: None for p in self.players}
        self.melds = {p: None for p in self.players}
        self.meld_cards = {p: [] for p in self.players}
        self.tricks_taken = {p: [] for p in self.players}
        self.has_suit = {p: {suit: True for suit in Card.suits} for p in self.players}
        self.has_card = {p: {suit: {val: True for val in Card.values} for suit in Card.suits} for p in self.players}

        # Log initial state
        self.log_state('INITIALIZE GAME')

    @property
    def printing(self):
        return self._printing or self.human_player is not None

    @printing.setter
    def printing(self, value):
        self._printing = value

    def print(self, *args):
        if self.printing:
            print(*args)

    def play_game(self):
        self.log_state('START GAME', save_state=False)
        while not any([p.score > self.winning_score for p in self.players]):
            self.play_hand()
        self.log_state('END GAME', save_state=False)

    def set_players(self, players: List[PinochlePlayer]):
        self.players = players
        for idx, player in enumerate(self.players):
            player.index = idx

    def start_next_hand(self):

        # Increment hand count
        self.hand_count += 1

        # Hand information
        self.current_players = []
        self.cards_played = []

        # Bid information
        self.trump = None
        self.high_bid = None
        self.high_bidder = None
        self.current_bid = None
        self.dropped_bid = None
        self.saved_bid = None

        # Trick information
        self.trick = None
        self.trick_winner = None
        self.tricks_played = []
        self.remaining_cards = {suit: {val: self.deck_type.card_instances for val in Card.values} for suit in Card.suits}

        # Per-player hand information
        self.bids = {p: None for p in self.players}
        self.melds = {p: None for p in self.players}
        self.meld_cards = {p: [] for p in self.players}
        self.tricks_taken = {p: [] for p in self.players}
        self.has_suit = {p: {suit: True for suit in Card.suits} for p in self.players}
        self.has_card = {p: {suit: {val: True for val in Card.values} for suit in Card.suits} for p in self.players}

        self.print('\nBeginning hand {}'.format(self.hand_count))
        self.log_state(f'START HAND {self.hand_count}')

    def get_settings_state(self):
        return {
            'last_trick_value': self.last_trick_value,
            'deck_type': self.deck_type.__name__,
            'dropped_bid_amt': self.dropped_bid_amt,
            'minimum_bid_amt': self.minimum_bid_amt,
            'bid_increment_amt': self.bid_increment_amt,
            'n_players': self.n_players,
            'n_cards_to_pass': self.n_cards_to_pass,
            'winning_score': self.winning_score,
            'partner_gets_points': False,
        }

    def get_state(self):
        return {
            **self.get_settings_state(),

            'game_id': self.game_id,
            'players': [p.get_state() for p in self.players],
            'human_player': None if self.human_player is None else self.human_player.index,
            'hand_count': self.hand_count,
            'scores': self.scores,

            'current_players': [p.index for p in self.current_players],
            'cards_played': [(c.get_state(), p.index) for c, p in self.cards_played],

            'trump': self.trump,
            'high_bid': self.high_bid,
            'high_bidder': None if self.high_bidder is None else self.high_bidder.index,
            'current_bid': self.current_bid,
            'dropped_bid': self.dropped_bid,
            'saved_bid': self.saved_bid,

            'trick': None if self.trick is None else self.trick.get_state(),
            'trick_winner': None if self.trick_winner is None else self.trick_winner.index,
            'tricks_played': [t.get_state() for t in self.tricks_played],
            'remaining_cards': self.remaining_cards,

            'bids': {p.index: self.bids[p] for p in self.players},
            'melds': {p.index: self.melds[p] for p in self.players},
            'meld_cards': {p.index: [c.get_state() for c in self.meld_cards[p]] for p in self.players},
            'tricks_taken': {p.index: [t.get_state() for t in self.tricks_taken[p]] for p in self.players},
            'has_suit': {p.index: self.has_suit[p] for p in self.players},
            'has_card': {p.index: self.has_card[p] for p in self.players},
        }

    def get_shared_state(self):
        state = self.get_state()
        state['players'] = [p.get_shared_state() for p in self.players]
        return state

    def log_state(self, action: str, save_state: bool = True):
        if self._logging:
            self._state_log.append(f'<<<{action}>>>')
            if save_state:
                self._state_log.append(self.get_state())

    def write_log_to_file(self, filename: str = None, path: str = None):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if filename is None:
            filename = f'state_log_{now}.json'

        if path is not None:
            filename = os.path.abspath(os.path.join(base_path, path, filename))

        with open(filename, 'w') as f:
            data = {
                'state_log': self._state_log,
                'timestamp': now,
            }
            json.dump(data, f)
            print(f'Wrote hand to {filename}')

    def play_to(self, winning_score):
        self.winning_score = winning_score

    def set_include_partners_meld(self, value):
        self.partner_gets_points = value

    def deal(self):

        self.deck = self.deck_type()
        if self.shuffle:
            self.deck.shuffle()
        self._deal_hands_to_players()
        self.show_human_hand_and_meld()
        self.log_state('CARDS DELT')

    def _deal_hands_to_players(self):
        for player in self.current_players:
            if not player.hand:
                player.take_cards(self.deck.deal_hand())

    def find_human_player(self):
        for player in self.players:
            if isinstance(player, HumanPinochlePlayer):
                return player

    def show_human_hand_and_meld(self):
        if self.human_player and self.human_player in self.current_players:
            msg = f'\n' \
                  f'Your hand\n' \
                  f'{self.human_player.hand}\n' \
                  f'Meld: {self.human_player.meld}'
            self.print(msg)

    def take_cards(self):
        self.log_state(f'WAITING FOR PLAYER {self.high_bidder.partner.index} TO PASS CARDS', save_state=False)
        from_partner = self.high_bidder.partner.pass_cards(self.n_cards_to_pass)
        self.high_bidder.take_cards(from_partner)
        if self.high_bidder is self.human_player:
            self.print('New meld: ', self.high_bidder.meld)
        self.log_state('TAKE CARDS')

    def give_cards(self):
        self.log_state(f'WAITING FOR PLAYER {self.high_bidder.index} TO PASS CARDS', save_state=False)
        to_partner = self.high_bidder.pass_cards(self.n_cards_to_pass)
        self.high_bidder.partner.take_cards(to_partner)
        self.log_state('GIVE CARDS')

    def pass_cards(self):
        self.take_cards()
        self.high_bidder_chooses_meld()
        self.give_cards()

    def high_bidder_chooses_meld(self):
        # Todo: select meld, save cards used in meld, do not discard meld
        pass

    def declare_meld(self):
        for player in self.current_players:
            player.meld.set_trump(self.trump)
            self.melds[player] = player.meld.final
            # Todo: need to store list of meld cards in state

        self.log_state('DECLARE MELD')

    def update_current_players(self):
        """
        Locates the current players out of the player pool and
        rotates player order each hand so the bid order changes.
        """
        # Find and order current players
        n, N = self.n_players, len(self.players)
        self.current_players = [self.players[i % N] for i in range(self.hand_count, self.hand_count + n)]
        for player in self.current_players:
            player.reset_hand_state()

    def bidding_process(self):
        # If no one bids, then the bid gets dropped on the last bidder
        start_bid_amt = self.minimum_bid_amt - self.bid_increment_amt
        self.high_bid = start_bid_amt
        self.high_bidder = self.current_players[-1]
        passed = {player: False for player in self.current_players}

        # Everyone keeps bidding until everyone passes except one person
        idx = 0
        n_players = len(self.current_players)
        while sum(passed.values()) < n_players - 1:
            player = self.current_players[idx]
            if not passed[player]:
                self.log_state(f'WAITING ON PLAYER {player.index} TO BID', save_state=False)
                self.player_bids(player, passed)

            idx = (idx + 1) % n_players

        # Check to see if the bid was dropped
        if self.high_bid == start_bid_amt:
            self.high_bid = self.dropped_bid_amt
            self.dropped_bid = True
            self.log_state(f'BID DROPPED ON PLAYER {self.high_bidder.index}')
            self.print(f'The bid was dropped on {self.high_bidder}')

        self.print(self.high_bidder, 'took the bid at', self.high_bid)

    def player_bids(self, player: PinochlePlayer, player_has_passed: dict):

        def bid_too_small(bid):
            return bid <= self.high_bid

        def bid_not_increment(bid):
            return bid % self.bid_increment_amt != 0

        this_bid = player.place_bid(self.high_bid, self.bid_increment_amt)
        if isinstance(player, HumanPinochlePlayer) and this_bid is not None:
            while bid_too_small(this_bid) or bid_not_increment(this_bid):
                if bid_too_small(this_bid):
                    print('Bid is too small')
                elif bid_not_increment(this_bid):
                    print('Bid is not a valid increment')
                this_bid = player.place_bid(self.high_bid, self.bid_increment_amt)

        if this_bid:
            self.high_bid = this_bid
            self.high_bidder = player
            self.log_state(f'PLAYER {player.index} BID {this_bid}')
        else:
            player_has_passed[player] = True
            self.log_state(f'PLAYER {player.index} PASSED')

    def set_lead_player(self):
        leader = self.trick_winner or self.high_bidder
        lead_idx = self.current_players.index(leader)
        n = len(self.current_players)
        self.current_players = [self.current_players[(lead_idx + i) % n] for i in range(n)]
        leader.is_high_bidder = True

        self.print(str(self.current_players[0]), 'is leading')
        self.log_state(f'PLAYER {leader.index} IS LEADING', save_state=False)

    def set_partners(self):
        self.current_players[0].partner = self.current_players[2]
        self.current_players[2].partner = self.current_players[0]
        self.current_players[1].partner = self.current_players[3]
        self.current_players[3].partner = self.current_players[1]
        self.log_state('SET PARTNERS')

    def set_position(self):
        lead_idx = self.high_bidder.index
        n_players = len(self.current_players)
        positions = {
            lead_idx: 'high_bidder',
            ((lead_idx + 1) % n_players): 'left',
            ((lead_idx + 2) % n_players): 'forward',
            ((lead_idx + 3) % n_players): 'right',
        }
        for idx in range(lead_idx, lead_idx + n_players):
            cur_idx = idx % n_players
            self.current_players[cur_idx].position = positions[cur_idx]

        self.log_state('SET POSITION')

    def call_trump(self):
        self.log_state(f'WAITING ON PLAYER {self.high_bidder.index} TO CALL TRUMP', save_state=False)
        self.trump = self.high_bidder.choose_trump()
        self.print(f'Trump is {self.trump}')
        self.log_state('CALL TRUMP')

    def play_next_card(self, player: PinochlePlayer):

        msg = f'High bidder: {self.high_bidder}\n' \
              f'Trump: {self.trump}'
        #self.print(msg)

        self.log_state(f'WAITING ON PLAYER {player.index} TO PLAY CARD', save_state=False)
        card = player.play_card(self.trick)
        self.trick.add_card(card, player)

        self.cards_played.append((card, player))
        # Todo: update the shared state variables pertaining to cards

        self.log_state(f'PLAYER {player.index} PLAYS {card.to_str()}')

    def update_scores(self):

        # Give "last trick" points to the winner of the last trick
        self.trick_winner.took_last_trick = True

        # Count points of the high bidder and their partner
        bidder_counters = self.high_bidder.counters(self.last_trick_value)
        partner_counters = self.high_bidder.partner.counters(self.last_trick_value)
        counters = bidder_counters + partner_counters

        # Find out if the bid was saved or set
        meld = self.high_bidder.meld.total_meld_given_trump[self.trump]
        self.saved_bid = counters + meld >= self.high_bid

        # If we saved the bid, add points to score
        if self.saved_bid:
            score = counters + meld
            self.high_bidder.add_points(score)
            if self.partner_gets_points:
                partner = self.high_bidder.partner
                partner.add_points(partner.meld.calculate_meld_with_trump(self.trump))

            self.print(f'SAVED IT! Made {score} points')
            self.log_state(f'HAND RESULT: PLAYER {self.high_bidder.index} SAVED BID')

        # If the bid was set, remove points from score
        else:
            self.print('SET !!!')
            self.high_bidder.remove_points(self.high_bid)
            self.log_state(f'HAND RESULT: PLAYER {self.high_bidder.index} WAS SET')

    def play_hand(self):
        self.log_state('START HAND', save_state=False)
        self.start_next_hand()
        self.update_current_players()
        self.deal()

        self.log_state('START BIDDING PROCESS', save_state=False)
        self.bidding_process()
        self.log_state('END BIDDING PROCESS', save_state=False)

        self.set_partners()
        self.set_position()
        self.call_trump()
        self.pass_cards()
        self.declare_meld()

        self.log_state('START TRICKS', save_state=False)
        self.play_tricks()
        self.log_state('END TRICKS', save_state=False)

        self.update_scores()
        self.log_state('END HAND', save_state=False)

    def play_tricks(self):
        while self.high_bidder.hand:
            self.play_next_trick()

    def play_next_trick(self):
        self.set_lead_player()
        self.trick = Trick(self.n_players, self.trump)
        for player in self.current_players:
            self.play_next_card(player)

        self.trick_winner = self.trick.winner()
        self.trick_winner.tricks.append(self.trick)
        self.log_state(f'PLAYER {self.trick_winner.index} TOOK TRICK')

        msg = f'{str(self.trick)}\n' \
              f'----------------------------'
        self.print(msg)

    @property
    def remaining_trump(self):
        return sum(self.remaining_cards[self.trump].values())

    def player_index(self, player):
        return self.players.index(player)

    def player_cannot_beat(self, player: PinochlePlayer, card: Card):
        value_idx = Card.values.index(card.value)
        for idx in range(value_idx + 1, len(Card.values)):
            value = Card.values[idx]
            self.has_card[player][card.suit][value] = False

    def player_does_not_have_suit(self, player: PinochlePlayer, suit: str):
        self.has_suit[player][suit] = False
        for value in Card.values:
            self.has_card[player][suit][value] = False

    @staticmethod
    def best_card_in_trick(trick, trump) -> Optional[Card]:
        if not len(trick):
            return None

        best_card = trick.cards[0]
        for card in trick.cards[1:]:
            if card.suit is trump:
                if best_card.suit is not trump or card > best_card:
                    best_card = card
            elif card.suit is best_card.suit and card > best_card:
                best_card = card

        return best_card

    @staticmethod
    def card_can_beat_trick(trick: Trick, card: Card, trump: str) -> bool:
        if not trick.card_to_beat:
            return True
        elif card.suit is trump:
            if trick.card_to_beat.suit is not trump or card > trick.card_to_beat:
                return True
        elif card.suit is trick.card_to_beat.suit and card > trick.card_to_beat:
            return True
        return False

    @staticmethod
    def legal_plays(trick: Trick, hand: Hand, trump: str) -> List[Card]:

        # If this is the first card played, any card is legal
        if len(trick.cards) == 0:
            return hand.cards

        # Player must follow suit
        elif hand.has_suit(trick.leading_suit):
            if trick.trump_played and trump is not trick.leading_suit:
                return hand[trick.leading_suit]
            elif hand[trick.leading_suit][0] > trick.card_to_beat:
                return [card for card in hand[trick.leading_suit] if card > trick.card_to_beat]
            else:
                return hand[trick.leading_suit]

        # Player must trump if they cannot follow suit
        elif hand.has_suit(trump):
            if trick.trump_played and hand[trump][0] > trick.card_to_beat:
                return [card for card in hand[trump] if card > trick.card_to_beat]
            else:
                return hand[trump]

        # Player cannot trump or follow suit
        else:
            return hand.cards

    def player_can_take_trick(self, player: PinochlePlayer) -> bool:
        legal = self.legal_plays(self.trick, Hand.one_of_each(), self.trump)
        can_beat = self.card_can_beat_trick(self.trick, legal[0], self.trump)

        if self.has_suit[player][self.trick.leading_suit]:
            if self.trick.trump_played:
                return False
            elif self.trick.card_to_beat.value is 'A':
                return False

            value = self.trick.card_to_beat.value
            value_idx = Card.values.index(value)
            for idx in range(value_idx + 1, len(Card.values)):
                value = Card.values[idx]
                if self.has_card[player][self.trick.leading_suit][value]:
                    return True
            return False

        elif self.has_suit[player][self.trump]:
            # Todo: finish this method
            pass


    def likelihood_player_will_take_trick(self, player: PinochlePlayer) -> float:
        pass

    def player_has_played(self, player: PinochlePlayer) -> bool:
        return player in self.trick.card_players

    def next_player(self) -> PinochlePlayer:
        for player in self.current_players:
            if player not in self.trick.card_players:
                return player


class DoubleDeckPinochle(Pinochle):

    last_trick_value = 2
    deck_type = DoublePinochleDeck
    dropped_bid_amt = 50
    minimum_bid_amt = 60
    bid_increment_amt = 10

    def __init__(self, players=None, printing=False, logging=False):
        Pinochle.__init__(self, players, printing=printing, logging=logging)


class FirehousePinochle(DoubleDeckPinochle):

    deck_type = FirehousePinochleDeck
    n_players = 3
    n_cards_to_pass = 5

    def __init__(self, players=None, printing=False, logging=False):
        DoubleDeckPinochle.__init__(self, players, printing=printing, logging=logging)
        self.kitty = Kitty()

    def _deal_hands_to_players(self):
        for player in self.current_players:
            if not player.hand:
                player.take_cards(self.deck.deal_hand())

        self.kitty.take_cards(self.deck.deal_kitty())

    def set_partners(self):
        self.high_bidder.partner = self.kitty
        self.kitty.partner = self.high_bidder.partner

        idx = self.current_players.index(self.high_bidder) - 1
        self.current_players[idx].partner = self.current_players[idx - 1]
        self.current_players[idx - 1].partner = self.current_players[idx]

        self.log_state('SET PARTNERS')

    def set_position(self):
        lead_idx = self.current_players.index(self.high_bidder)
        n_players = len(self.current_players)
        positions = {
            lead_idx: 'high_bidder',
            ((lead_idx + 1) % n_players): 'back_seat',
            ((lead_idx + 2) % n_players): 'front_seat',
        }
        for idx in range(lead_idx, lead_idx + n_players):
            cur_idx = idx % n_players
            self.current_players[cur_idx].position = positions[cur_idx]

        self.log_state('SET POSITION')

    def set_include_partners_meld(self, value):
        pass

    def update_current_players(self):
        self.kitty.reset_hand_state()
        super().update_current_players()


def play_and_save_hands(game_type, players):
    the_game = game_type(players, logging=True)
    while True:
        score = the_game.play_hand()
        the_game.write_log_to_file(path='logs/hands')


def test():
    from time import time

    player_type = SimplePinochlePlayer
    players = [player_type('Alice', 100),
               player_type('Bob', 100),
               player_type('Charlie', 100),
               player_type('Dave', 100)]

    scores = []
    n_runs, count = 10000, 0
    start = time()
    for _ in range(n_runs):
        score = test_game(FirehousePinochle, players[:3])
        if score > 0:
            count += 1
            scores.append(score)

    print(' ')
    print('# of runs:', n_runs)
    print('Time: {} seconds'.format(round(time() - start, 1)))
    print('Average score:', round(sum(scores) / len(scores), 1) if scores else 0)
    print('Percent saved: {}%'.format(round(count / n_runs * 100.0, 1)))


def play():

    players = [HumanPinochlePlayer(),
               SimplePinochlePlayer('Bob', 100),
               SimplePinochlePlayer('Charlie', 100),
               SimplePinochlePlayer('Dave', 100)]

    play_and_save_hands(FirehousePinochle, players[:3])


if __name__ == "__main__":
    play()
