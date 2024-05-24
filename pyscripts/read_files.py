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
    
    
# ============ Enhancement ============
# gathering enhance features here
ENHANCE_PLT = True

try:
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    
    # dummy to load manager for plt
    _ = plt.figure()
    def render_plot_to_html(fig):        
        buf = BytesIO()
        fig.savefig(buf, format='jpeg')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        html_img = f'<img src="data:image/jpeg;base64,{img_base64}">'
        return html_img
except:
    ENHANCE_PLT = False
# =====================================

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
            print("<b><i>shape: {}</i></b>".format(array.shape))
            print("[")
            if len(array) > 5:
                for item in array[:5]:
                    print_ndarray(item)
                    print(",")
                print("...,")
                print_ndarray(array[-1])
            else:
                for item in array[:-1]:
                    print_ndarray(item)
                    print(",")
                print_ndarray(array[-1])
            print("]")
    else:
        print("<b><i>shape: {}</i></b>".format(array.shape))
        # repr(array) will outputs "array([e, e, ...])", we cut the head "array(" and tail ")", then replace redundant 6 spaces per line
        print(repr(array)[6:-1].replace(" " * 6, ""))

if file_type == FileType.NUMPY.value:
    # Solve numpy files .npy or .npz
    try:
        import numpy as np
        if file_path.endswith("npz"):
            content = np.load(file_path, allow_pickle=True)
            print("{")
            for f in content.files:
                print("'<b><i>{}</i></b>':".format(f))
                print_ndarray(content[f])
                # print(",")
            print("}")
        else:
            content = np.load(file_path, allow_pickle=True)
            print_ndarray(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PICKLE.value:
    # Solve pickle files .pkl
    try:
        import pickle
        contents = []
        with open(file_path, "rb") as f:
            while True:
                try:
                    contents.append(pickle.load(f))
                except EOFError:
                    break
        num_contents = len(contents)
        for i, c in enumerate(contents):
            if ENHANCE_PLT:
                if isinstance(c, plt.Figure):
                    c = render_plot_to_html(c)
            print(f'Item {i+1}/{num_contents}:', c, sep="\n")
    except UnicodeDecodeError:
        with open(file_path, "rb") as f:
            content = pickle.load(f, encoding="latin1")
        print(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PYTORCH.value:
    # Solve pytorch files .pth
    try:
        import torch
        content = torch.load(file_path, map_location='cpu')
        print(content)
    except Exception as e:
        print(e)
else:
    print("Unsupport file type.")
