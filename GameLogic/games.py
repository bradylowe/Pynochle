from GameLogic.cards import PinochleDeck, DoublePinochleDeck, FirehousePinochleDeck
from GameLogic.ledgers import PinochleLedger
from GameLogic.players import PinochlePlayer, AutoPinochlePlayer, HumanPinochlePlayer


class Trick:

    def __init__(self, trump):
        self.trump = trump
        self.cards = []
        self.card_to_beat = None
        self.trump_played = False
        self.card_player = {}

    @property
    def leading_card(self):
        return self.cards[0] if len(self.cards) else None

    @property
    def leading_suit(self):
        return self.leading_card.suit if len(self.cards) else None

    @property
    def n_cards_played(self):
        return len(self.cards)

    def has_played(self, player):
        return player in self.card_player.values()

    def next_play(self, player):
        card = player.play_card(self)
        print(player, 'plays', card)
        self.add_card(card)
        self.card_player[card] = player

    def add_card(self, card):
        self.cards.append(card)

        if not self.card_to_beat:
            self.card_to_beat = card
        elif card.suit is self.trump:
            if self.card_to_beat.suit is not self.trump or card > self.card_to_beat:
                self.card_to_beat = card
        elif card.suit is self.card_to_beat.suit and card > self.card_to_beat:
            self.card_to_beat = card

        if card.suit == self.trump:
            self.trump_played = True

    def can_beat_winning_card(self, cards):
        """This method assumes that 'cards' is already in the appropriate suit"""
        if self.card_to_beat is None:
            return cards
        else:
            return [card for card in cards if card > self.card_to_beat]

    def legal_plays(self, hand):

        if len(self.cards) == 0:
            return hand.cards
        elif hand.has_suit(self.leading_suit):
            if self.trump_played and self.trump != self.leading_suit:
                return hand[self.leading_suit]
            else:
                return self.can_beat_winning_card(hand[self.leading_suit]) or hand[self.leading_suit]
        elif hand.has_suit(self.trump):
            if self.trump_played:
                return self.can_beat_winning_card(hand[self.trump]) or hand[self.trump]
            else:
                return hand[self.trump]
        else:
            return hand.cards

    def counters(self):
        return sum([1 for card in self.cards if PinochleDeck.is_counter(card)])

    def winner(self):
        for card in self.cards:
            if card == self.card_to_beat:
                return self.card_player[card]

    def have_played(self):
        return list(self.card_player.values())

    def __str__(self):
        return ' | '.join([str(card) for card in self.cards])


