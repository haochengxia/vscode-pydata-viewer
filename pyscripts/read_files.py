# -*- coding: utf-8 -*-

"""
sys.argv[1]: `.npy` or `.npz` file path
"""

import sys
from enum import Enum

class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2
    COMPRESSED_PICKLE = 3

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

np = None
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

def process_file(file_type: int, file_path: str):
    """main function to process file
    
    Args:
        file_type: 
        file_path: 
    """
    if file_type == FileType.NUMPY.value:
        # Solve numpy files .npy or .npz
        try:
            global np
            import numpy as np
            if file_path.endswith("npz"):
                content = np.load(file_path, allow_pickle=True)
                print("{")
                for f in content.files:
                    print("'<b><i>{}</i></b>':".format(f))
                    print_ndarray(content[f])
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
            
    elif file_type == FileType.COMPRESSED_PICKLE.value:
        # compressed pickle file .pkl.gz
        try:
            import compress_pickle
            contents = compress_pickle.load(file_path)
            if ENHANCE_PLT:
                if isinstance(contents, plt.Figure):
                    contents = render_plot_to_html(contents)
            print(contents)
        except Exception as e:
            print(e)
            
    elif file_type == FileType.PYTORCH.value:
        # Solve pytorch files .pth
        try:
            import torch
            content = torch.load(file_path, map_location='cpu', weights_only=True)
            print(content)
        except Exception as e:
            print(e)
    else:
        print("Unsupport file type.")

def main():
    """main function"""
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        print("Usage: python read_files.py <file_type> <file_path>")
        return
    
    try:
        file_type = int(sys.argv[1])
        file_path = sys.argv[2]
        process_file(file_type, file_path)
    except ValueError:
        print("Error: file_type must be an integer")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
