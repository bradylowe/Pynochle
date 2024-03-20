# Pynochle

***NOTE:* REPOSITORY UNDER DEVELOPMENT**

Play Pinochle online, against algorithms, in betting scenarios, all written in Python.

## Quick Start

Run `pip install -r requirements.txt` to install the necessary packages. 
Some packages may not be necessary for some users. For instance, `torch` 
is listed as a requirement and is used in the "NeuralNetModels" module.
Also, `PyQt5` is used in the "DesktopApp" module.

Most modules do not have much functionality at the moment. Only the 
"GameLogic" module is fully developed. 

Run `python GameLogic/games.py` to play on the command line.

## Game Play

Play Pinochle on the command line by running `python GameLogic/games.py`. 
This allows testing of the game logic as well as recording human-play 
examples to log files for use in training machine learning models.

You can modify the "games.py" file to play different styles of Pinochle or 
use different rule sets, toggle logging, etc.

Some supported functionality includes:

- Basic game logic
  * Supports single-deck partners Pinochle, double-deck partners Pinochle, and double-deck three-handed Firehouse Pinochle
  * Supports various game rules such as last trick value, minimum bid amount, bid increment amount, number of cards to pass, winning score
  * Definitions of cards, decks, players, game, meld, etc.
  * Calculation of meld (necessary for game play)
  * Calculation of legal plays (necessary for game play)
  * Calculation of points
  * Game-play of entire hand 
    * Deal, bid, call trump, pass cards, meld, play tricks, score
  * Command-line interface into the game
- Autoplay algorithms
  * `RandomPinochlePlayer` always passes on the bid and plays a random legal play for each card, passes random cards to partner
  * `SimplePinochlePlayer` will place bids when the minimum number of counters is required; avoids passing trump, aces, and meld cards; attempts to pay partner and avoid playing unnecessarily powerful cards
- Monte Carlo simulations (see dedicated section below)
- Advanced logging capabilities
  * Log each action along with the entire game state at each action
  * Restore game from saved state and resume game play
  * Access "public state" variables to maintain hidden information
- 

## Monte Carlo Simulations

Run Monte Carlo simulations by running `python GameLogic/monte_carlo.py`.
Use command line arguments to trigger different outcomes. Run 
`python GameLogic/monte_carlo.py -h` to see a description of possible 
input arguments.

Examples:

- `python GameLogic/monte_carlo.py --compare_players --player random --opponent random`
- `python GameLogic/monte_carlo.py --meld_analysis --trails 10000`
- `python GameLogic/monte_carlo.py --next_card --opponent simple`
- `python GameLogic/monte_carlo.py --best_suit`

## Machine Learning

One main goal of this repository is to facilitate the development of a 
super-human level Pinochle game play algorithm. This will likely be 
achieved using reinforcement learning agents. These agents may have 
simple (fully-connected) neural nets under the hood or may utilize 
something more sophisticated such as transformer networks.

Some simple models have been initialized to perform functions such as 
predicting the next card to play given a state, predicting the legal 
plays given the current state, or predicting the meld of the current 
hand in all 4 suits (assuming each suit were to be called trump).

## Desktop Application

A simple Qt application has been created which shows a single Pinochle 
card and allows the user to move this card around and look at it. 
The machine learning section is currently a higher priority.

## Web Application

The web app modules have been removed, but they could be developed at 
any time to allow a nice UX into the functionality of the game logic.
