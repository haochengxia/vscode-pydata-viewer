#!/usr/bin/env python3
"""
Example custom processing script for PyData Viewer extension

This script demonstrates how to handle pickle files with local imports
and custom classes. Adapt this script for your specific project needs.

Usage:
1. Modify the imports and processing logic for your project
2. Set the script path in VS Code settings:
   "vscode-pydata-viewer.scriptPath": "/path/to/this/script.py"
3. Open your pickle files in VS Code

Author: PyData Viewer Extension
"""

import sys
import os
import pickle
import numpy as np
from pathlib import Path
from enum import Enum

class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2
    COMPRESSED_PICKLE = 3

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

# Configure your project root - adjust this path as needed
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Optional: Add additional paths to sys.path if needed
# sys.path.insert(0, '/path/to/additional/modules')

# ============================================================================
# IMPORT YOUR PROJECT MODULES
# ============================================================================

# Add your project-specific imports here
try:
    # Example imports - replace with your actual modules
    # from my_project.models import NeuralNet, DataProcessor
    # from my_project.utils import helper_function
    # from my_project.data import Dataset
    
    LOCAL_IMPORTS_AVAILABLE = True
    print("<!-- Local imports loaded successfully -->")
except ImportError as e:
    LOCAL_IMPORTS_AVAILABLE = False
    print(f"<!-- Warning: Local imports not available: {e} -->")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_object_info(obj, max_depth=2, current_depth=0):
    """Format object information for HTML display"""
    indent = "&nbsp;" * (current_depth * 2)
    
    if current_depth >= max_depth:
        return f"{indent}{type(obj).__name__}(...)"
    
    if hasattr(obj, '__dict__'):
        result = f"{indent}<b>{type(obj).__name__}</b> {{\n"
        for key, value in obj.__dict__.items():
            if key.startswith('_'):
                continue  # Skip private attributes
            result += f"{indent}&nbsp;&nbsp;<b>{key}:</b> "
            if isinstance(value, (str, int, float, bool, type(None))):
                result += f"{value}\n"
            elif isinstance(value, np.ndarray):
                result += f"<i>ndarray(shape={value.shape}, dtype={value.dtype})</i>\n"
            else:
                result += f"{format_object_info(value, max_depth, current_depth + 1)}\n"
        result += f"{indent}}}"
        return result
    else:
        return f"{indent}{repr(obj)}"

def format_numpy_array(arr, max_elements=100):
    """Format numpy array for display"""
    if arr.size > max_elements:
        return f"<i>Large array: shape={arr.shape}, dtype={arr.dtype}, size={arr.size}</i>"
    else:
        return f"<i>shape={arr.shape}, dtype={arr.dtype}</i><br><pre>{repr(arr)}</pre>"

def format_dict(d, max_depth=2, current_depth=0):
    """Format dictionary for HTML display"""
    indent = "&nbsp;" * (current_depth * 2)
    
    if current_depth >= max_depth:
        return f"{indent}dict with {len(d)} items"
    
    result = f"{indent}{{\n"
    for key, value in d.items():
        result += f"{indent}&nbsp;&nbsp;<b>'{key}':</b> "
        if isinstance(value, dict):
            result += f"\n{format_dict(value, max_depth, current_depth + 1)}\n"
        elif isinstance(value, np.ndarray):
            result += f"<i>ndarray(shape={value.shape})</i>\n"
        elif isinstance(value, (list, tuple)):
            if len(value) > 10:
                result += f"<i>{type(value).__name__} with {len(value)} items</i>\n"
            else:
                result += f"{value}\n"
        else:
            result += f"{value}\n"
    result += f"{indent}}}"
    return result

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

def process_pickle_file(file_path):
    """Process pickle files with support for local imports"""
    try:
        print(f"<h3>📦 Pickle File: {os.path.basename(file_path)}</h3>")
        
        with open(file_path, 'rb') as f:
            contents = []
            try:
                while True:
                    contents.append(pickle.load(f))
            except EOFError:
                pass
        
        print(f"<b>📊 Found {len(contents)} object(s)</b><br><br>")
        
        for i, obj in enumerate(contents):
            print(f"<h4>Object {i+1}/{len(contents)}</h4>")
            print(f"<b>Type:</b> {type(obj).__name__}<br>")
            
            # Show module information if available
            if hasattr(obj, '__module__'):
                print(f"<b>Module:</b> {obj.__module__}<br>")
            
            # Handle different object types
            if isinstance(obj, dict):
                print(f"<b>Dictionary with {len(obj)} keys:</b><br>")
                print(format_dict(obj))
            elif isinstance(obj, np.ndarray):
                print(f"<b>NumPy Array:</b><br>")
                print(format_numpy_array(obj))
            elif isinstance(obj, (list, tuple)):
                print(f"<b>{type(obj).__name__} with {len(obj)} items:</b><br>")
                if len(obj) <= 10:
                    for j, item in enumerate(obj):
                        print(f"&nbsp;&nbsp;[{j}]: {item}<br>")
                else:
                    for j in range(3):
                        print(f"&nbsp;&nbsp;[{j}]: {obj[j]}<br>")
                    print(f"&nbsp;&nbsp;... ({len(obj)-6} more items)<br>")
                    for j in range(len(obj)-3, len(obj)):
                        print(f"&nbsp;&nbsp;[{j}]: {obj[j]}<br>")
            elif hasattr(obj, '__dict__'):
                print(f"<b>Custom Object:</b><br>")
                print(format_object_info(obj))
            else:
                print(f"<b>Value:</b> {repr(obj)}<br>")
            
            print("<br>")
            
    except Exception as e:
        print(f"<b>❌ Error processing pickle file:</b> {e}<br>")
        print(f"<b>Error type:</b> {type(e).__name__}<br>")
        
        # Provide helpful suggestions
        if "No module named" in str(e):
            print(f"<br><b>💡 Suggestion:</b> This pickle file contains objects from a module that's not in your Python path.<br>")
            print(f"Try one of these solutions:<br>")
            print(f"1. Set your Python path to a virtual environment that includes the required modules<br>")
            print(f"2. Modify this script to import the required modules<br>")
            print(f"3. Use PYTHONPATH environment variable to add the required paths<br>")

