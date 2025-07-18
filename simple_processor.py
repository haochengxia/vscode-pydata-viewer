#!/usr/bin/env python3
"""
Simple custom processing script

Configure in VS Code settings:
{
  "vscode-pydata-viewer.scriptPath": "/path/to/this/script.py"
}
"""

import sys
import os
import pickle
from pathlib import Path

# Add project root directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Try to import custom classes
try:
    from test_local_imports import MyModel
    HAS_LOCAL_IMPORTS = True
except ImportError:
    HAS_LOCAL_IMPORTS = False

def process_pickle_file(file_path):
    """Process pickle files"""
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"<h3>📦 File: {os.path.basename(file_path)}</h3>")
        print(f"<b>Local imports:</b> {'✅ Available' if HAS_LOCAL_IMPORTS else '❌ Not available'}<br>")
        print(f"<b>Data type:</b> {type(data).__name__}<br><br>")
        
        # Format output based on data type
        if HAS_LOCAL_IMPORTS and isinstance(data, MyModel):
            print(f"<div style='border: 1px solid #ccc; padding: 10px; background: #f9f9f9;'>")
            print(f"<h4>🤖 Custom Model: {data.name}</h4>")
            print(f"<b>Training status:</b> {'✅ Trained' if data.trained else '❌ Not trained'}<br>")
            print(f"<b>Data:</b> {data.data}<br>")
            print(f"</div>")
        elif isinstance(data, dict):
            print(f"<h4>📋 Dictionary content:</h4>")
            for key, value in data.items():
                print(f"<b>{key}:</b> {value}<br>")
        elif isinstance(data, list):
            print(f"<h4>📋 List content ({len(data)} items):</h4>")
            for i, item in enumerate(data):
                print(f"<b>[{i}]:</b> {item}<br>")
        else:
            print(f"<b>Content:</b> {data}")
            
    except Exception as e:
        print(f"<h3>❌ Error</h3>")
        print(f"<b>Error message:</b> {e}<br>")
        if "No module named" in str(e):
            print(f"<br><b>💡 Suggestion:</b> This file contains local modules, please check Python path settings.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_processor.py <file_type> <file_path>")
        return
    
    file_type = int(sys.argv[1])
    file_path = sys.argv[2]
    
    print(f"<div style='font-family: monospace;'>")
    print(f"<h2>🔧 Simple Processor</h2>")
    print(f"<b>File:</b> {file_path}<br>")
    print(f"<b>Python:</b> {sys.version.split()[0]}<br>")
    print("<hr>")
    
    if file_type == 1:  # Pickle file
        process_pickle_file(file_path)
    else:
        print(f"<b>ℹ️ This processor only supports pickle files</b>")
    
    print("</div>")

if __name__ == "__main__":
    main()
