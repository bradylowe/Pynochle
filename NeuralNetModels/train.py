import torch
import torch.nn as nn

from NeuralNetModels.PredictLegalPlays.model import Net
from NeuralNetModels.dataset import load_dataset

import matplotlib.pyplot as plt
plt.style.use('ggplot')


def get_accuracy(pred_arr, original_arr):
    final_pred = pred_arr.detach().numpy() > 0.5
    original_arr = original_arr.numpy()

    correct = (final_pred == original_arr).all(axis=1).sum()
    return correct / len(final_pred) * 100


def train(model, optimizer, criterion, x_train, y_train, x_test, y_test, n_epochs):
    train_loss = []
    train_accuracy = []
    test_accuracy = []

    for epoch in range(n_epochs):

        output_train = model(x_train)

        train_accuracy.append(get_accuracy(output_train, y_train))

        # calculate the loss
        loss = criterion(output_train, y_train)
        train_loss.append(loss.item())

        # clear out the gradients from the last step loss.backward()
        optimizer.zero_grad()

        # backward propagation: calculate gradients
        loss.backward()

        # update the weights
        optimizer.step()

        with torch.no_grad():
            output_test = model(x_test)
            test_accuracy.append(get_accuracy(output_test, y_test))

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch + 1}/{n_epochs}, "
                  f"Train Loss: {loss.item():.4f}, "
                  f"Train Accuracy: {sum(train_accuracy) / len(train_accuracy):.2f}, "
                  f"Test Accuracy: {sum(test_accuracy) / len(test_accuracy):.2f}")

    return train_loss, train_accuracy, test_accuracy


def run_training(base_dir, n_data, tag='',
                 model=None, model_out=None,
                 n_epochs=100, learning_rate=0.01, hidden_dim=256):

    model = Net(hidden_dim)
    x_train, x_test, y_train, y_test = load_dataset(n_data, base_dir, tag=tag)

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    #criterion = nn.CrossEntropyLoss()
    criterion = nn.MSELoss()
    train_loss, train_accuracy, test_accuracy = train(model, optimizer, criterion,
                                                      x_train.float(), y_train.float(),
                                                      x_test.float(), y_test.float(),
                                                      n_epochs//2)

    criterion = nn.L1Loss()
    train_loss, train_accuracy, test_accuracy = train(model, optimizer, criterion,
                                                      x_train.float(), y_train.float(),
                                                      x_test.float(), y_test.float(),
                                                      n_epochs//2)

    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(12, 6), sharex=True)

    ax1.plot(train_accuracy)
    ax1.set_ylabel("training accuracy")

    ax2.plot(train_loss)
    ax2.set_ylabel("training loss")

    ax3.plot(test_accuracy)
    ax3.set_ylabel("test accuracy")

    ax3.set_xlabel("epochs")
    fig.show()
    input('Press Enter...')
