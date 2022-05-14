import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from time import time
import os.path as osp


def dataset_paths(n, base_dir, tag=''):
    if n >= 1000000000:
        n_billions = int(n / 1000000000)
        base_file = f'{base_dir}/Datasets/dataset_{n_billions}G'
    elif n >= 1000000:
        n_millions = int(n / 1000000)
        base_file = f'{base_dir}/Datasets/dataset_{n_millions}M'
    elif n >= 1000:
        n_thousands = int(n / 1000)
        base_file = f'{base_dir}/Datasets/dataset_{n_thousands}K'
    else:
        base_file = f'{base_dir}/Datasets/dataset_{n}'

    if tag:
        infile, outfile = f'{base_file}_{tag}_input.csv', f'{base_file}_{tag}_output.csv'
    else:
        infile, outfile = f'{base_file}_input.csv', f'{base_file}_output.csv'

    return osp.abspath(infile), osp.abspath(outfile)


def load_dataset(n, base_dir, test_size=0.2, random_state=2, tag=''):
    infile, outfile = dataset_paths(n, base_dir, tag)
    x = torch.tensor(pd.read_csv(infile).values)
    y = torch.tensor(pd.read_csv(outfile).values)
    return train_test_split(x, y, test_size=test_size, random_state=random_state)


def test_loading_data(n, base_dir):
    import code
    start = time()
    x, x_test, y, y_test = load_dataset(n, base_dir)
    print('Loaded dataset of size 1M in {} seconds'.format(round(time() - start, 1)))
    code.interact(local=locals())