def process_numpy_file(file_path):
    """Process numpy files (.npy/.npz)"""
    try:
        print(f"<h3>🔢 NumPy File: {os.path.basename(file_path)}</h3>")
        
        if file_path.endswith('.npz'):
            # Archive file
            data = np.load(file_path, allow_pickle=True)
            print(f"<b>Archive with {len(data.files)} arrays:</b><br>")
            for name in data.files:
                arr = data[name]
                print(f"<b>'{name}':</b> {format_numpy_array(arr)}<br>")
        else:
            # Single array file
            arr = np.load(file_path, allow_pickle=True)
            print(f"<b>Array:</b> {format_numpy_array(arr)}")
            
    except Exception as e:
        print(f"<b>❌ Error processing numpy file:</b> {e}")

def process_pytorch_file(file_path):
    """Process PyTorch files (.pth/.pt/.ckpt)"""
    try:
        print(f"<h3>🔥 PyTorch File: {os.path.basename(file_path)}</h3>")
        
        # Try to import torch
        try:
            import torch
        except ImportError:
            print("<b>❌ PyTorch not available</b><br>")
            print("Install with: pip install torch")
            return
        
        # Load with CPU mapping to avoid GPU dependencies
        data = torch.load(file_path, map_location='cpu', weights_only=False)
        
        if isinstance(data, dict):
            print(f"<b>State dictionary with {len(data)} items:</b><br>")
            for key, value in data.items():
                if hasattr(value, 'shape'):
                    print(f"&nbsp;&nbsp;<b>{key}:</b> tensor(shape={value.shape})<br>")
                else:
                    print(f"&nbsp;&nbsp;<b>{key}:</b> {value}<br>")
        else:
            print(f"<b>Tensor:</b> shape={data.shape if hasattr(data, 'shape') else 'N/A'}<br>")
            print(f"<b>Data type:</b> {data.dtype if hasattr(data, 'dtype') else type(data)}<br>")
            
    except Exception as e:
        print(f"<b>❌ Error processing PyTorch file:</b> {e}")

def process_compressed_pickle(file_path):
    """Process compressed pickle files (.pkl.gz)"""
    try:
        print(f"<h3>🗜️ Compressed Pickle: {os.path.basename(file_path)}</h3>")
        
        try:
            import compress_pickle
        except ImportError:
            print("<b>❌ compress_pickle not available</b><br>")
            print("Install with: pip install compress_pickle")
            return
        
        data = compress_pickle.load(file_path)
        
        if isinstance(data, dict):
            print(format_dict(data))
        else:
            print(f"<b>Data:</b> {repr(data)}")
            
    except Exception as e:
        print(f"<b>❌ Error processing compressed pickle:</b> {e}")

# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_file(file_type, file_path):
    """Main function to process files based on type"""
    # Add some basic info
    print(f"<div style='font-family: monospace; font-size: 14px;'>")
    print(f"<b>📁 File:</b> {file_path}<br>")
    print(f"<b>🔧 Processor:</b> Custom Script<br>")
    print(f"<b>🐍 Python:</b> {sys.version.split()[0]}<br>")
    print(f"<b>📦 Local imports:</b> {'✅ Available' if LOCAL_IMPORTS_AVAILABLE else '❌ Not available'}<br>")
    print("<hr>")
    
    # Process based on file type
    if file_type == FileType.NUMPY.value:
        process_numpy_file(file_path)
    elif file_type == FileType.PICKLE.value:
        process_pickle_file(file_path)
    elif file_type == FileType.PYTORCH.value:
        process_pytorch_file(file_path)
    elif file_type == FileType.COMPRESSED_PICKLE.value:
        process_compressed_pickle(file_path)
    else:
        print(f"<b>❌ Unsupported file type: {file_type}</b>")
    
    print("</div>")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the script"""
    if len(sys.argv) < 3:
        print("Usage: python custom_processor.py <file_type> <file_path>")
        print("File types: 0=numpy, 1=pickle, 2=pytorch, 3=compressed_pickle")
        return
    
    try:
        file_type = int(sys.argv[1])
        file_path = sys.argv[2]
        
        # Ensure UTF-8 output
        sys.stdout.reconfigure(encoding='utf-8')
        
        process_file(file_type, file_path)
        
    except ValueError:
        print("Error: file_type must be an integer")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
