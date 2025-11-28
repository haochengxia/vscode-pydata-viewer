# -*- coding: utf-8 -*-

"""
sys.argv[1]: File Type ID
sys.argv[2]: File Path
"""

import sys
import types
from enum import Enum
from io import BytesIO
import base64

# ============ Configuration ============
MAX_DEPTH = 10         # Max nesting level to prevent infinite recursion
MAX_ITEMS = 30         # Max items to show per collection (start + end)
MAX_STR_LEN = 1000      # Max string characters before truncation
INDENT_SPACER = "&nbsp;&nbsp;&nbsp;&nbsp;" # 4 spaces for HTML indentation

def set_config(mode):
    global MAX_DEPTH, MAX_ITEMS, MAX_STR_LEN
    if mode == 'full':
        MAX_DEPTH = 100
        MAX_ITEMS = 1000000
        MAX_STR_LEN = 1000000
        if np:
            np.set_printoptions(threshold=sys.maxsize)
        if torch:
            torch.set_printoptions(threshold=float('inf'))
# =======================================

class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2
    COMPRESSED_PICKLE = 3

# Library Loading with Fallbacks
try:
    import numpy as np
except ImportError:
    np = None

try:
    import torch
except ImportError:
    torch = None

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # dummy to load manager for plt
    _ = plt.figure()
    HAS_MPL = True
except:
    HAS_MPL = False

# ============ Core Formatter ============

