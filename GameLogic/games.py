import sys
import os
sys.path.append(os.path.abspath('./'))

from typing import Iterable, Optional

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


'''
class SharedKnowledge:

    def __init__(self, players):

        self._players = players
        self.scores = {p.id: p.score for p in self._players}
        for player in self._players:
            player.shared_knowledge = self
        
        self.hand_count = 0

        self.trump = None
        self.high_bid = None
        self.high_bidder = None
        self.current_bid = None

        self.trick = None
        self.best_card_in_trick = None
        self.trick_winner = None
        
        self.player_order = []
        self.tricks_taken = {p: [] for p in self._players}
        self.has_card = {p: {suit: {value: True for value in Card.values} for suit in Card.suits} for p in self._players}

    def new_hand(self):
        self.trump = None
        self.high_bid = None
        self.high_bidder = None
        self.current_bid = None
        self.player_order = []

        self.trick = None
        self.best_card_in_trick = None
        self.trick_winner = None
        
        self.tricks_taken = {p: [] for p in self._players}
        self.has_suit = {p: {suit: True for suit in Card.suits} for p in self._players}
        self.has_card = {p: {suit: {value: True for value in Card.values} for suit in Card.suits} for p in self._players}
    
    def player_cannot_beat(player: PinochlePlayer, card: Card):
        value_idx = Card.values.index(card.value)
        for idx in range(value_idx + 1, len(Card.values)):
            value = Card.values[idx]
            self.has_card[player][card.suit][value] = False
    
    def player_does_not_have_suit(player: PinochlePlayer, suit: str):
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
            if self.card_to_beat.suit is not trump or card > self.card_to_beat:
                return True
        elif card.suit is self.card_to_beat.suit and card > self.card_to_beat:
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
                return [card for card in suit if card > trick.card_to_beat]
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
    
    def player_can_take_trick(player: PinochlePlayer) -> bool:
        legal = SharedKnowledge.legal_plays(Hand.one_of_each())
        can_beat = SharedKnowledge.card_can_beat_trick(self.trick, legal[0], self.trump)
        
        if self.has_suit[player][self.trick.leading_suit]:
            if self.trick.trump_played:
                return False
            elif self.trick.card_to_beat.value is 'A':
                return False
            
            value = self.trick.card_to_beat.value
            value_idx = Card.values.index(value)
            for idx in range(value_idx + 1, len(Card.values)):
                value = Card.values[idx]
                if self.has_card[player][suit][value]:
                    return True
            return False
                
        elif self.has_suit[player][self.trump]:
        
    
    def likelihood_player_will_take_trick(player: PinochlePlayer) -> float:
        pass
    
    def player_has_played(player: PinochlePlayer) -> bool:
        return player in self.trick.card_players
    
    def next_player() -> PinochlePlayer:
        for player in self.player_order:
            if player not in trick.card_players:
                return player
'''


