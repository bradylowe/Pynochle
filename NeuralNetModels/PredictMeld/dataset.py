import os
import sys
sys.path.append(os.path.abspath('./'))

import pickle
import numpy as np
from torch.utils.data import Dataset as TorchDataset

from GameLogic.meld import Meld
from GameLogic.cards import DoublePinochleDeck, Card
from NeuralNetModels.PredictMeld.model import MeldPredictorTransformer
from NeuralNetModels.dataset import DatasetIterator


class MeldDatasetBuilder:
    """
    CARDS (Vocabulary)
    ---
    0-J♠  | 1-Q♠  | 2-K♠  | 3-10♠  | 4-A♠  | 5-J♥  | 6-Q♥  | 7-K♥   | 8-10♥  | 9-A♥
    10-J♣ | 11-Q♣ | 12-K♣ | 13-10♣ | 14-A♣ | 15-J♦ | 16-Q♦ | 17-K♦  | 18-10♦ | 19-A♦

    INPUTS
    ---
    - list of cards in hand

    OUTPUTS
    ---
    - Meld value given Spades is trump
    - Meld value given Hearts is trump
    - Meld value given Clubs is trump
    - Meld value given Diamonds is trump
    """

    def __init__(self):
        super().__init__()
        self.deck = DoublePinochleDeck()

    def build(self, filename, n_examples, hand_length):

        hands = np.empty((n_examples, hand_length), dtype=int)
        melds = np.empty((n_examples, 4), dtype=int)

        # Play and encode n tricks
        for idx in range(n_examples):
            self.deck.shuffle()
            cards = self.deck.cards[:hand_length]
            meld = Meld(cards)

            hands[idx] = [MeldPredictorTransformer.to_token(card) for card in cards]
            melds[idx] = tuple(meld.total_meld_given_trump[suit] for suit in Card.suits)

        with open(filename, 'wb') as f:
            pickle.dump((hands, melds), f)


class MeldDataset(TorchDataset):

    def __init__(self, filename, batch_size=1):
        super().__init__()
        self.batch_size = batch_size
        self.filename = filename
        with open(filename, 'rb') as f:
            self.inputs, self.outputs = pickle.load(f)

    def __getitem__(self, index):
        return self.inputs[index], self.outputs[index]

    def __len__(self):
        return len(self.inputs)

    def __iter__(self):
        return DatasetIterator(self)


if __name__ == '__main__':

    from NeuralNetModels.PredictMeld import data_dir
    from NeuralNetModels import num_to_str
    from time import time
    import argparse
    parser = argparse.ArgumentParser(description='Build dataset for Meld prediction network')
    parser.add_argument('--filename', type=str, help='Output filename of dataset (.pkl)')
    parser.add_argument('--n', type=int, default=10000, help='Build dataset with this many entries')
    parser.add_argument('--cards', type=int, default=25, help='Number of cards per hand')
    args = parser.parse_args()

    builder = MeldDatasetBuilder()

    if not args.filename:
        args.filename = f'double_deck_{args.cards}_cards_{num_to_str(args.n)}_examples.pkl'

    filename = os.path.join(data_dir, args.filename)
    assert filename.endswith('.pkl'), 'Must be a pickle file (.pkl)'

    start = time()
    builder.build(filename, args.n, args.cards)
    print('Calculated and wrote', args.n, 'data entries in', round(time() - start, 1), 'seconds')