class JetBrainsFormatter:
    def __init__(self):
        self.seen_ids = set()

    def _render_plot_to_html(self, fig):
        """Renders a matplotlib figure to base64 HTML"""
        try:
            buf = BytesIO()
            fig.savefig(buf, format='jpeg')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return f'<br><img src="data:image/jpeg;base64,{img_base64}"><br>'
        except Exception as e:
            return f"&lt;Plot Error: {e}&gt;"

    def _get_indent(self, level):
        return INDENT_SPACER * level

    def _format_header(self, type_name, meta_info):
        """
        Returns bold type name and italicized meta info.
        Example: <b>list</b> <i>(len=50)</i>
        """
        return f"<b>{type_name}</b> <i>{meta_info}</i>"

    def format(self, obj, level=0):
        """Recursive entry point"""
        
        # 1. Handle Matplotlib Figures (Special Case)
        if HAS_MPL and isinstance(obj, plt.Figure):
            return self._render_plot_to_html(obj)

        # 2. Check Recursion Depth & Circular References
        if level > MAX_DEPTH:
            return "<i>... (max depth exceeded)</i>"
        
        obj_id = id(obj)
        # Only track container types for circular refs
        if isinstance(obj, (dict, list, tuple, set)) and obj_id in self.seen_ids:
             return f"<i>... (circular reference {type(obj).__name__})</i>"
        
        # We don't add immutable primitives to seen_ids, only containers
        is_container = isinstance(obj, (dict, list, tuple, set))
        if is_container:
            self.seen_ids.add(obj_id)

        try:
            res = self._dispatch_format(obj, level)
        finally:
            if is_container:
                self.seen_ids.remove(obj_id)
        
        return res

    def _dispatch_format(self, obj, level):
        indent = self._get_indent(level)
        
        # --- Basic Primitives ---
        if obj is None:
            return f"<span style='color:#888'>None</span>"
        if isinstance(obj, bool):
            return f"<span style='color:#cc7832'>{str(obj)}</span>"
        if isinstance(obj, (int, float, complex)):
            return f"<span style='color:#6897bb'>{str(obj)}</span>"
        
        # --- Strings (with truncation) ---
        if isinstance(obj, str):
            if len(obj) > MAX_STR_LEN:
                preview = obj[:MAX_STR_LEN] \
                    .replace('<', '&lt;').replace('>', '&gt;').replace('\n', '\\n')
                return f"<i>(len={len(obj)})</i><span style='color:#6a8759'>'{preview}...'</span>"
            else:
                safe_str = obj.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '\\n')
                return f"<i>(len={len(obj)})</i><span style='color:#6a8759'>'{safe_str}'</span>"

        # --- Bytes ---
        if isinstance(obj, bytes):
            return f"<b>bytes</b> <i>(len={len(obj)})</i>"

        # --- NumPy Arrays ---
        if np and isinstance(obj, np.ndarray):
            return self._format_numpy(obj, level)

        # --- PyTorch Tensors ---
        if torch and isinstance(obj, torch.Tensor):
            return self._format_torch(obj, level)

        # --- Dictionaries ---
        if isinstance(obj, dict):
            return self._format_dict(obj, level)

        # --- Lists / Tuples / Sets ---
        if isinstance(obj, (list, tuple, set)):
            return self._format_sequence(obj, level)

        # --- Generic Objects (Classes) ---
        if hasattr(obj, '__dict__'):
            return self._format_object(obj, level)

        # --- Fallback ---
        return str(obj)

    def _format_numpy(self, arr, level):
        shape_str = str(arr.shape).replace(" ", "")
        header = self._format_header("ndarray", f"(shape={shape_str}, dtype={arr.dtype})")
        
        if arr.size == 0:
            return header + " []"
        
        if arr.size == 1:
            # Use recursive format for the single item
            return header + f" {self.format(arr.item(), level + 1)}"

        # If small 1D/2D, print full content
        if (arr.size < 20 and arr.ndim <= 2) or MAX_ITEMS > 1000:
            content = str(arr).replace('\n', f'\n{self._get_indent(level+1)}')
            return f"{header}<br>{self._get_indent(level+1)}{content}"

        # Otherwise, show preview
        try:
            return f"{header} min: {np.min(arr):.4g}, max: {np.max(arr):.4g}, mean: {np.mean(arr):.4g}"
        except Exception as e:
            return f"{header}"

    def _format_torch(self, tensor, level):
        shape_str = str(tuple(tensor.shape)).replace(" ", "")
        device = str(tensor.device)
        dtype = str(tensor.dtype).replace("torch.", "")
        header = self._format_header("tensor", f"(shape={shape_str}, dtype={dtype}, device={device})")
        
        if tensor.numel() == 1:
            return header + f" {tensor.item()}"
            
        return f"{header}"

    def _format_sequence(self, seq, level):
        # Lists, Tuples, Sets
        type_name = type(seq).__name__
        length = len(seq)
        header = self._format_header(type_name, f"(len={length})")
        
        if length == 0:
            return header + " []"

        indent = self._get_indent(level)
        child_indent = self._get_indent(level + 1)
        
        # Convert set to list for indexing
        items = list(seq) if isinstance(seq, set) else seq
        
        result = [header, " {"]
        
        # Determine how many items to show
        indices_to_show = []
        if length <= MAX_ITEMS:
            indices_to_show = range(length)
        else:
            # Show first few and last few
            half = MAX_ITEMS // 2
            indices_to_show = list(range(half)) + [-1] + list(range(length - half, length))

        for i in indices_to_show:
            if i == -1:
                result.append(f"<br>{child_indent}<i>... ({length - MAX_ITEMS} more items) ...</i>")
                continue
                
            val = items[i]
            formatted_val = self.format(val, level + 1)
            result.append(f"<br>{child_indent}[{i}]: {formatted_val}")
            
        result.append(f"<br>{indent}}}")
        return "".join(result)

    def _format_dict(self, d, level):
        length = len(d)
        header = self._format_header("dict", f"(len={length})")
        
        if length == 0:
            return header + " {}"

        indent = self._get_indent(level)
        child_indent = self._get_indent(level + 1)
        
        result = [header, " {"]
        
        keys = list(d.keys())
        indices_to_show = []
        
        if length <= MAX_ITEMS:
            indices_to_show = range(length)
        else:
            half = MAX_ITEMS // 2
            indices_to_show = list(range(half)) + [-1] + list(range(length - half, length))

        for i in indices_to_show:
            if i == -1:
                result.append(f"<br>{child_indent}<i>... ({length - MAX_ITEMS} more items) ...</i>")
                continue
                
            key = keys[i]
            val = d[key]
            
            # Format Key
            key_str = str(key)
            if isinstance(key, str):
                key_str = f"'{key}'"
            
            formatted_val = self.format(val, level + 1)
            result.append(f"<br>{child_indent}<b>{key_str}</b>: {formatted_val}")
            
        result.append(f"<br>{indent}}}")
        return "".join(result)

    def _format_object(self, obj, level):
        # Custom objects
        attrs = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        header = self._format_header(type(obj).__name__, f"(attrs={len(attrs)})")
        
        indent = self._get_indent(level)
        child_indent = self._get_indent(level + 1)
        
        result = [header, " {"]
        
        for k, v in list(attrs.items())[:MAX_ITEMS]:
            formatted_val = self.format(v, level + 1)
            result.append(f"<br>{child_indent}<b>{k}</b>: {formatted_val}")
            
        if len(attrs) > MAX_ITEMS:
             result.append(f"<br>{child_indent}<i>... ({len(attrs) - MAX_ITEMS} more attributes)</i>")
             
        result.append(f"<br>{indent}}}")
        return "".join(result)

