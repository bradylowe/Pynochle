import torch
import torch.nn as nn
import torch.nn.functional as F

from NeuralNetModels.PredictLegalPlays.dataset import input_dim, output_dim


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
