import sys
import os
sys.path.append(os.path.abspath('./'))

import json


filename = 'state_log_2024-02-04_22-09-16.json'
file_path = 'logs/hands'

with open(os.path.join(file_path, filename), 'r') as f:
    d = json.load(f)


for item in d['state_log']:
    if isinstance(item, str) and item.startswith('<<<'):
        print(item)
