import torch
import torch.nn as nn
import math

from GameLogic.cards import Card


class MeldPredictorTransformer(nn.Module):

    _card_to_token = {card: token for token, card in enumerate(Card.one_of_each())}
    n_tokens = len(_card_to_token)

    def __init__(self, n_input, n_heads, n_hidden, n_layers, dropout=0.5):
        super(MeldPredictorTransformer, self).__init__()
        #self.pos_encoder = PositionalEncoding(n_input, dropout)
        encoder_layers = nn.TransformerEncoderLayer(n_input, n_heads, n_hidden, dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, n_layers)
        self.encoder = nn.Embedding(self.n_tokens, n_input)
        self.n_inp = n_input
        self.decoder = nn.Linear(n_input, 4)  # Output is 4 integers for meld values
        self.init_weights()

    def init_weights(self):
        init_range = 0.1
        self.encoder.weight.data.uniform_(-init_range, init_range)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-init_range, init_range)

    def forward(self, src):
        src = self.encoder(src) * math.sqrt(self.n_inp)
        #src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        output = self.decoder(output.mean(dim=1))  # Aggregate over seq length and predict
        return output

    def predict(self, cards):
        tokens = [self.to_token(card) for card in cards]
        return self.forward(tokens)

    @staticmethod
    def to_token(card):
        return MeldPredictorTransformer._card_to_token[card]

class PositionalEncoding(nn.Module):

    def __init__(self, d_model, dropout=0.1, max_len=500):
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
