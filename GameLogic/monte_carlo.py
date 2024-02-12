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


def plot_data_by_suit(
    results: dict,
    title: str = 'Counts',
    x_min: float = None,
    x_max: float = None,
    same_range: bool = False,
    log: bool = False,
    combined: bool = False,
    chart_style: str = 'hist',
    bins: int = None,
):

    # Check for allowed style
    allowed_styles = ['hist', 'bar']
    if chart_style not in allowed_styles:
        raise ValueError(f'Chart style "{chart_style}" not allowed, must be {allowed_styles}')

    # Create the grid of plots
    if combined:
        fig, ax = plt.subplots(figsize=(10, 8))
        all_axes = [ax] * len(results)
        same_range = False  # This will happen automatically
    else:
        fig, axs = plt.subplots(len(results), 1)
        all_axes = axs.flat if len(results) > 1 else [axs]

    # Find the min and max bounds for x-axis and y-axis
    suits, values_by_suit, counts_by_suit = [], [], []
    y_min, y_max = 0.0, None
    x_min_calculated, x_max_calculated = 10_000, 0
    y_max_calculated = 0
    if same_range:
        for suit in results:
            if len(results[suit]) == 0:
                continue

            unique_vals, counts = np.unique(results[suit], return_counts=True)
            suits.append(suit)
            values_by_suit.append(unique_vals)
            counts_by_suit.append(counts)
            x_min_calculated = min(x_min_calculated, min(unique_vals))
            x_max_calculated = max(x_max_calculated, max(unique_vals))
            y_max_calculated = max(y_max_calculated, max(counts))

        # Give buffer for visual appeal
        if x_min is None:
            x_min = 0.9 * x_min_calculated
        if x_max is None:
            x_max = 1.1 * x_max_calculated
        if chart_style != 'hist':
            y_max = 1.1 * y_max_calculated

    # Plot the data
    n_suits = len(results)
    width = 1 / n_suits
    offsets = [width * (idx - (n_suits - 1) / 2) for idx in range(n_suits)]
    for ax, suit, offset in zip(all_axes, results, offsets):

        # Plot the data
        unique_values, counts = np.unique(results[suit], return_counts=True)
        if chart_style == 'hist':
            ax.hist(results[suit], bins=bins, label=suit, alpha=0.6, color=suit_colors.get(suit), edgecolor='black')
        elif chart_style == 'bar':
            values = unique_values + offset if combined else unique_values
            ax.bar(values, counts, width=0.4, label=suit, alpha=0.6, color=suit_colors.get(suit))

        # Customize the chart
        ax.set_title(title)
        ax.legend()
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        if log:
            ax.set_yscale('log')

    # Show the plots
    plt.tight_layout() # Adjust layout to not overlap
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

    plot_data_by_suit({'Counts': powers}, title='Suit Power')
    plot_data_by_suit({'Counts': melds}, title='Suit Meld')
    plot_data_by_suit({'Counts': ranks}, title='Suit Rank')

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

        # Plot the data
        if len(counters):
            plot_data_by_suit(counters, title='Counters', x_min=0, x_max=50, chart_style='bar')
            plot_data_by_suit(counters, title='Counters', x_min=0, x_max=50)
            plot_data_by_suit(meld, title='Meld')
            if len(counters) > 1:
                plot_data_by_suit(counters, title='Counters', x_min=0, x_max=50, combined=True, chart_style='bar')
                plot_data_by_suit(counters, title='Counters', x_min=0, x_max=50, combined=True)
                plot_data_by_suit(meld, title='Meld', combined=True)

        exit()
