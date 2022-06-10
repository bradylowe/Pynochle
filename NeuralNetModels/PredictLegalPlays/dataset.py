import os.path as osp
import numpy as np
import pandas as pd

from NeuralNetModels.dataset import DatasetBuilder, Dataset
from NeuralNetModels.encodings import SuitEncoding, CardEncoding
from NeuralNetModels.PredictLegalPlays.model import PredictLegalPlaysNet

from GameLogic.games import Trick
from GameLogic.cards import DoublePinochleDeck, Hand


class LegalPlaysDatasetBuilder(DatasetBuilder):
    """
    CARDS
    ---
    0-J♠  | 1-Q♠  | 2-K♠  | 3-10♠  | 4-A♠  | 5-J♥  | 6-Q♥  | 7-K♥   | 8-10♥  | 9-A♥
    10-J♣ | 11-Q♣ | 12-K♣ | 13-10♣ | 14-A♣ | 15-J♦ | 16-Q♦ | 17-K♦  | 18-10♦ | 19-A♦

    INPUTS
    ---
    - cards played in trick (REQUIRED)    list(3 cards)   = 60 neurons
    - trump suit (REQUIRED)               suit            = 4 neuron

    OUTPUTS
    ---
    - score for every card in deck (20 neurons)
    """

    def __init__(self):
        super().__init__()
        self.base_dir = osp.dirname(osp.abspath(__file__))

        # Set up the possible card values and build the one-hot encodings
        self.deck = DoublePinochleDeck()
        CardEncoding.build()

        # Set and check input/output neural net dimensions
        self.input_dim, self.output_dim = PredictLegalPlaysNet.input_dim, PredictLegalPlaysNet.output_dim
        indim = CardEncoding.n * 3 + SuitEncoding.n
        assert self.input_dim == indim, f'Input dimension should be {self.input_dim}, not {indim}'

        outdim = CardEncoding.n
        assert self.output_dim == CardEncoding.n, f'Output dimension should be {self.output_dim}, not {outdim}'

    def build(self, n, path=None, tags=None):
        # Create empty DataFrames of the proper size
        input = pd.DataFrame(np.empty((n, self.input_dim), dtype='uint8'))
        output = pd.DataFrame(np.empty((n, self.output_dim), dtype='uint8'))

        # Play and encode n tricks
        for idx in range(n):
            self.deck.shuffle()
            hands = [Hand(cards) for cards in self.deck.deal()]
            n_cards_played = np.random.randint(self.deck.n_players - 1)
            trump = hands[idx % self.deck.n_players].choose_random_suit()
            trick = Trick(trump)
            for hand_idx in range(n_cards_played):
                hand = hands[(idx + hand_idx) % self.deck.n_players]
                trick.add_card(trick.legal_plays(hand)[-1], None)

            input.loc[idx] = self.build_input(trick.cards, trump)
            output.loc[idx] = self.build_output(trick)

        # Write the data to file
        infile, outfile = self.build_filenames(n, path, tags)
        input.to_csv(infile, index=False)
        output.to_csv(outfile, index=False)
        return infile, outfile

    def build_input(self, cards_played_in_trick, trump):
        """
        Inputs:
        - Card1 [20 bits]
        - Card2 [20 bits]
        - Card3 [20 bits]
        - Trump [4 bits]
        Total input size:  64 bits
        """
        x = np.zeros(self.input_dim, dtype=int)
        for idx, card in enumerate(cards_played_in_trick):
            x[CardEncoding.n * idx : CardEncoding.n * (idx + 1)] = CardEncoding.one_hot[card]

        x[-SuitEncoding.n:] = SuitEncoding.one_hot[trump]
        return x

    def build_output(self, trick):
        """
        Calculate all possible legal plays and convert to one-hot encoding [20 bits]
        """
        legal_plays = trick.legal_plays(CardEncoding.unique)
        return np.sum([CardEncoding.one_hot[card] for card in legal_plays], axis=0)


class LegalPlaysDataset(Dataset):

    def __init__(self, filename, batch_size=1):
        super().__init__(filename, batch_size)
        self.inputs = self.inputs.float()
        self.outputs = self.outputs.float()


if __name__ == '__main__':

    from time import time
    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--n', type=int, default=1000, help='Build dataset with this many entries')
    parser.add_argument('--tags', type=str, nargs='+', help='Save the dataset with this tag in its filename')
    parser.add_argument('--split', type=float, default=0.2, help='Percentage of items to save to test dataset')
    args = parser.parse_args()

    builder = LegalPlaysDatasetBuilder()

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