class Pinochle:

    last_trick_value = 1
    deck_type = PinochleDeck
    dropped_bid_amt = 25
    minimum_bid_amt = 30
    bid_increment_amt = 5
    n_players = 4
    n_cards_to_pass = 3
    n_tricks = 12

    def __init__(self, players=None, winning_score=None):
        self.deck = self.deck_type()
        self.players = players or []

        self.hand_count = -1

        self.trump = None
        self.high_bid = 0
        self.high_bidder = None
        self.current_players = []
        self.human_player = self.find_human_player()

        self.winning_score = winning_score
        self.partner_gets_points = False

        self._printing = False

    @property
    def printing(self):
        return self._printing or self.human_player is not None

    @printing.setter
    def printing(self, value):
        self._printing = value

    def get_state(self):
        return {
            'player_states': [p.get_state() for p in self.players],
            'game_type': self.__class__.__name__,
            'deck_type': self.deck_type.__name__,
            'rule_set': 'default',
            'hand_state': self.get_hand_state(),
            'last_trick_value': self.last_trick_value,
            'dropped_bid_amt': self.dropped_bid_amt,
            'minimum_bid_amt': self.minimum_bid_amt,
            'bid_increment_amt': self.bid_increment_amt,
            'n_players': self.n_players,
            'n_cards_to_pass': self.n_cards_to_pass,
            'n_tricks': self.n_tricks,
        }

    def get_hand_state(self):
        return {
            'player_hands': [p.hand for p in self.players],
            'player_melds': [p.meld for p in self.players],
            #'record_of_tricks': self.tricks, # Todo: do some refactoring
            #'record_of_bids': self.bids,
            #'initial_kitty': self.initial_kitty,
            #'final_kitty': self.final_kitty,
            'trump': self.trump,
            'high_bid': self.high_bid,
            'high_bidder': self.high_bidder,
            'dropped_bid': self.dropped_bid_amt,
        }

    def play_to(self, winning_score):
        self.winning_score = winning_score

    def set_include_partners_meld(self, value):
        self.partner_gets_points = value

    def deal(self):
        hands = self.deck.deal()
        self.current_players[0].take_cards(hands[0])
        self.current_players[1].take_cards(hands[1])
        self.current_players[2].take_cards(hands[2])
        self.current_players[3].take_cards(hands[3])

    def find_human_player(self):
        for player in self.players:
            if isinstance(player, HumanPinochlePlayer):
                return player

    def show_human_hand_and_meld(self):
        if self.human_player and self.human_player in self.current_players:
            print(' ')
            print('Your hand')
            print('...')
            print(self.human_player.hand)
            print('Meld: ', self.human_player.meld)

    def pass_cards(self):
        from_partner = self.high_bidder.partner.discard(self.n_cards_to_pass)
        self.high_bidder.take_cards(from_partner)
        if self.high_bidder is self.human_player:
            print('New meld: ', self.high_bidder.meld)
        to_partner = self.high_bidder.discard(self.n_cards_to_pass)
        self.high_bidder.partner.take_cards(to_partner)

    def update_current_players(self):
        """
        Locates the current players out of the player pool and
        rotates player order each hand so the bid order changes.
        """
        # Find and order current players
        n, N = self.n_players, len(self.players)
        self.current_players = [self.players[i % N] for i in range(self.hand_count, self.hand_count + n)]
        for player in self.current_players:
            player.start_new_hand()

    def bid(self):
        # If no one bids, then the bid gets dropped on the last bidder
        game_type = type(self)
        self.high_bid = game_type.minimum_bid_amt - game_type.bid_increment_amt
        self.high_bidder = self.current_players[-1]
        passed = {player: False for player in self.current_players}

        # Everyone keeps bidding until everyone passes except one person
        while sum(passed.values()) < len(self.current_players) - 1:
            for player in self.current_players:
                if not passed[player]:
                    this_bid = player.place_bid(self.high_bid, game_type.bid_increment_amt)
                    if this_bid:
                        self.high_bid = this_bid
                        self.high_bidder = player
                    else:
                        passed[player] = True

    def begin_next_hand(self):
        self.update_current_players()
        self.hand_count += 1

    def set_lead_player(self, player):
        lead_idx = self.current_players.index(player)
        n = len(self.current_players)
        self.current_players = [self.current_players[(lead_idx + i) % n] for i in range(n)]
        player.is_high_bidder = True

    def set_partners(self):
        self.current_players[0].partner = self.current_players[2]
        self.current_players[2].partner = self.current_players[0]
        self.current_players[1].partner = self.current_players[3]
        self.current_players[3].partner = self.current_players[1]

    def play_hand(self):
        self.begin_next_hand()
        self.deck.shuffle()
        self.deal()
        self.show_human_hand_and_meld()
        self.bid()
        self.set_lead_player(self.high_bidder)
        self.set_partners()

        if self.printing:
            print(' ')
            print('Beginning hand #{}'.format(self.hand_count))
            print(self.high_bidder, 'took the bid at', self.high_bid)

        self.trump = self.high_bidder.choose_trump()
        self.pass_cards()

        if self.printing:
            print('Trump is', self.trump)

        trick_winner = None
        while self.high_bidder.hand:

            if self.printing:
                print(str(self.current_players[0]), 'is leading')

            trick = Trick(self.n_players, self.trump)
            for player in self.current_players:
                card = player.play_card(trick)
                trick.add_card(card, player)

            trick_winner = trick.winner()
            trick_winner.tricks.append(trick)
            self.set_lead_player(trick_winner)

            if self.printing:
                print(str(trick))
                print('---------------------------')

        # Add points for last trick
        trick_winner.took_last_trick = True

        counters = self.high_bidder.counters(self.last_trick_value) + \
                   self.high_bidder.partner.counters(self.last_trick_value)
        meld = self.high_bidder.meld.total_meld_given_trump[self.trump]
        if counters + meld < self.high_bid:
            if self.printing:
                print('SET !!!')
            self.high_bidder.remove_points(self.high_bid)
            return -meld
        else:
            points = counters + meld
            if self.printing:
                print('SAVED IT !!!')
                print('Made {} points'.format(points))
            self.high_bidder.add_points(points)
            if self.partner_gets_points:
                partner = self.high_bidder.partner
                partner.add_points(partner.meld.calculate_meld_with_trump(self.trump))
            return points


class DoubleDeckPinochle(Pinochle):

    last_trick_value = 2
    deck_type = DoublePinochleDeck
    dropped_bid_amt = 50
    minimum_bid_amt = 60
    bid_increment_amt = 10
    n_tricks = 20

    def __init__(self, players=None, winning_score=None):
        Pinochle.__init__(self, players, winning_score)


class FirehousePinochle(DoubleDeckPinochle):

    deck_type = FirehousePinochleDeck
    n_players = 3
    n_cards_to_pass = 5
    n_tricks = 25

    def __init__(self, players=None, winning_score=None):
        DoubleDeckPinochle.__init__(self, players, winning_score)
        self.kitty = Kitty()
        self.initial_kitty = None
        self.final_kitty = None

    def get_hand_state(self):
        return {
            **super().get_hand_state(),
            'initial_kitty': self.initial_kitty,
            'final_kitty': self.final_kitty,
        }

    def deal(self, shuffle=True):
        hands = self.deck.deal()
        self.current_players[0].take_cards(hands[0])
        self.current_players[1].take_cards(hands[1])
        self.current_players[2].take_cards(hands[2])
        self.kitty.take_cards(hands[3])

    def set_partners(self):
        self.high_bidder.partner = self.kitty
        self.kitty.partner = self.high_bidder.partner

        idx = self.current_players.index(self.high_bidder) - 1
        self.current_players[idx].partner = self.current_players[idx - 1]
        self.current_players[idx - 1].partner = self.current_players[idx]

    def set_include_partners_meld(self, value):
        pass

    def update_current_players(self):
        self.kitty.start_new_hand()
        super().update_current_players()


def test_game(game_type, players):
    the_game = game_type(players)
    return the_game.play_hand()


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

    test_game(FirehousePinochle, players[:3])


if __name__ == "__main__":
    play()
