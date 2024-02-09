import torch
from torch import nn

from NeuralNetModels.PredictMeld import base_dir
from NeuralNetModels.PredictMeld.model import MeldPredictorTransformer


if __name__ == '__main__':

    import pickle
    from NeuralNetModels.PredictMeld import train_filename, test_filename

    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--n_data', type=int, default=1000000, help='Load the dataset that contains this many entries')
    parser.add_argument('--tag', type=str, help='Load the dataset with this tag in its filename')
    parser.add_argument('--model', type=str, help='Filename of the model to load')
    parser.add_argument('--model_out', type=str, help='Output filename of the model')
    parser.add_argument('--n_epochs', type=int, default=100, help='Run through the training set this many times')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')
    parser.add_argument('--hidden_dim', type=int, default=256, help='Dimensions of hidden layer')
    args = parser.parse_args()

    # Load the training dataset
    with open(train_filename, 'rb') as f:
        train_dataset = pickle.load(f)

    # For a DoubleDeck meld model:
    n_input = 8
    n_heads = 4
    n_hidden = 16
    n_layers = 3

    # Build the model
    model = MeldPredictorTransformer(n_input, n_heads, n_hidden, n_layers)

    # Define the loss function and optimizer
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters())

    # Enter the training loop
    num_epochs = 10
    for epoch in range(num_epochs):
        for hand, meld_values in train_dataset:
            hand = torch.tensor(hand, dtype=torch.long).unsqueeze(0)  # Add batch dimension
            meld_values_target = torch.tensor(meld_values, dtype=torch.float).unsqueeze(0)  # Add batch dimension

            # Forward pass
            predictions = model(hand)
            loss = loss_fn(predictions, meld_values_target)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item()}')

    # Save the model
    torch.save(model.state_dict(), 'transformer_model_state_dict.pth')

    '''
    # Load the testing dataset
    with open(test_filename, 'rb') as f:
        test_dataset = pickle.load(f)
    '''
