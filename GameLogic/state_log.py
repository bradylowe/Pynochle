import os
import re
import json
import numpy as np


class StateLog:

    def __init__(self, filename: str):
        self.filename = filename
        self.log = []
        self.timestamp = None

        self._states_by_index = {}
        self._actions_by_index = {}

        if os.path.exists(self.filename):
            self._read_log()

    def get_state_index_before(self, index: int) -> int:
        last_idx = 0
        for idx in self._states_by_index:
            if idx > index:
                return last_idx
            last_idx = idx

    def get_state_index_after(self, index: int) -> int:
        for idx in self._states_by_index:
            if idx > index:
                return idx

    def get_action_index_before(self, index: int) -> int:
        last_idx = 0
        for idx in self._actions_by_index:
            if idx > index:
                return last_idx
            last_idx = idx

    def get_action_index_after(self, index: int) -> int:
        for idx in self._actions_by_index:
            if idx > index:
                return idx

    def _read_log(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
            self.timestamp = data['timestamp']
            self.log = data['state_log']

        self._sort()

    def _sort(self):
        for idx, line in enumerate(self.log):
            if isinstance(line, dict):
                self._states_by_index[idx] = line
            elif line.startswith('<<<'):
                self._actions_by_index[idx] = line

    def get_card_play_indices(self, after: bool = False):
        pattern = r'<<<PLAYER (\d+) PLAYS (A|10|K|Q|J|9) of (Spades|Hearts|Clubs|Diamonds)>>>'
        indices = []
        for idx, action in self._actions_by_index.items():
            if re.match(pattern, action):
                if after:
                    idx = self.get_state_index_after(idx)
                else:
                    idx = self.get_state_index_before(idx)
                indices.append(idx)

        return indices

    def get_random_card_play(self) -> int:
        indices = self.get_card_play_indices()
        return np.random.choice(indices)

    def __getitem__(self, item):
        return self.log[item]
