from typing import List

import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim
from torch.nn import TransformerEncoder, TransformerEncoderLayer

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


class TransformerPinochlePlayer(SimplePinochlePlayer):
    def __init__(self, ntoken, ninp, nhead, nhid, nlayers, n_actions, dropout=0.5):
        super(TransformerPinochlePlayer, self).__init__()
        self.model = TransformerModel(ntoken, ninp, nhead, nhid, nlayers, n_actions, dropout)
        #self.model = TransformerModel(input_size, ninp, nhead, nhid, nlayers, n_actions, dropout)
        self.optimizer = optim.Adam(self.model.parameters())
        self.n_actions = n_actions

    def select_action(self, state):
        """
        Selects an action (card to play) based on the current state.
        The state should be preprocessed to fit the transformer input requirements.
        """
        with torch.no_grad():
            action_scores = self.model(state)
            action = action_scores.max(1)[1].view(1, 1)
        return action

    def update(self, reward, state, action):
        """
        Update the model based on the outcome of the action.
        """
        self.optimizer.zero_grad()
        action_scores = self.model(state)
        loss = self.compute_loss(action_scores, action, reward)
        loss.backward()
        self.optimizer.step()

    def compute_loss(self, action_scores, action, reward):
        # Define a loss function based on your reinforcement learning algorithm
        return loss

    def convert_game_state(self, game_state: dict) -> np.ndarray:
        pass

    def _choose_cards_to_pass(self, n: int = 0) -> List[Card]:
        return super()._choose_cards_to_pass(n=n)

    def place_bid(self, current_bid: int, bid_increment: int) -> int:
        return super().place_bid(current_bid, bid_increment)

    def choose_trump(self) -> str:
        return super().choose_trump()

class TransformerModel(nn.Module):
    def __init__(self, ntoken, ninp, nhead, nhid, nlayers, n_actions, dropout):
        super(TransformerModel, self).__init__()
        from torch.nn import TransformerEncoder, TransformerEncoderLayer
        self.encoder = nn.Embedding(ntoken, ninp)
        #self.encoder = nn.Linear(input_size, ninp)
        self.pos_encoder = PositionalEncoding(ninp, dropout)
        encoder_layers = TransformerEncoderLayer(ninp, nhead, nhid, dropout)
        self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
        self.ninp = ninp
        self.decoder = nn.Linear(ninp, n_actions)

        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src):
        src = self.encoder(src) * math.sqrt(self.ninp)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        output = self.decoder(output)
        return output

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * -(math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)
