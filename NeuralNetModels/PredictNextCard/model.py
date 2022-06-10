import torch.nn as nn


class PredictNextCard(nn.Module):

    input_dim = 50
    output_dim = 20

    def __init__(self, hidden_dim):
        super(PredictNextCard, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(self.input_dim, hidden_dim, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim, self.output_dim)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, x):
        _, (h, _) = self.lstm(x)
        x = self.fc1(h[0])
        x = self.softmax(x)
        return x
