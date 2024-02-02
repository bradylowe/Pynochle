import numpy as np

import matplotlib.pyplot as plt

from GameLogic.games import FirehousePinochle, Trick
from GameLogic.cards import Hand
from GameLogic.players import PinochlePlayer


def test_bids_monto_carlo(
    hand: Hand,
    trump: str,
    n_trials: int,
    other_player_type: type,
    min_bid: int = 0,
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
        The total number of trials (simulations) to run on the hand
    other_player_type : type[PinochlePlayer]
        Determines the algorithm to use to make the decisions
        in the simulation trials
    min_bid : int
        Minimum bid allowed

    Returns
    -----

    list[int]
        List of bid amounts where the player attempted to save the bid
    list[int]
        List of bid amounts where the player saved the bid
    """
    players = [other_player_type(f'P{idx}') for idx in range(FirehousePinochle.n_players)]
    game = FirehousePinochle(players)
    game.begin_next_hand()

    # Initialize the output lists
    bids, saved_bids = [], []

    # Remove the player's cards from the pinochle deck
    for player_card in hand.cards:
        for idx, deck_card in enumerate(game.deck.cards):
            if player_card == deck_card:
                del game.deck.cards[idx]
                break

    # Start the simulation trials
    for idx in range(n_trials):

        # Set up our players with the appropriate cards
        game.update_current_players()
        game.current_players[0].hand = hand.copy()

        # Shuffle and deal the remaining cards to remaining players
        game.deck.shuffle()
        game.current_players[1].take_cards(game.deck.cards[0:25])
        game.current_players[2].take_cards(game.deck.cards[25:50])
        game.kitty.take_cards(game.deck.cards[50:55])

        # Set the bid
        game.high_bidder = game.current_players[0]
        game.set_lead_player(game.high_bidder)
        game.set_partners()

        # Call trump and get cards from the kitty
        game.trump = trump
        game.pass_cards()

        # Calculate a random bid based on the meld value
        meld = game.current_players[0].meld.total_meld_given_trump[trump]
        mu = meld + 20
        sigma = np.sqrt(mu)
        game.high_bid = max(min_bid, int(sigma * np.random.randn() + mu))
        bids.append(game.high_bid)

        # Play the hand
        trick_winner = game.high_bidder
        while game.high_bidder.hand:

            trick = Trick(game.n_players, game.trump)
            for player in game.current_players:
                card = player.play_card(trick)
                trick.add_card(card, player)

            trick_winner = trick.winner()
            game.set_lead_player(trick_winner)

        # Add points for last trick
        trick_winner.took_last_trick = True

        # If the player saved the hand, increment the counter
        # for this bid amount
        counters = game.high_bidder.counters(game.last_trick_value) + \
                   game.high_bidder.partner.counters(game.last_trick_value)

        meld = game.high_bidder.meld.total_meld_given_trump[game.trump]
        if counters + meld >= game.high_bid:
            saved_bids.append(game.high_bid)

    return bids, saved_bids


def plot_bid_histograms(suits: list, bids: list, won_bids: list, bins: int = 50, log: bool = False):

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))  # Create 2x2 grid of subplots

    for ax, total_data, won_data, title in zip(axs.flat, bids, won_bids, suits):

        # Plot histogram for total bids
        ax.hist(total_data, bins=bins, alpha=0.6, label='Total Bids')
        # Plot histogram for won bids on the same axes
        ax.hist(won_data, bins=bins, alpha=0.6, label='Won Bids')

        ax.set_title(title)
        ax.legend()
        if log:
            ax.set_yscale('log')

    plt.tight_layout()  # Adjust layout to not overlap
    plt.show()


def plot_bid_bar_charts(suits: list, bids: list, won_bids: list, log: bool = True):
    fig, axs = plt.subplots(2, 2, figsize=(10, 8)) # Create 2x2 grid of subplots

    for ax, total_data, won_data, title in zip(axs.flat, bids, won_bids, suits):

        # Count for won bids
        won_bids, won_counts = np.unique(won_data, return_counts=True)
        # Count for total bids
        total_bids, total_counts = np.unique(total_data, return_counts=True)

        # Plot total bids
        ax.bar(total_bids - 0.2, total_counts, width=0.4, label='Total Bids', alpha=0.6)
        # Plot won bids
        ax.bar(won_bids + 0.2, won_counts, width=0.4, label='Won Bids', alpha=0.6)

        ax.set_title(title)
        ax.legend()
        if log:
            ax.set_yscale('log')

    plt.tight_layout() # Adjust layout to not overlap
    plt.show()


if __name__ == "__main__":
    from GameLogic.cards import FirehousePinochleDeck
    from GameLogic.players import RandomPinochlePlayer, SimplePinochlePlayer

    deck = FirehousePinochleDeck()
    deck.shuffle()
    hand = Hand(deck.deal()[0])

    n_trials = 3000

    print('Hand:')
    print(hand)

    min_bid = 0
    player_type = SimplePinochlePlayer
    suits = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    bids, saved_bids = [], []
    for suit in suits:
        these_bids, these_saved_bids = test_bids_monto_carlo(hand, suit, n_trials, player_type, min_bid=min_bid)
        bids.append(these_bids)
        saved_bids.append(these_saved_bids)

        print()
        print('-----------')
        print(suit)
        print(f'Player saved {len(these_saved_bids)} bids out of {n_trials} attemps')

    plot_bid_histograms(suits, bids, saved_bids)

    """
    Notes
    -----
    
    - Can set meld value manually in order to account for different meld
    - Can set bid value manually in order to test best trump suit
    
    """