# ============ Main Processor ============

def process_file(file_type: int, file_path: str):
    """Loads file and applies formatting"""
    
    content = None
    formatter = JetBrainsFormatter()

    try:
        # 1. Load the content based on type
        if file_type == FileType.NUMPY.value:
            if np is None: raise ImportError("Numpy not installed")
            content = np.load(file_path, allow_pickle=True)
            # Handle .npz (NpzFile) specifically
            if hasattr(content, 'files'):
                print("<b>NpzFile</b> <i>(keys={})</i> {{".format(len(content.files)))
                for k in content.files:
                    print(f"&nbsp;&nbsp;<b>'{k}'</b>: {formatter.format(content[k], 1)}")
                print("}")
                return

        elif file_type == FileType.PICKLE.value:
            import pickle
            
            class UnknownObject:
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs
                def __repr__(self):
                    return f"<UnknownObject>"

            class SafeUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    try:
                        return super().find_class(module, name)
                    except (AttributeError, ImportError):
                        # Create a dynamic class with the original name so it shows up correctly in the formatter
                        return type(name, (UnknownObject,), {
                            '__module__': module,
                            '__repr__': lambda self: f"<{module}.{name}>"
                        })

            # Read all objects in the pickle file
            items = []
            with open(file_path, "rb") as f:
                while True:
                    try:
                        items.append(SafeUnpickler(f).load())
                    except EOFError:
                        break
                    except UnicodeDecodeError:
                        # Fallback for older python 2 pickles
                        f.seek(0)
                        items.append(SafeUnpickler(f, encoding="latin1").load())
                        break
            
            # v0 compatibility: Print items with headers
            for i, item in enumerate(items):
                print(f'<b>Item {i+1}/{len(items)}:</b>')
                print(formatter.format(item))
            return

        elif file_type == FileType.COMPRESSED_PICKLE.value:
            import compress_pickle
            content = compress_pickle.load(file_path)

        elif file_type == FileType.PYTORCH.value:
            if torch is None: raise ImportError("Torch not installed")
            try:
                content = torch.load(file_path, map_location='cpu', weights_only=True)
            except TypeError:
                content = torch.load(file_path, map_location='cpu')

        else:
            print("Unsupported file type.")
            return

        # 2. Format and Print
        print(formatter.format(content))

    except Exception as e:
        # Print error in red
        print(f"<span style='color:red'>Error processing file: {e}</span>")
        import traceback
        traceback.print_exc()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        print("Usage: python read_files.py <file_type> <file_path> [mode]")
        return
    
    try:
        f_type = int(sys.argv[1])
        f_path = sys.argv[2]
        
        if len(sys.argv) > 3:
            set_config(sys.argv[3])
            
        process_file(f_type, f_path)
    except ValueError:
        print("Error: file_type must be an integer")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
