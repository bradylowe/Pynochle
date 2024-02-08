from typing import List

import torch
import torch.nn as nn
import numpy as np

from GameLogic.cards import Card
from GameLogic.players import SimplePinochlePlayer

class DRLPinochlePlayer(SimplePinochlePlayer):

    input_dimensions = 10
    policy_hidden_layer_size = 32
    value_hidden_layer_size = 32
    output_dimensions = len(Card.suits) * len(Card.values)
    available_actions = {idx: card for idx, card in enumerate(Card.one_of_each())}
    available_action_keys = list(available_actions)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_network = self.initialize_policy_network()
        self.value_network = self.initialize_value_network()

    def initialize_policy_network(self):
        # Define the policy network architecture
        return nn.Sequential(
            nn.Linear(self.input_dimensions, self.policy_hidden_layer_size),
            nn.ReLU(),
            nn.Linear(self.policy_hidden_layer_size, self.output_dimensions),
            nn.Softmax(dim=-1)  # Assuming discrete actions
        )

    def initialize_value_network(self):
        # Define the value network architecture
        return nn.Sequential(
            nn.Linear(self.input_dimensions, self.value_hidden_layer_size),
            nn.ReLU(),
            nn.Linear(self.value_hidden_layer_size, 1)
        )

    def convert_game_state(self, game_state: dict) -> np.ndarray:
        pass

    def choose_card(self, game_state):
        # Convert game_state to a suitable format for the network
        # For now, let's assume it's already a suitable tensor
        action_probabilities = self.policy_network(game_state)
        chosen_action = np.random.choice(self.available_action_keys, p=action_probabilities.detach().numpy())
        return self.available_actions[chosen_action]

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        return super()._choose_cards_to_pass(n=n)

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        return super().place_bid(current_bid, bid_increment)

    def choose_trump(self) -> str:
        return super().choose_trump()

    # Additional methods to handle training, updating networks, etc.
