import os.path as osp
import pandas as pd
from NeuralNetModels import num_to_str

from torch.utils.data import Dataset as TorchDataset


class DatasetBuilder:

    def __init__(self):
        self.base_dir = osp.dirname(osp.abspath(__file__))

    def build(self, n, path=None, tags=None):
        pass

    def build_filenames(self, n, path=None, tags=None):
        if path is None:
            path = osp.join(self.base_dir, 'Datasets')

        base_name = osp.join(path, f'dataset_{num_to_str(n)}')
        if tags is not None:
            tags_str = tags if isinstance(tags, str) else '_'.join(tags)
            infile, outfile = f'{base_name}_{tags_str}_input.csv', f'{base_name}_{tags_str}_output.csv'
        else:
            infile, outfile = f'{base_name}_input.csv', f'{base_name}_output.csv'

        return osp.abspath(infile), osp.abspath(outfile)


class Dataset(TorchDataset):

    def __init__(self, filename, batch_size=1):
        super().__init__()
        self.batch_size = batch_size
        self.inputs_file = filename.replace('_output', '_input')
        self.outputs_file = filename.replace('_input', '_output')
        self.inputs = pd.read_csv(self.inputs_file).values
        self.outputs = pd.read_csv(self.outputs_file).values

    def __getitem__(self, index):
        return self.inputs[index], self.outputs[index]

    def __len__(self):
        return len(self.inputs)

    def __iter__(self):
        return DatasetIterator(self)


class DatasetIterator:
    """
    This class allows us to iterate through our dataset in batches.
    """

    def __init__(self, data):
        self._batch_size = data.batch_size
        self._inputs = data.inputs
        self._outputs = data.outputs
        self._index = 0

    def __next__(self):
        length = len(self._inputs)
        if self._index < length:
            end = self._index + self._batch_size
            if end > length:
                end = length
            inputs = self._inputs[self._index:end]
            outputs = self._outputs[self._index:end]
            self._index = end
            return inputs, outputs
        else:
            raise StopIteration
