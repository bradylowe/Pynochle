import matplotlib.pyplot as plt
import numpy as np
import torch
plt.style.use('ggplot')


def get_accuracy(pred_arr, original_arr):
    final_pred = np.argmax(pred_arr.detach().numpy(), axis=1)
    original_arr = original_arr.numpy()

    correct = np.equal(final_pred, original_arr)
    return correct.sum() / len(correct) * 100


def train(model, optimizer, criterion, scheduler, train_dataset, test_dataset, n_epochs):
    train_loss = []
    train_accuracy = []
    test_accuracy = []

    test_iterator = test_dataset.__iter__()

    for epoch in range(n_epochs):

        for x, y in train_dataset:
            output_train = model(x)
            loss = criterion(output_train, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Sample the current model performance at every epoch
        train_accuracy.append(get_accuracy(output_train, y))
        train_loss.append(loss.item())
        with torch.no_grad():
            x_test, y_test = next(test_iterator)
            output_test = model(x_test)
            test_accuracy.append(get_accuracy(output_test, y_test))

        # Print model performance to user sometimes
        if epoch < 5 or (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch + 1}/{n_epochs}, "
                  f"Train Loss: {loss.item():.4f}, "
                  f"Train Accuracy: {sum(train_accuracy) / len(train_accuracy):.2f}, "
                  f"Test Accuracy: {sum(test_accuracy) / len(test_accuracy):.2f}")
        scheduler.step()

    return train_loss, train_accuracy, test_accuracy


def plot_training_results(train_accuracy, train_loss, test_accuracy, plot_file=None):

    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(12, 6), sharex=True)

    ax1.plot(train_accuracy)
    ax1.set_ylabel("training accuracy")
    ax2.plot(train_loss)
    ax2.set_ylabel("training loss")
    ax3.plot(test_accuracy)
    ax3.set_xlabel("epochs")
    ax3.set_ylabel("test accuracy")

    if plot_file:
        fig.savefig(plot_file)
    else:
        fig.show()
        input('Press enter...')
