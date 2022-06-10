import numpy as np
import pandas as pd
import torch
import os.path as osp

from NeuralNetModels.dataset import DatasetBuilder, Dataset
from NeuralNetModels.encodings import SuitEncoding, CardEncoding, PlayerEncoding, HandEncoding
from NeuralNetModels.PredictNextCard.model import PredictNextCard

from GameLogic.games import FirehousePinochle, Trick
from GameLogic.players import AutoPinochlePlayer


class NextCardDatasetBuilder(DatasetBuilder):
    """
    CARDS
    ---
    0-J♠  | 1-Q♠  | 2-K♠  | 3-10♠  | 4-A♠  | 5-J♥  | 6-Q♥  | 7-K♥   | 8-10♥  | 9-A♥
    10-J♣ | 11-Q♣ | 12-K♣ | 13-10♣ | 14-A♣ | 15-J♦ | 16-Q♦ | 17-K♦  | 18-10♦ | 19-A♦

    INPUTS
    ---
    Assuming 3 players, 4 suits, 20 distinct cards, 25 tricks

    - SEQUENCE OF (CARDS + CONTEXT) [n_tricks x 50 bits]
      * last_card [20 bits]
      * last_card_player [3 bits]
      * trump [4 bits]
      * high_bidder [3 bits]
      * current_player_hand [20 integers (representing a count for each unique card type)]


    OUTPUTS
    ---
    - next card to be played [1 integer]
    """

    def __init__(self):
        super().__init__()
        self.base_dir = osp.dirname(osp.abspath(__file__))

        self.game = FirehousePinochle([AutoPinochlePlayer(name) for name in ['A', 'B', 'C']])
        PlayerEncoding.build(self.game.players)
        CardEncoding.build()

        # Set and check input/output neural net dimensions
        self.input_dim, self.output_dim = PredictNextCard.input_dim, PredictNextCard.output_dim
        #        last card        last player        trump            cur player         cur options
        indim = CardEncoding.n + PlayerEncoding.n + SuitEncoding.n + PlayerEncoding.n + CardEncoding.n
        assert PredictNextCard.input_dim == indim, f'Input dimension should be {self.input_dim}, not {indim}'
        outdim = CardEncoding.n
        assert PredictNextCard.output_dim == CardEncoding.n, f'Output dimension should be {self.output_dim}, not {outdim}'

    def build(self, n, path=None, tags=None):
        # Calculate how many hands will be played and how many cards that is
        n_hands = int(n / self.game.n_tricks / PlayerEncoding.n)
        n = n_hands * self.game.n_tricks * PlayerEncoding.n

        # Create empty DataFrames of the proper size
        input = pd.DataFrame(np.empty((n, self.input_dim), dtype='uint8'))
        output = pd.DataFrame(np.empty((n, 1), dtype='uint8'))

        count = 0
        for _ in range(n_hands):
            # Start single hand
            self.game.begin_next_hand()
            self.game.deck.shuffle()
            self.game.deal()
            self.game.high_bidder, self.game.high_bid = self.game.bid()
            self.game.set_lead_player(self.game.high_bidder)
            self.game.set_partners()

            self.game.trump = self.game.high_bidder.call_trump()
            self.game.pass_cards()

            # Play the hand
            while self.game.high_bidder.hand:

                # Play this trick, record each card as it is played
                trick = Trick(self.game.trump)
                for player in self.game.current_players:
                    input.loc[count] = self.build_input(trick)
                    trick.next_play(player)
                    output.loc[count] = self.build_output(trick)
                    count += 1

                self.game.set_lead_player(trick.winner())

        # Write the data to file
        infile, outfile = self.build_filenames(n, path, tags)
        input.to_csv(infile, index=False)
        output.to_csv(outfile, index=False)
        return infile, outfile

    def build_input(self, trick):
        """
        Inputs:
        - Last card [20 bits]
        - Last player [3 bits]
        - Trump [4 bits]
        - Current player [3 bits]
        - Current player's card options [20 ints]
        Total size:  50 bits
        """
        x = np.zeros(self.input_dim, dtype=int)

        start_card, end_card = 0, CardEncoding.n
        start_player, end_player = end_card, end_card + PlayerEncoding.n
        start_trump, end_trump = end_player, end_player + SuitEncoding.n
        start_bidder, end_bidder = end_trump, end_trump + PlayerEncoding.n
        start_hand, end_hand = end_bidder, end_bidder + CardEncoding.n

        if trick:
            # Last card played
            card = trick.cards[-1]
            x[start_card: end_card] = CardEncoding.one_hot[card]

            # Player of last card played
            player = trick.card_players[-1]
            x[start_player: end_player] = PlayerEncoding.one_hot[player]
        else:
            player = self.game.current_players[0]

        # Trump, current player, cards available to current player
        x[start_trump: end_trump] = SuitEncoding.one_hot[self.game.trump]
        x[start_bidder: end_bidder] = PlayerEncoding.one_hot[self.game.high_bidder]
        x[start_hand: end_hand] = HandEncoding.counts(player.hand)
        return x

    def build_output(self, trick):
        """
        Integer index of next card to be played
        """
        return CardEncoding.idx[trick.cards[-1]]


class NextCardDataset(Dataset):

    def __init__(self, filename, batch_size=1):
        super().__init__(filename, batch_size)
        self.inputs = torch.tensor(self.expand_inputs(self.inputs), dtype=torch.float)
        self.outputs = torch.tensor(self.outputs, dtype=torch.long).flatten()

    @staticmethod
    def expand_inputs(x):
        n_tricks = FirehousePinochle.n_tricks
        expanded = np.empty((x.shape[0], n_tricks, x.shape[1]), dtype=np.uint8)
        expanded[:, n_tricks - 1, :] = x

        mask = np.zeros(len(x), dtype=bool)
        for idx in range(0, n_tricks-1):
            opposite_idx = n_tricks - idx - 2
            mask[idx::n_tricks] = True
            expanded[:, opposite_idx, :] = np.roll(x, idx+1, axis=0)
            expanded[mask, opposite_idx, :] = 0

        return expanded


if __name__ == '__main__':

    from time import time
    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--n', type=int, default=1000, help='Build dataset with this many entries')
    parser.add_argument('--tags', type=str, nargs='+', help='Save the dataset with this tag in its filename')
    parser.add_argument('--split', type=float, default=0.2, help='Percentage of items to save to test dataset')
    args = parser.parse_args()

    builder = NextCardDatasetBuilder()

    n_test = int(args.n * args.split)
    n_train = args.n - n_test

    train_tags = ['train'] + (args.tags if args.tags else [])
    test_tags = ['test'] + (args.tags if args.tags else [])

    if n_train:
        start = time()
        builder.build(n_train, tags=train_tags)
        print('Calculated and wrote', n_train, 'data entries in', round(time() - start, 1), 'seconds')

    if n_test:
        start = time()
        builder.build(n_test, tags=test_tags)
        print('Calculated and wrote', n_test, 'data entries in', round(time() - start, 1), 'seconds')