class Pinochle:

    last_trick_value = 1
    deck = PinochleDeck()
    dropped_bid = 25
    minimum_bid = 30
    minimum_bid_increment = 5
    n_players_per_hand = 4
    n_cards_to_pass = 3

    def __init__(self, players=None, ledger=None, winning_score=None):
        self.players = players or []
        self.ledger = ledger or PinochleLedger()

        self.hand_count = 0

        self.trump = None
        self.high_bid = 0
        self.high_bidder = None
        self.current_players = []
        self.human_player = None

        self.winning_score = winning_score
        self.partner_gets_points = False

        self._printing = False

        self.game_type = type(self)

    @property
    def printing(self):
        return self._printing or self.human_player is not None

    @printing.setter
    def printing(self, value):
        self._printing = value

    def play_to(self, winning_score):
        self.winning_score = winning_score

    def set_include_partners_meld(self, value):
        self.partner_gets_points = value

    def deal(self):
        hands = self.deck.deal()
        self.current_players[0].new_hand(hands[0])
        self.current_players[1].new_hand(hands[1])
        self.current_players[2].new_hand(hands[2])
        self.current_players[3].new_hand(hands[3])

    def show_human_hand_and_meld(self):
        if self.human_player:
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
        # Find and order current players
        n, N = self.n_players_per_hand, len(self.players)
        self.current_players = [self.players[i % N] for i in range(self.hand_count, self.hand_count + n)]
        for player in self.current_players:
            player.reset()

        # Find human player
        self.human_player = None
        for player in self.current_players:
            if isinstance(player, HumanPinochlePlayer):
                self.human_player = player
                break

    def bid(self):
        # If no one bids, then the bid gets dropped on the last bidder
        game_type = type(self)
        current_bid = game_type.minimum_bid - game_type.minimum_bid_increment
        current_high_bidder = self.current_players[-1]
        passed = {player: False for player in self.current_players}

        # Everyone keeps bidding until everyone passes except one person
        while sum(passed.values()) < len(self.current_players) - 1:
            for player in self.current_players:
                this_bid = player.place_bid(current_bid, game_type.minimum_bid_increment)
                if this_bid:
                    current_bid = this_bid
                    current_high_bidder = player
                else:
                    passed[player] = True

        return current_high_bidder, current_bid

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
        self.high_bidder, self.high_bid = self.bid()
        self.set_lead_player(self.high_bidder)
        self.set_partners()

        if self.printing:
            print(' ')
            print('Beginning hand #{}'.format(self.hand_count))
            print(self.high_bidder, 'took the bid at', self.high_bid)

        self.trump = self.high_bidder.call_trump()
        self.pass_cards()

        if self.printing:
            print('Trump is', self.trump)

        trick_winner = None
        while self.high_bidder.hand:

            trick = Trick(self.trump)
            for player in self.current_players:
                trick.next_play(player)

            trick_winner = trick.winner()
            trick_winner.add_counters(trick.counters())
            self.set_lead_player(trick_winner)

            if self.printing:
                print(str(trick))
                print('---------------------------')

        # Add points for last trick
        trick_winner.add_counters(self.last_trick_value)

        counters = self.high_bidder.counters + self.high_bidder.partner.counters
        meld = self.high_bidder.meld.meld_with_trump[self.trump]
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
    deck = DoublePinochleDeck()
    dropped_bid = 50
    minimum_bid = 60
    minimum_bid_increment = 10

    def __init__(self, players=None, ledger=None, winning_score=None):
        Pinochle.__init__(self, players, ledger, winning_score)


class FirehousePinochle(DoubleDeckPinochle):

    deck = FirehousePinochleDeck()
    n_players_per_hand = 3
    n_cards_to_pass = 5

    def __init__(self, players=None, ledger=None, winning_score=None):
        DoubleDeckPinochle.__init__(self, players, ledger, winning_score)
        self.kitty = PinochlePlayer('Kitty')

    def deal(self, shuffle=True):
        hands = self.deck.deal()
        self.current_players[0].new_hand(hands[0])
        self.current_players[1].new_hand(hands[1])
        self.current_players[2].new_hand(hands[2])
        self.kitty.hand.set(hands[3])

    def pass_cards(self):
        self.high_bidder.take_cards(self.kitty.hand.cards)
        if isinstance(self.high_bidder, HumanPinochlePlayer):
            print('New meld: ', self.high_bidder.meld)
        self.kitty.hand.set(self.high_bidder.discard(self.n_cards_to_pass))

    def set_partners(self):
        high_bidder_idx = self.current_players.index(self.high_bidder)
        self.current_players[high_bidder_idx].partner = PinochlePlayer('')

        idx = high_bidder_idx - 1
        self.current_players[idx].partner = self.current_players[idx - 1]
        self.current_players[idx - 1].partner = self.current_players[idx]

    def set_include_partners_meld(self, value):
        assert not value, 'Bid-taker has no partner in Firehouse Pinochle'


def test_game(game_type, players):
    the_game = game_type(players)
    return the_game.play_hand()


def test():
    from time import time

    players = [AutoPinochlePlayer('Alice', 100),
               AutoPinochlePlayer('Bob', 100),
               AutoPinochlePlayer('Charlie', 100),
               AutoPinochlePlayer('Dave', 100)]

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
    print('Time: {}'.format(round(time() - start, 1)))
    print('Average score:', round(sum(scores) / len(scores), 1) if scores else 0)
    print('Percent saved: {}%'.format(round(count / n_runs * 100.0, 1)))


def play():

    players = [HumanPinochlePlayer(),
               AutoPinochlePlayer('Bob', 100),
               AutoPinochlePlayer('Charlie', 100),
               AutoPinochlePlayer('Dave', 100)]

    test_game(FirehousePinochle, players[:3])


if __name__ == "__main__":
    play()
