# -*- coding: utf-8 -*-

"""
sys.argv[1]: `.npy` or `.npz` file path
"""

import sys;
file_type = int(sys.argv[1])
file_path = sys.argv[2]

from enum import Enum
class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2
if file_type == FileType.NUMPY.value:
    # Solve numpy files .npy or .npz
    try:
        import numpy as np
        content = np.load(sys.argv[1], allow_pickle=True)
        print(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PICKLE.value:
    # Solve pickle files .pkl
    try:
        import pickle
        f = open(file_path, 'rb')
        content = pickle.load(f)
        print(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PICKLE.value:
    # Solve pytorch files .pth
    try:
        import torch
        content = torch.load(file_path)
        print(content)
    except Exception as e:
        print(e)
else:
    print('Unsupport file type.')