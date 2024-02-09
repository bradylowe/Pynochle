import os
import pickle
import numpy as np
from torch.utils.data import Dataset as TorchDataset

from GameLogic.meld import Meld
from GameLogic.cards import DoublePinochleDeck, Card
from NeuralNetModels.PredictMeld.model import MeldPredictorTransformer


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
        self.hand_lengths = [20, 23, 25, 30]

    def build(self, filename, n_examples):

        examples = [None] * n_examples

        # Play and encode n tricks
        for idx in range(n_examples):
            self.deck.shuffle()
            n_cards = np.random.choice(self.hand_lengths)
            cards = self.deck.cards[:n_cards]
            meld = Meld(cards)

            tokens = [MeldPredictorTransformer.to_token(card) for card in cards]
            melds = tuple(meld.total_meld_given_trump[suit] for suit in Card.suits)
            examples[idx] = (tokens, melds)

        with open(filename, 'wb') as f:
            pickle.dump(examples, f)


class MeldDataset(TorchDataset):

    def __init__(self, filename, batch_size=1):
        super().__init__()
        self.batch_size = batch_size
        self.filename = filename
        with open(filename, 'rb') as f:
            self.examples = pickle.load(f)

    def __getitem__(self, index):
        return self.examples[index]

    def __len__(self):
        return len(self.examples)

    def __iter__(self):
        return DatasetIterator(self)


class DatasetIterator:
    """
    This class allows us to iterate through our dataset in batches.
    """

    def __init__(self, data):
        self._batch_size = data.batch_size
        self._examples = data.examples
        self._index = 0

    def __next__(self):
        length = len(self._examples)
        if self._index < length:
            end = self._index + self._batch_size
            if end > length:
                end = length
            inputs = [self._examples[idx][0] for idx in range(self._index, end)]
            outputs = [self._examples[idx][1] for idx in range(self._index, end)]
            self._index = end
            return inputs, outputs
        else:
            raise StopIteration


if __name__ == '__main__':

    from NeuralNetModels.PredictMeld import train_filename, test_filename

    from time import time
    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--n', type=int, default=10000, help='Build dataset with this many entries')
    parser.add_argument('--tags', type=str, nargs='+', help='Save the dataset with this tag in its filename')
    parser.add_argument('--split', type=float, default=0.2, help='Percentage of items to save to test dataset')
    args = parser.parse_args()

    builder = MeldDatasetBuilder()

    n_test = int(args.n * args.split)
    n_train = args.n - n_test

    train_tags = ['train'] + (args.tags if args.tags else [])
    test_tags = ['test'] + (args.tags if args.tags else [])

    if n_train:
        start = time()
        builder.build(train_filename, n_train)
        print('Calculated and wrote', n_train, 'data entries in', round(time() - start, 1), 'seconds')

    if n_test:
        start = time()
        builder.build(test_filename, n_test)
        print('Calculated and wrote', n_test, 'data entries in', round(time() - start, 1), 'seconds')
