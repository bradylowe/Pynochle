from NeuralNetModels.PredictLegalPlays import base_dir
from NeuralNetModels.train import run_training


if __name__ == '__main__':

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

    run_training(base_dir, n_data=args.n_data, tag=args.tag,
                 model=args.model, model_out=args.model_out,
                 n_epochs=args.n_epochs, learning_rate=args.lr, hidden_dim=args.hidden_dim)
