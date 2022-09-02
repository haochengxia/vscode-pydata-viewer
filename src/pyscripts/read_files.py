# -*- coding: utf-8 -*-

"""
sys.argv[1]: `.npy` or `.npz` file path
"""

import sys

try:
    import numpy as np
    content = np.load(sys.argv[1], allow_pickle=True)
    print(content)
except Exception as e:
    print(e)