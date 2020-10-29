import torch
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.transforms as transforms
import numpy as np
import os
import subprocess

from dataset import CNN3D_Dataset

# from spatial_transforms import (Compose, Normalize, Scale, CenterCrop, ToTensor)
# from temporal_transforms import LoopPadding

import configparser


def extract_frames_from_video(config):
    ########################################################################
    # Extract Frames from videos
    extracted_frame_dir = config.get('dataset', 'extracted_frame_path')
    video_data_dir = config.get('dataset', 'dataset_path')
    suffix = config.get('dataset', 'video_suffix')
    fps = config.getint('dataset', 'fps')

    if os.path.exists(extracted_frame_dir):
        subprocess.call('rm -rf {}'.format(extracted_frame_dir), shell=True)

    subprocess.call('mkdir {}'.format(extracted_frame_dir), shell=True)
    for name in video_names:
        video_full_name = name + suffix
        video_path = os.path.join(video_data_dir, video_full_name)
        if os.path.exists(video_path):
            print(video_path)
            frame_dir = os.path.join(extracted_frame_dir, name)
            subprocess.call('mkdir {}'.format(frame_dir), shell=True)
            # extrat frames from video and store in tmp
            # subprocess.call('ffmpeg -i {} -vf "scale={}:{},fps={}" tmp/image_%04d.jpg'
            #     .format(video_path, fps), shell=True)

            subprocess.call('ffmpeg -i {} -vf "fps={}" {}/image_%04d.jpg'
                .format(video_path, fps, frame_dir), shell=True)


def get_config(config_path):
    if not os.path.exists(config_path):
        raise FileExistsError('config file does not exist')
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def get_model_name(config):
    """ Generate a name for the model consisting of all the hyperparameter values

    Args:
        config: Configuration object containing the hyperparameters
    Returns:
        path: A string with the hyperparameter name and value concatenated
    """
    path = "model_"
    path += "epoch{}_".format(config["num_epochs"])
    path += "bs{}_".format(config["batch_size"])
    path += "lr{}".format(config["learning_rate"])

    return path


def get_relevant_indices(dataset, classes, target_classes):
    """ Returns the indices for datapoints in the dataset that
    belongs to the desired target classes, a subset of all possible classes.

    Args:
        dataset: Dataset object
        classes: A list of strings denoting the name of each class
        target_classes: A list of strings denoting the name of the desired classes.
                        Should be a subset of the 'classes'
    Returns:
        indices: list of indices that have labels corresponding to one of the target classes
    """
    indices = []
    for i in range(len(dataset)):
        # Check if the label is in the target classes
        label_index = dataset[i][1] # ex: 3
        label_class = classes[label_index] # ex: 'cat'
        if label_class in target_classes:
            indices.append(i)

    return indices


def normalize_label(labels):
    """
    Given a tensor containing 2 possible values, normalize this to 0/1

    Args:
        labels: a 1D tensor containing two possible scalar values
    Returns:
        A tensor normalize to 0/1 value
    """
    max_val = torch.max(labels)
    min_val = torch.min(labels)
    norm_labels = (labels - min_val)/(max_val - min_val)

    return norm_labels



################################### LOADING DATA ################################### 
def get_data_loader(train_list, test_list, train_label, test_label, model_name, config):
    # Use the mean and std 
    # https://pytorch.org/docs/stable/torchvision/models.html
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    frame_size = config.getint(model_name, 'frame_size')
    ## sample_duration will be the number of frames = duration of video in seconds
    # opt.sample_duration = len(os.listdir("tmp"))
    # TODO: Normalize Image (center / min-max) & Map rgb --> [0, 1]
    spatial_transform  = transforms.Compose([transforms.Resize([frame_size, frame_size]),
                                transforms.ToTensor(),
                                transforms.Normalize(mean=mean, std=std)])

    ## temporal_transform = LoopPadding(opt.sample_duration)
    temporal_transform = None
    
    # data = Video(video_path, spatial_transform=spatial_transform,
    #              temporal_transform=temporal_transform,
    #              sample_duration=opt.sample_duration)
    # data_loader = torch.utils.data.DataLoader(data, batch_size=opt.batch_size,
    #                                           shuffle=False, num_workers=opt.n_threads, pin_memory=True)

    batch_size = config.getint(model_name, 'batch_size')
    extract_frames_path = config.get('dataset', 'extracted_frame_path')
    n_threads = config.getint(model_name, 'n_threads')

    train_set = CNN3D_Dataset(extract_frames_path, train_list, train_label, spatial_transform=spatial_transform,
                 temporal_transform=temporal_transform)
    valid_set = CNN3D_Dataset(extract_frames_path, test_list, test_label, spatial_transform=spatial_transform,
                 temporal_transform=temporal_transform)
    train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size,
                                              shuffle=False, num_workers=n_threads, pin_memory=True)
    valid_loader = torch.utils.data.DataLoader(valid_set, batch_size=batch_size,
                                              shuffle=False, num_workers=n_threads, pin_memory=True)

    return train_loader, valid_loader