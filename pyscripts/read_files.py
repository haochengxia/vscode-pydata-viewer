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

def format_pickle_content(obj, max_list_items=50, max_dict_items=20, indent_level=0):
    """Enhanced formatting for pickle file contents to reduce truncation"""
    indent = "&nbsp;" * (indent_level * 2)
    
    if isinstance(obj, np.ndarray) if np else False:
        # Use existing numpy array formatting but with better formatting
        if obj.size <= 100:  # For small arrays, show full content
            return f"<b><i>shape: {obj.shape}</i></b><br>{repr(obj)[6:-1].replace(' ' * 6, '')}"
        else:
            # For large arrays, show shape and some sample data
            sample_size = min(10, obj.size)
            flat_view = obj.flat
            sample_values = [str(next(flat_view)) for _ in range(sample_size)]
            return f"<b><i>shape: {obj.shape}, dtype: {obj.dtype}, size: {obj.size}</i></b><br>Sample values: [{', '.join(sample_values)}, ...]"
    
    elif isinstance(obj, dict):
        if len(obj) == 0:
            return "{}"
        
        result = "{\n"
        items_shown = 0
        for key, value in obj.items():
            if items_shown >= max_dict_items:
                result += f"{indent}&nbsp;&nbsp;... ({len(obj) - items_shown} more items)\n"
                break
            
            result += f"{indent}&nbsp;&nbsp;<b>'{key}'</b>: "
            if isinstance(value, (dict, list, tuple)) and len(str(value)) > 100:
                result += f"\n{indent}&nbsp;&nbsp;&nbsp;&nbsp;"
                result += format_pickle_content(value, max_list_items, max_dict_items, indent_level + 2)
            else:
                result += format_pickle_content(value, max_list_items, max_dict_items, indent_level + 1)
            result += ",\n"
            items_shown += 1
        
        result += f"{indent}}}"
        return result
    
    elif isinstance(obj, (list, tuple)):
        type_name = "list" if isinstance(obj, list) else "tuple"
        if len(obj) == 0:
            return f"{type_name}()" if isinstance(obj, tuple) else "[]"
        
        # For small lists/tuples, show all items
        if len(obj) <= max_list_items:
            bracket_start = "(" if isinstance(obj, tuple) else "["
            bracket_end = ")" if isinstance(obj, tuple) else "]"
            
            if len(obj) <= 10:  # Show all items inline for small collections
                items = [str(item) for item in obj]
                return f"{bracket_start}{', '.join(items)}{bracket_end}"
            else:  # Show items with line breaks for medium collections
                result = f"{bracket_start}\n"
                for i, item in enumerate(obj):
                    result += f"{indent}&nbsp;&nbsp;[{i}]: {format_pickle_content(item, max_list_items, max_dict_items, indent_level + 1)},\n"
                result += f"{indent}{bracket_end}"
                return result
        else:
            # For large lists/tuples, show first few, middle indicator, and last few
            bracket_start = "(" if isinstance(obj, tuple) else "["
            bracket_end = ")" if isinstance(obj, tuple) else "]"
            show_count = min(5, max_list_items // 2)
            
            result = f"{bracket_start}\n"
            # Show first few items
            for i in range(show_count):
                result += f"{indent}&nbsp;&nbsp;[{i}]: {format_pickle_content(obj[i], max_list_items, max_dict_items, indent_level + 1)},\n"
            
            # Show truncation indicator
            result += f"{indent}&nbsp;&nbsp;... ({len(obj) - 2 * show_count} more items),\n"
            
            # Show last few items
            for i in range(len(obj) - show_count, len(obj)):
                result += f"{indent}&nbsp;&nbsp;[{i}]: {format_pickle_content(obj[i], max_list_items, max_dict_items, indent_level + 1)}"
                if i < len(obj) - 1:
                    result += ","
                result += "\n"
            
            result += f"{indent}{bracket_end}"
            return result
    
    elif hasattr(obj, '__dict__') and not isinstance(obj, type):
        # Custom objects with attributes
        result = f"<b>{type(obj).__name__}</b> {{\n"
        attrs = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        
        if attrs:
            for key, value in list(attrs.items())[:max_dict_items]:
                result += f"{indent}&nbsp;&nbsp;<b>{key}</b>: {format_pickle_content(value, max_list_items, max_dict_items, indent_level + 1)},\n"
            if len(attrs) > max_dict_items:
                result += f"{indent}&nbsp;&nbsp;... ({len(attrs) - max_dict_items} more attributes)\n"
        
        result += f"{indent}}}"
        return result
    
    else:
        # Basic types (int, float, str, bool, None, etc.)
        return repr(obj)

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
    global np
    
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
            # Import numpy for enhanced array formatting
            if np is None:
                try:
                    import numpy as np
                except ImportError:
                    pass
                
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
                        continue
                
                # Use enhanced formatting for non-matplotlib objects
                print(f'<b>Item {i+1}/{num_contents}:</b>')
                formatted_content = format_pickle_content(c)
                print(formatted_content)
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
