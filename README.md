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
