import torch
import torch.nn as nn

from NeuralNetModels.PredictNextCard.model import PredictNextCard
from NeuralNetModels.PredictNextCard.dataset import NextCardDataset
from NeuralNetModels.train import train, plot_training_results


if __name__ == '__main__':

    from time import time
    import argparse
    parser = argparse.ArgumentParser(description='Train the neural net model')
    parser.add_argument('--train_file', type=str, required=True, help='Path to the training data')
    parser.add_argument('--test_file', type=str, required=True, help='Path to the testing data')
    parser.add_argument('--n_epochs', type=int, default=100, help='Run through the training set this many times')
    parser.add_argument('--batch_size', type=int, default=64, help='Number of items to learn on at a time')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')
    parser.add_argument('--hidden_dim', type=int, default=256, help='Dimensions of hidden layer')
    parser.add_argument('--plot_file', type=str, help='Filename to use for plot file')
    args = parser.parse_args()

    model = PredictNextCard(args.hidden_dim)
    print()
    print(f'Using {args.hidden_dim} neurons in hidden dimension')

    train_dataset = NextCardDataset(args.train_file, batch_size=args.batch_size)
    test_dataset = NextCardDataset(args.test_file, batch_size=args.batch_size)

    print('Size of training data:', train_dataset.inputs.size(), train_dataset.outputs.size())
    print('Size of testing data:', test_dataset.inputs.size(), test_dataset.outputs.size())

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
    criterion = nn.NLLLoss()

    start = time()
    print('Training with', criterion)
    train_loss, train_accuracy, test_accuracy = train(model, optimizer, criterion, scheduler,
                                                      train_dataset, test_dataset, args.n_epochs)
    end = time()
    print(f'Took {round(end - start)} seconds to train')

    if not args.plot_file:
        args.plot_file = args.train_file\
            .replace('Datasets', 'Plots')\
            .replace('.csv', '.png')\
            .replace('_input', f'_{args.n_epochs}epochs_{args.hidden_dim}hidden')
        print(f'Saving {args.plot_file} to file')

    plot_training_results(train_accuracy, train_loss, test_accuracy, args.plot_file)
