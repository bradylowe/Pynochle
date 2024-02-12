import os
import sys
sys.path.append(os.path.abspath('./'))

import json
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
    HumanPinochlePlayer,
)
from GameLogic.meld import Meld


# Variables for plotting
suit_colors = {
    'Spades': 'black',
    'Hearts': 'red',
    'Clubs': 'blue',
    'Diamonds': '#b72450',
}


def simulate_full_hand(
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
        ax.bar(val, counts, width=0.4, label=label, alpha=0.6, color=suit_colors[suit])

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

        ax.bar(positions, counts, width=width, label=suit, alpha=0.6, color=suit_colors[suit])

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


def plot_histogram_combined(results: dict, title: str = 'Counts per suit', bins: int = 35, log: bool = False):

    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Assuming the range and distribution of your data are known, adjust bins accordingly
    bins = np.linspace(min(min(results.values())), max(max(results.values())), bins)

    # Plot data for each suit
    for suit, color in suit_colors.items():
        vals = results.get(suit, [])
        if len(vals) == 0:
            continue

        ax.hist(vals, bins=bins, label=suit, alpha=0.6, color=color, edgecolor='black')

    # Customize the chart
    ax.set_title(title)
    ax.legend()
    if log:
        ax.set_yscale('log')

    # Show the plot
    plt.tight_layout()
    plt.show()


def plot_next_card_data(data):

    # Define the suits and card ranks of interest
    suits = ['Hearts', 'Spades', 'Clubs', 'Diamonds']
    ranks = ['A', '10', 'K', 'Q', 'J']

    # Initialize a 2x2 subplot grid
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Simulation Results by Suit')

    # Flatten the axes for easy iteration
    axs = axs.flatten()

    # Colors for different ranks (optional, for better visualization)
    colors = ['red', 'green', 'blue', 'orange', 'purple']

    # Loop over each suit to create a subplot
    for i, suit in enumerate(suits):
        ax = axs[i]
        ax.set_title(f'{suit}')

        # Filter data for the current suit and plot histograms
        for j, rank in enumerate(ranks):
            key = f'{rank} of {suit}'
            if key in data:
                ax.hist(data[key], bins=15, alpha=0.5, label=key, color=colors[j])

        # Enhance readability
        ax.legend()
        ax.set_xlabel('Outcome')
        ax.set_ylabel('Frequency')

        # Optional: Set the same scale for all subplots for direct comparison
        # ax.set_ylim([0, max_limit])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the layout to make room for the main title
    plt.show()


def compare_players(
    n_trials: int = 1000,
):
    """
    Compare the performance of all player types against all
    other player types with many runs on a single, random hand
    and plot the results

    Parameters
    ----------
    n_trials: int
        Number of trials to run per trump suit, per hand, per
        pairing of player types
    """

    hand = FirehousePinochleDeck.get_random_hand()
    print('Hand')
    print(hand)

    player_types = RandomPinochlePlayer, SimplePinochlePlayer
    for suit in Card.suits:
        if not hand.has_marriage(suit):
            continue

        results = {
            (player_type, opponent_type): None
            for player_type in player_types for opponent_type in player_types
        }

        for player_type in player_types:
            for opponent_type in player_types:
                counters, _ = simulate_full_hand(hand, suit, n_trials, player_type, opponent_type)
                results[(player_type, opponent_type)] = counters

        # Map names
        names = {
            RandomPinochlePlayer: 'Rand',
            SimplePinochlePlayer: 'Simp',
        }

        # Plot
        print()
        print(suit)
        fig, axs = plt.subplots(2, 2)
        all_axes = axs.flat
        for ax, (player_type, opponent_type), counters in zip(all_axes, results, results.values()):

            # Assuming the range and distribution of your data are known, adjust bins accordingly
            bins = np.linspace(min(counters), max(counters), 30)
            ax.hist(counters, bins=bins, label=suit, alpha=0.6, color=suit_colors[suit], edgecolor='black')

            # Customize the chart
            title = f'{names[player_type]} VS {names[opponent_type]}'
            ax.set_title(title)
            ax.legend()

            # Print the stats to console
            print(f'{title}: mean={np.mean(counters)}, std={np.std(counters)}')

        # Show the plot
        plt.tight_layout()
        plt.show()


def power_rank_meld_distributions(
    n_trials: int = 1000,
    deck_type: type = FirehousePinochleDeck,
):
    """
    Plot a distribution of the power, rank, and meld of
    many random hands and return the values

    Generate ``n_trials`` random hands and calculate the
    power, rank, and meld of each suit for each hand.
    Store all of these values in 3 lists, and then bin
    them into histograms and plot them.

    Parameters
    ----------
    n_trials: int
        Number of random hands to generate
    deck_type: type
        Type of :class:`PinochleDeck` to use. Options are
        :class:`PinochleDeck`,
        :class:`DoublePinochleDeck`, and
        :class:`FirehousePinochleDeck`.
        The default is :class:`FirehousePinochleDeck`.

    Returns
    -------
    list
        List of all power values seen
    list
        List of all meld values seen
    list
        List of all rank values seen

    Notes
    -----
    The plot will show all the data in Spades because the
    plotting function is expecting to plot a dictionary
    of suits, and we are flattening all the data out into
    a single suit because their distributions will not vary.
    """
    powers = [None] * n_trials * 4
    melds = [None] * n_trials * 4
    ranks = [None] * n_trials * 4
    for i in range(0, n_trials * 4, 4):
        hand = deck_type.get_random_hand()
        meld = Meld(hand)
        for j, suit in enumerate(Card.suits):
            powers[i + j] = meld.power[suit]
            melds[i + j] = meld.total_meld_given_trump[suit]
            ranks[i + j] = meld.rank[suit]

    plot_histogram_combined({'Spades': powers}, title='Suit Power')
    plot_histogram_combined({'Spades': melds}, title='Suit Meld')
    plot_histogram_combined({'Spades': ranks}, title='Suit Rank')

    return powers, melds, ranks


def choose_next_card(
    game_state: dict,
    n_trials: int,
    plot_results: bool = False,
) -> dict:
    """
    Run many simulations of a given game state starting from some
    point during the trick taking phase to gain insight into the
    most advantageous card to play next for the next player

    The simulation results show the total counters pulled at the
    end of each hand by the current player and their partner.

    A distribution is measured for each possible next legal play
    for the next player waiting to play a card. After playing the
    chosen card, all future plays of this player and the other
    players are made randomly.

    Parameters
    ----------
    game_state: dict
        A dictionary representing the game state
    n_trials: int
        Number of trials to run for each possible card play
    plot_results: bool
        If True, plot the distributions for each possible play

    Returns
    -------
    Dict[Card, dict]
        Results are returned as a dictionary with the possible
        plays (cards) as keys in basic string format.

        Each dictionary contains the 'mean' and 'std' of the
        distribution as well as the distribution data itself
        in a list called 'counters'.
    """

    game_state['human_player'] = None
    for idx in range(len(game_state['players'])):
        game_state['players'][idx]['player_type'] = RandomPinochlePlayer.__name__

    game = Pinochle.restore_state(game_state)
    if game.trick is None or game.trick.complete:
        game.set_up_trick()

    player = game.get_next_player()
    player_index = player.index
    unique_legal_plays = set(game.trick.legal_plays(player.hand))
    counters = {card.to_str(): [None] * n_trials for card in unique_legal_plays}

    for card in unique_legal_plays:
        for idx in range(n_trials):
            game = Pinochle.restore_state(game_state)

            if game.trick is None or game.trick.complete:
                game.set_up_trick()
            game.play_next_card(card)
            game.play_cards_in_trick()
            game.finish_trick()

            game.play_tricks()

            for player in game.current_players:
                if player.index == player_index:
                    mine = player.counters(game.last_trick_value)
                    partners = player.partner.counters(game.last_trick_value)
                    counters[card.to_str()][idx] = mine + partners
                    break

    if plot_results:
        plot_next_card_data(counters)

    results = {}
    for card in counters:
        results[card] = {
            'mean': np.mean(counters[card]),
            'std': np.std(counters[card]),
            'counters': counters[card],
        }
    return results

if __name__ == "__main__":

    from argparse import ArgumentParser
    parser = ArgumentParser('Run a Monte Carlo simulation')
    parser.add_argument('--compare_players', action='store_true', help='Compare player types based on counters pulled')
    parser.add_argument('--meld_analysis', action='store_true', help='Analyze power, rank, and meld distributions')
    parser.add_argument('--next_card', action='store_true', help='Look at the "next card" prediction distributions')
    parser.add_argument('--best_suit', action='store_true', help='Play a random hand, try calling each suit trump')

    parser.add_argument('--trials', type=int, default=1000, help='Number of trials per suit per bid')
    parser.add_argument('--player', type=str, default='simple', choices=['simple', 'random'], help='Player type')
    parser.add_argument('--opponent', type=str, default='random', choices=['simple', 'random'], help='Opponent type')
    args = parser.parse_args()

    player_types = {
        'simple': SimplePinochlePlayer,
        'random': RandomPinochlePlayer,
    }

    # Compare players head-to-head, show results, and exit
    if args.compare_players:
        compare_players(args.trials)
        exit()

    # Plot power, rank, and meld distributions, then exit
    if args.meld_analysis:
        power_rank_meld_distributions(args.trials)
        exit()

    # Generate distributions for the next card to play in a hand
    if args.next_card:
        with open('logs/game_state.json', 'r') as f:
            game_state = json.load(f)
        choose_next_card(game_state=game_state, n_trials=args.trials, plot_results=True)
        exit()

    # Try playing a random hand many times, and find out which suit is best for trump
    if args.best_suit:

        hand = FirehousePinochleDeck.get_random_hand()

        print('Hand:')
        print(hand)

        player_type = player_types[args.player]
        other_player_type = player_types[args.opponent]

        counters = {}
        meld = {}
        for suit in Card.suits:
            if not hand.has_marriage(suit):
                continue

            counters[suit], meld[suit] = simulate_full_hand(
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
            plot_histogram_combined(counters, title='Counters pulled per suit')
            #plot_histogram_combined(meld, title='Meld per suit')
            #plot_bar_chart_combined(meld, title='Meld per suit')

        exit()
