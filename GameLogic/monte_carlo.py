import os
import sys
sys.path.append(os.path.abspath('./'))

from typing import Optional, List
import numpy as np

import matplotlib.pyplot as plt

from GameLogic.games import (
    Pinochle,
    DoubleDeckPinochle,
    FirehousePinochle,
)
from GameLogic.cards import (
    Card,
    Hand,
    PinochleDeck,
    DoublePinochleDeck,
    FirehousePinochleDeck,
)
from GameLogic.players import (
    PinochlePlayer,
    RandomPinochlePlayer,
    SimplePinochlePlayer,
)
from GameLogic.meld import Meld


def test_hand_monto_carlo(
    hand: Hand,
    trump: str,
    n_trials: int,
    player_type: type,
    other_player_type: Optional[type] = None,
):
    """
    Test the given human hand in a Monte Carlo-type simulation.

    For a given human hand, run through some number of trials.
    For each trial, choose a random bid amount by sampling from
    a normal distribution with a mean equal to the players meld
    plus 20 and a standard deviation of 15. The bid must be
    greater than the specified minimum bid amount.

    A list of all bids is returned as well as a list of all bid
    amounts that the player managed to save.

    Parameters
    -----
    hand : Hand
        The hand to be tested
    trump : str
        The suit to choose for trump in running the trials
    n_trials : int
        The total number of trials (simulations) to run
    player_type : type[PinochlePlayer]
        Determines the algorithm to use to make decisions for the
        main player
    other_player_type : type[PinochlePlayer]
        Determines the algorithm to use to make the decisions
        for the other players in the simulation trials

    Returns
    -----
    list[int]
        List of bid amounts where the player saved the bid
    """

    # Check for valid hand for bidding
    if not hand.has_marriage(trump):
        return [], []

    # Initialize the output lists
    counters = [None] * n_trials
    meld = [None] * n_trials

    # Set up players
    if other_player_type is None:
        other_player_type = player_type

    player = player_type('P0')
    other_player_1 = other_player_type('P1')
    other_player_2 = other_player_type('P2')
    players = [player, other_player_1, other_player_2]

    # Create the game
    game = FirehousePinochle(players)

    # Preset the values to stay constant for all trials
    game.preset_bid = 0
    game.preset_bidder = player
    game.preset_trump = trump
    game.preset_player_hands[player] = hand

    # Play the hands
    for idx in range(n_trials):
        game.play_hand()

        # Record the outcome
        counters[idx] = player.counters(game.last_trick_value)
        meld[idx] = player.meld.total_meld_given_trump[trump]

    return counters, meld


def plot_bar_charts(results: dict, label: str = 'Counts', log: bool = False):

    if len(results) == 0:
        print('No data found for plotting')
        return

    # Create the grid of plots
    fig, axs = plt.subplots(len(results), 1)
    colors = {
        'Spades': 'black',
        'Hearts': 'red',
        'Clubs': 'blue',
        'Diamonds': '#b72450',
    }

    # Flatten all plots into a list
    all_axes = axs.flat if len(results) > 1 else [axs]

    # Find the min and max bounds for x-axis and y-axis
    suits, values_by_suit, counts_by_suit = [], [], []
    min_val, max_val = 10_000, 0
    max_count = 0
    for suit in results:
        if len(results[suit]) == 0:
            continue

        unique_vals, counts = np.unique(results[suit], return_counts=True)
        suits.append(suit)
        values_by_suit.append(unique_vals)
        counts_by_suit.append(counts)
        min_val = min(min_val, min(unique_vals))
        max_val = max(max_val, max(unique_vals))
        max_count = max(max_count, max(counts))

    # Plot the data
    for ax, suit, val, counts in zip(all_axes, suits, values_by_suit, counts_by_suit):

        # Plot the data
        ax.bar(val, counts, width=0.4, label=label, alpha=0.6, color=colors[suit])

        # Customize the chart
        ax.set_title(suit)
        ax.legend()
        ax.set_xlim(min_val, max_val)
        ax.set_ylim(0.0, 1.1 * max_count)
        if log:
            ax.set_yscale('log')

    # Show the plots
    plt.tight_layout() # Adjust layout to not overlap
    plt.show()


def plot_bar_chart_combined(results: dict, title: str = 'Counts per suit', log: bool = False):
    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Variables for plotting
    width = 0.2  # Width of each bar
    colors = {
        'Spades': 'black',
        'Hearts': 'red',
        'Clubs': 'blue',
        'Diamonds': '#b72450',
    }

    # Find the unique vals across all suits for consistent x-axis
    all_vals = set()
    for vals in results.values():
        all_vals.update(vals)
    all_vals = sorted(all_vals)

    # Map each unique val to an x-axis position
    positions_map = {val: i for i, val in enumerate(all_vals)}

    # Plot data for each suit
    i = 0
    for suit in Card.suits:
        vals = results.get(suit, [])
        if len(vals) == 0:
            continue

        unique_vals, counts = np.unique(vals, return_counts=True)
        positions = [positions_map[val] + (i * width) for val in unique_vals]

        ax.bar(positions, counts, width=width, label=suit, alpha=0.6, color=colors[suit])

        # Increment chart counter
        i += 1

    # Customize the chart
    ax.set_title(title)
    ax.legend()
    if log:
        ax.set_yscale('log')
    else:
        # Optional: Set a uniform y-axis limit if needed
        pass

    # Show the plot
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    from argparse import ArgumentParser
    parser = ArgumentParser('Run the Monte Carlo bidding simulation')
    parser.add_argument('--trials', type=int, default=1000, help='Number of trials per suit per bid')
    parser.add_argument('--player', type=str, default='simple', choices=['simple', 'random'], help='Player type')
    parser.add_argument('--opponent', type=str, default='random', choices=['simple', 'random'], help='Opponent type')
    args = parser.parse_args()

    hand = FirehousePinochleDeck.get_random_hand()

    print('Hand:')
    print(hand)

    player_types = {
        'simple': SimplePinochlePlayer,
        'random': RandomPinochlePlayer,
    }

    player_type = player_types[args.player]
    other_player_type = player_types[args.opponent]

    counters = {}
    meld = {}
    for suit in Card.suits:
        if not hand.has_marriage(suit):
            continue

        counters[suit], meld[suit] = test_hand_monto_carlo(
            hand,
            suit,
            args.trials,
            player_type,
            other_player_type=other_player_type,
        )

        min_counters = min(counters[suit])
        max_counters = max(counters[suit])
        sum_counters = sum(counters[suit])
        n_counters = len(counters[suit])

        mean_counters = round(sum_counters / n_counters, 2)
        dev_counters = sum([abs(mean_counters - x) for x in counters[suit]])
        std_counters = round(dev_counters / n_counters, 2)

        print(f'{suit} counter stats: min={min_counters}, max={max_counters}, mean={mean_counters}, std={std_counters}')

    plot_bar_charts(counters, label='Counters')
    #plot_bar_charts(meld, label='Meld')
    if len(counters) > 1:
        plot_bar_chart_combined(counters, title='Counters pulled per suit')
        #plot_bar_chart_combined(meld, title='Meld per suit')

    """
    Notes
    -----
    
    - Can set meld value manually in order to account for different meld
    - Can set bid value manually in order to test best trump suit
    
    """
