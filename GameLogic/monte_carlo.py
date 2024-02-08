import os
import sys
sys.path.append(os.path.abspath('./'))

from typing import Optional
import numpy as np

import matplotlib.pyplot as plt

from GameLogic.games import FirehousePinochle
from GameLogic.cards import Card, Hand
from GameLogic.players import PinochlePlayer


def test_bids_monto_carlo(
    hand: Hand,
    trump: str,
    bids: list,
    n_trials_per_bid: int,
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
    bids : list
        List of bids to use in simulations
    n_trials_per_bid : int
        The total number of trials (simulations) to run for each bid
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

    # Initialize the output lists
    saved_bids = []

    # Check for valid hand for bidding
    if not hand.has_marriage(trump):
        return saved_bids

    # Set up players
    if other_player_type is None:
        other_player_type = player_type

    player = player_type('P0')
    other_player_1 = other_player_type('P1')
    other_player_2 = other_player_type('P2')
    players = [player, other_player_1, other_player_2]

    # Create the game
    game = FirehousePinochle(players)

    # Remove the player's cards from the pinochle deck
    for card in hand.cards:
        game.deck.discard(card)

    # Start the simulation trials
    for bid in bids:
        for idx in range(n_trials_per_bid):

            # Set up the next hand
            game.start_next_hand()
            game.update_current_players()

            # Deal the cards to the remaining players
            # game.deal()
            game.deck.shuffle()
            player.take_cards(hand.cards)
            other_player_1.take_cards(game.deck.cards[0:25])
            other_player_2.take_cards(game.deck.cards[25:50])
            game.kitty.take_cards(game.deck.cards[50:55])

            # Calculate a random bid for the main player based on the meld value
            # game.bidding_process()
            game.high_bidder = player
            game.high_bid = bid
            game.trump = trump

            # Complete the hand
            game.set_partners()
            game.set_position()
            # game.call_trump()
            game.pass_cards()
            game.declare_meld()
            game.play_tricks()
            game.update_scores()

            if game.saved_bid:
                saved_bids.append(game.high_bid)

    return saved_bids


def plot_bid_bar_charts(saved_bids: dict, n_attempts_per_bid: int, log: bool = False):

    if len(saved_bids) == 0:
        print('No data found for plotting')
        return

    # Create the grid of plots
    fig, axs = plt.subplots(len(saved_bids), 1)
    colors = {
        'Spades': 'black',
        'Hearts': 'red',
        'Clubs': 'blue',
        'Diamonds': '#e75480',
    }

    # Flatten all plots into a list
    all_axes = axs.flat if len(saved_bids) > 1 else [axs]

    # Find the unique bids across all suits for consistent x-axis
    all_bids = set()
    for bids in saved_bids.values():
        all_bids.update(bids)
    all_bids = sorted(all_bids)

    # Find percentages for each bid
    suits, bids_by_suit, percentages_by_suit = [], [], []
    min_bid, max_bid = 1000, 0
    for suit in saved_bids:
        if len(saved_bids[suit]) == 0:
            continue

        unique_bids, counts = np.unique(saved_bids[suit], return_counts=True)
        suits.append(suit)
        bids_by_suit.append(unique_bids)
        percentages_by_suit.append(counts / n_attempts_per_bid)
        min_bid = min(min_bid, min(unique_bids))
        max_bid = max(max_bid, max(unique_bids))

    # Find maximum percentage across data
    max_percentage = 0.0
    for vals in percentages_by_suit:
        max_percentage = max(max_percentage, max(vals))

    # Plot the data
    for ax, suit, bids, win_percents in zip(all_axes, suits, bids_by_suit, percentages_by_suit):

        # Plot the data
        ax.bar(bids, win_percents, width=0.4, label='Won Bid %', alpha=0.6, color=colors[suit])

        # Customize the chart
        ax.set_title(suit)
        ax.legend()
        ax.set_xticks(all_bids)
        ax.set_xticklabels(all_bids)
        ax.set_xlim(min_bid - 5, max_bid + 5)
        ax.set_ylim(0.0, 1.1 * max_percentage)
        if log:
            ax.set_yscale('log')

    # Show the plots
    plt.tight_layout() # Adjust layout to not overlap
    plt.show()


def plot_bid_bar_chart_combined(saved_bids: dict, n_attempts_per_bid: int, log: bool = False):
    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Variables for plotting
    width = 0.2  # Width of each bar
    colors = {
        'Spades': 'black',
        'Hearts': 'red',
        'Clubs': 'blue',
        'Diamonds': '#e75480',
    }

    # Find the unique bids across all suits for consistent x-axis
    all_bids = set()
    for bids in saved_bids.values():
        all_bids.update(bids)
    all_bids = sorted(all_bids)

    # Map each unique bid to an x-axis position
    bid_positions = {bid: i for i, bid in enumerate(all_bids)}

    # Plot data for each suit
    i = 0
    for suit in Card.suits:
        bids = saved_bids.get(suit, [])
        if len(bids) == 0:
            continue

        unique_bids, counts = np.unique(bids, return_counts=True)
        percentages = counts / n_attempts_per_bid
        positions = [bid_positions[bid] + (i * width) for bid in unique_bids]

        ax.bar(positions, percentages, width=width, label=suit, alpha=0.6, color=colors[suit])

        # Increment chart counter
        i += 1

    # Customize the chart
    ax.set_title('Winning Bid Percentages by Suit')
    ax.legend()
    ax.set_xticks([pos + width for pos in range(len(all_bids))])
    ax.set_xticklabels(all_bids)
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
    from GameLogic.cards import FirehousePinochleDeck
    from GameLogic.players import RandomPinochlePlayer, SimplePinochlePlayer

    parser = ArgumentParser('Run the Monte Carlo bidding simulation')
    parser.add_argument('--bids', nargs='+', type=int, help='Bids to consider')
    parser.add_argument('--trials', type=int, default=100, help='Number of trials per suit per bid')
    parser.add_argument('--player', type=str, default='simple', choices=['simple', 'random'], help='Player type')
    parser.add_argument('--opponent', type=str, default='random', choices=['simple', 'random'], help='Opponent type')
    args = parser.parse_args()

    deck = FirehousePinochleDeck()
    deck.shuffle()
    hand = Hand(deck.deal()[0])

    standard_bids = list(range(60, 100, 5)) + list(range(100, 151, 10))

    print('Hand:')
    print(hand)

    player_types = {
        'simple': SimplePinochlePlayer,
        'random': RandomPinochlePlayer,
    }

    player_type = player_types[args.player]
    other_player_type = player_types[args.opponent]
    if not args.bids:
        args.bids = standard_bids

    '''
    min_bid, max_bid, bid_increment = 60, 150, 5
    bids = list(range(min_bid, max_bid + 1, bid_increment))
    '''

    saved_bids = {}
    for suit in Card.suits:
        if not hand.has_marriage(suit):
            continue

        saved_bids[suit] = test_bids_monto_carlo(
            hand,
            suit,
            args.bids,
            args.trials,
            player_type,
            other_player_type=other_player_type,
        )

        n_saved = len(saved_bids[suit])
        n_bids = args.trials * len(args.bids)
        percent = round(n_saved / n_bids * 100.0)
        print(f'{suit}: Saved {n_saved} out of {n_bids} bids [{percent}%]')

    plot_bid_bar_charts(saved_bids, args.trials)
    plot_bid_bar_chart_combined(saved_bids, args.trials)

    """
    Notes
    -----
    
    - Can set meld value manually in order to account for different meld
    - Can set bid value manually in order to test best trump suit
    
    """
