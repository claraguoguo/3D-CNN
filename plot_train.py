import matplotlib.pyplot as plt
import pandas as pd
import torch
from util import *


def load_csv(type, model_name, config):
    """
    Given the type ('err'/'loss'), loads the appropriate CSV files to plot

    :param type: string denoting the type of files to load ('err' or 'loss')
    :param config: configuration dictionary
    :return: Numpy arrays for the train and test value
    """

    epoch = config.getint(model_name, 'epoch')
    lr = config.getfloat(model_name, 'lr')
    bs = config.getint(model_name, 'batch_size')


    model_path = model_name
    train_file = 'train_{}_{}_lr{}_epoch{}_bs{}.csv'.format(type, model_path, lr, epoch, bs)
    val_file = 'val_{}_{}_lr{}_epoch{}_bs{}.csv'.format(type, model_path, lr, epoch, bs)

    train_data = pd.read_csv(train_file)
    val_data = pd.read_csv(val_file)

    return train_data, val_data


def plot_graph(model_name, type, train_data, val_data, config):
    """
    Plot the training loss/error curve given the data from CSV
    """
    epoch = config.getint(model_name, 'epoch')
    lr = config.getfloat(model_name, 'lr')
    bs = config.getint(model_name, 'batch_size')
    valid_loss = val_data["val_loss"].iloc[-1]

    plt.figure()
    plt.title("{} over training epochs \n {}_lr{}_epoch{}_bs{}_val{}".format(
        type, model_name, lr, epoch, bs, valid_loss))
    plt.plot(train_data["epoch"], train_data["train_{}".format(type)], label="Train")
    plt.plot(val_data["epoch"], val_data["val_{}".format(type)], label="Validation")
    plt.xlabel("Epoch")
    plt.ylabel(type)
    plt.legend(loc='best')
    plt.savefig("{}_{}_lr{}_epoch{}_bs{}_val{}.png".format(type, model_name, lr, epoch, bs, valid_loss))
    return


def generate_result_plots(model_name, config):
    ########################################################################
    # Loads the configuration for the experiment from the configuration file
    type = 'loss'
    # Load the CSV files according to the current config
    # train_err_data, val_err_data = load_csv('err', model_path)
    train_loss_data, val_loss_data = load_csv(type, model_name, config)

    # Print the final loss/error for the train/validation set from the CSV file
    # print("Final training error: {0:.3f}% | Final validation error: {1:.3f}%".format(train_err_data["train_err"].iloc[-1]*100, val_err_data["val_err"].iloc[-1]*100))
    print("Final training loss: {0:.5f} | Final validation loss: {1:.5f}".format(train_loss_data["train_loss"].iloc[-1],
          val_loss_data["val_loss"].iloc[-1]))

    # Plot a train vs test err/loss graph for this hyperparameter
    # plot_graph(model_path, "err", train_err_data, val_err_data)
    plot_graph(model_name, type, train_loss_data, val_loss_data, config)
