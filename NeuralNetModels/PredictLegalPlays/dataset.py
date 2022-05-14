from time import time

import numpy as np
import pandas as pd

from NeuralNetModels.dataset import dataset_paths, test_loading_data
from NeuralNetModels.encodings import SuitEncoding, CardEncoding
from NeuralNetModels.PredictLegalPlays import base_dir

from GameLogic.games import Trick
from GameLogic.cards import Card, DoublePinochleDeck, Hand


# Set up the possible card values and build the one-hot encodings
Card.values = DoublePinochleDeck.values
CardEncoding.build()

input_dim = CardEncoding.n * DoublePinochleDeck.n_players + SuitEncoding.n
output_dim = CardEncoding.n


def build_input(cards_played_in_trick, trump):
    x = np.zeros(input_dim, dtype=int)

    for idx, card in enumerate(cards_played_in_trick):
        x[CardEncoding.n * idx : CardEncoding.n * (idx + 1)] = CardEncoding.one_hot[card]

    x[-SuitEncoding.n:] = SuitEncoding.one_hot[trump]
    return x


def build_dataset(n_entries, tag=''):
    infile, outfile = dataset_paths(n_entries, base_dir, tag)

    input = pd.DataFrame(np.empty((n_entries, input_dim), dtype='uint8'))
    output = pd.DataFrame(np.empty((n_entries, output_dim), dtype='uint8'))

    start = time()
    deck = DoublePinochleDeck()
    for idx in range(n_entries):
        deck.shuffle()
        hands = [Hand(cards) for cards in deck.deal()]
        n_cards_played = np.random.randint(deck.n_players - 1)
        trump = hands[idx % deck.n_players].choose_random_suit()
        trick = Trick(trump)
        for hand_idx in range(n_cards_played):
            hand = hands[(idx + hand_idx) % deck.n_players]
            trick.add_card(trick.legal_plays(hand)[-1])

        input.loc[idx] = build_input(trick.cards, trump)

        # Build correct output for neural net
        # Calculate all possible legal plays and convert to one-hot encoding
        legal_plays = trick.legal_plays(CardEncoding.unique)
        legal_plays_one_hot = np.sum([CardEncoding.one_hot[card] for card in legal_plays], axis=0)
        output.loc[idx] = legal_plays_one_hot

    print('Calculated', n_entries, 'data entries in', round(time() - start, 1), 'seconds')

    start = time()
    input.to_csv(infile, index=False)
    output.to_csv(outfile, index=False)
    print('Wrote', n_entries, 'to files in', round(time() - start, 1), 'seconds')


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--n', type=int, default=1000000, help='Build dataset with this many entries')
    parser.add_argument('--tag', type=str, help='Save the dataset with this tag in its filename')
    args = parser.parse_args()

    build_dataset(n_entries=args.n, tag=args.tag)
    test_loading_data(args.n, base_dir)
