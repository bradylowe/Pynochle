import torch
import torch.nn as nn
import torch.nn.functional as F

from NeuralNetModels.PredictLegalPlays.dataset import input_dim, output_dim


'''
INPUTS
---
- cards played in trick (REQUIRED)    list(3 cards)   = 60 neurons
- number of players (REQUIRED)        integer         = 1 neuron
- trump suit (REQUIRED)               suit            = 4 neuron

- cards in hand (maybe)               list(25 cards)  = 500 neurons
'''


'''
OUTPUT
1-J♠  | 2-Q♠  | 3-K♠  | 4-10♠  | 5-A♠  | 6-J♥  | 7-Q♥  | 8-K♥   | 9-10♥  | 10-A♥
11-J♣ | 12-Q♣ | 13-K♣ | 14-10♣ | 15-A♣ | 16-J♦ | 17-Q♦ | 18-K♦  | 19-10♦ | 20-A♦
---
- score for every card in deck (20 neurons)
'''


class Net(nn.Module):
    def __init__(self, hidden_dim):
        super(Net, self).__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        self.fc1 = nn.Linear(self.input_dim, self.hidden_dim)
        self.fc2 = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)

        return torch.sigmoid(x)
