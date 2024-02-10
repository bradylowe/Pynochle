import os
import sys
sys.path.append(os.path.abspath('./'))

import torch
from torch import nn


if __name__ == '__main__':

    from NeuralNetModels.PredictMeld import data_dir, model_dir
    from NeuralNetModels.PredictMeld.dataset import MeldDataset
    from NeuralNetModels.PredictMeld.model import MeldPredictorTransformer

    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--filename', type=str, required=True, help='Output filename of dataset (.pkl)')
    parser.add_argument('--model', type=str, help='Filename of the model to load')
    parser.add_argument('--model_out', type=str, default='transformer_model_state_dict.pth',
                        help='Output filename of the model')

    parser.add_argument('--n_epochs', type=int, default=10, help='Run through the training set this many times')
    parser.add_argument('--batch_size', type=int, default=32, help='Examples per batch')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')

    parser.add_argument('--n_input', type=int, default=8, help='Input embedding dimension')
    parser.add_argument('--n_heads', type=int, default=4, help='Number of attention heads')
    parser.add_argument('--n_hidden', type=int, default=32, help='Hidden layer dimension')
    parser.add_argument('--n_layers', type=int, default=4, help='Number of transformer layers')
    args = parser.parse_args()

    # Load the training dataset
    if os.path.exists(args.filename):
        filename = args.filename
    else:
        filename = os.path.join(data_dir, args.filename)
    train_dataset = MeldDataset(filename, args.batch_size)

    # Reference the model directory
    if args.model and not args.model.startswith(model_dir):
        args.model = os.path.join(model_dir, args.model)
    if args.model_out and not args.model_out.startswith(model_dir):
        args.model_out = os.path.join(model_dir, args.model_out)

    # Build the model
    model = MeldPredictorTransformer(
        args.n_input,
        args.n_heads,
        args.n_hidden,
        args.n_layers,
    )

    # Define the loss function and optimizer
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters())

    # Enter the training loop
    for epoch in range(args.n_epochs):
        for hands, melds in train_dataset:
            hands = torch.tensor(hands, dtype=torch.long)
            melds = torch.tensor(melds, dtype=torch.float)

            # Forward pass
            predictions = model(hands)
            loss = loss_fn(predictions, melds)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Save the model
        torch.save(model.state_dict(), args.model_out.replace('.pth', f'_{epoch}.pth'))
        print(f'Epoch [{epoch + 1}/{args.n_epochs}], Loss: {loss.item()}')

    '''
    # Load the testing dataset
    with open(test_filename, 'rb') as f:
        test_dataset = pickle.load(f)
    '''
