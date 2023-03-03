# -*- coding: utf-8 -*-

"""
sys.argv[1]: `.npy` or `.npz` file path
"""

import sys
file_type = int(sys.argv[1])
file_path = sys.argv[2]

from enum import Enum
class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2

def print_ndarray(array):
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    if array.dtype == np.dtype("O"):
        if not array.shape:
            array = array.item()
            if isinstance(array, dict):
                print("{")
                for k, v in array.items():
                    print("'<b><i>{}</i></b>':".format(k))
                    if isinstance(v, np.ndarray):
                        print("<b><i>shape: {}</i></b>".format(v.shape))
                    print("{},".format(v))
                print("}")
            else:
                print(array)
        else:
            if len(array) > 5:
                print("[")
                for item in array[:5]:
                    print_ndarray(item)
                    print(',')
                print("...,")
                print_ndarray(array[-1])
                print("]")
            else:
                for item in array:
                    print_ndarray(item)
    else:
        print("<b><i>shape: {}</i></b>".format(array.shape))
        print(array)

if file_type == FileType.NUMPY.value:
    # Solve numpy files .npy or .npz
    try:
        import numpy as np
        if file_path.endswith('npz'):
            content = np.load(file_path, allow_pickle=True)
            print('{')
            for f in content.files:
                print("'<b><i>{}</i></b>':".format(f))
                print_ndarray(content[f])
                # print(',')
            print('}')
        else:
            content = np.load(file_path, allow_pickle=True)
            print_ndarray(content)
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
elif file_type == FileType.PYTORCH.value:
    # Solve pytorch files .pth
    try:
        import torch
        content = torch.load(file_path)
        print(content)
    except Exception as e:
        print(e)
else:
    print('Unsupport file type.')