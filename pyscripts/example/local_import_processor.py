#!/usr/bin/env python3
"""
Example custom processor for handling local imports

This script demonstrates how to create a custom processor that can handle
pickle files with local imports from your project.

Usage:
1. Set this script as your custom processor in VS Code settings
2. Create example files with create_local_import_example.py
3. Open the created pickle files in VS Code

Configuration in VS Code settings:
{
  "vscode-pydata-viewer.scriptPath": "/path/to/this/script.py"
}
"""

import sys
import os
import pickle
from pathlib import Path
from enum import Enum

class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2
    COMPRESSED_PICKLE = 3

# Add the example directory to Python path to import local classes
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the local classes from the example
try:
    from create_local_import_example import CustomModel, DataProcessor
    LOCAL_CLASSES_AVAILABLE = True
    print("<!-- Successfully imported local classes -->")
except ImportError as e:
    LOCAL_CLASSES_AVAILABLE = False
    print(f"<!-- Warning: Could not import local classes: {e} -->")

def format_custom_model(model):
    """Format CustomModel objects for display"""
    html = f"""
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; background: #f9f9f9;">
        <h4>🤖 Custom Model: {model.name}</h4>
        <b>Parameters:</b><br>
        <ul>
    """
    for key, value in model.parameters.items():
        html += f"<li>{key}: {value}</li>"
    html += f"""
        </ul>
        <b>Training Status:</b> {'✅ Trained' if model.trained else '❌ Not Trained'}<br>
        <b>Type:</b> {type(model).__name__}<br>
        <b>Module:</b> {model.__class__.__module__}<br>
    </div>
    """
    return html

def format_data_processor(processor):
    """Format DataProcessor objects for display"""
    html = f"""
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; background: #f0f8ff;">
        <h4>🔧 Data Processor</h4>
        <b>Configuration:</b><br>
        <ul>
    """
    for key, value in processor.config.items():
        html += f"<li>{key}: {value}</li>"
    html += f"""
        </ul>
        <b>Processed Count:</b> {processor.processed_count}<br>
        <b>Type:</b> {type(processor).__name__}<br>
    </div>
    """
    return html

def format_generic_object(obj, max_depth=2, current_depth=0):
    """Format generic objects for display"""
    if current_depth >= max_depth:
        return f"<i>{type(obj).__name__}(...)</i>"
    
    if hasattr(obj, '__dict__'):
        html = f"<b>{type(obj).__name__}</b> {{\n"
        for key, value in obj.__dict__.items():
            if key.startswith('_'):
                continue
            html += f"&nbsp;&nbsp;<b>{key}:</b> "
            if isinstance(value, (str, int, float, bool, type(None))):
                html += f"{value}<br>"
            else:
                html += f"{format_generic_object(value, max_depth, current_depth + 1)}<br>"
        html += "}"
        return html
    else:
        return str(obj)

def process_pickle_with_local_imports(file_path):
    """Process pickle files that may contain local imports"""
    try:
        print(f"<h3>📦 Pickle File with Local Imports</h3>")
        print(f"<b>File:</b> {os.path.basename(file_path)}<br>")
        print(f"<b>Local classes available:</b> {'✅ Yes' if LOCAL_CLASSES_AVAILABLE else '❌ No'}<br>")
        print("<hr>")
        
        # Load the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"<b>Loaded data type:</b> {type(data).__name__}<br><br>")
        
        # Handle different data types
        if isinstance(data, CustomModel):
            print(format_custom_model(data))
        elif isinstance(data, DataProcessor):
            print(format_data_processor(data))
        elif isinstance(data, dict):
            print("<h4>📋 Dictionary Contents:</h4>")
            for key, value in data.items():
                print(f"<h5>Key: '{key}'</h5>")
                if isinstance(value, CustomModel):
                    print(format_custom_model(value))
                elif isinstance(value, DataProcessor):
                    print(format_data_processor(value))
                elif isinstance(value, dict):
                    print("<b>Nested dictionary:</b><br>")
                    for sub_key, sub_value in value.items():
                        print(f"&nbsp;&nbsp;<b>{sub_key}:</b> {sub_value}<br>")
                elif isinstance(value, list):
                    print(f"<b>List with {len(value)} items:</b><br>")
                    for i, item in enumerate(value[:5]):  # Show first 5 items
                        print(f"&nbsp;&nbsp;[{i}]: {item}<br>")
                    if len(value) > 5:
                        print(f"&nbsp;&nbsp;... and {len(value) - 5} more items<br>")
                else:
                    print(f"<b>Value:</b> {value}<br>")
                print("<br>")
        elif isinstance(data, list):
            print(f"<h4>📋 List with {len(data)} items:</h4>")
            for i, item in enumerate(data):
                print(f"<h5>Item {i + 1}:</h5>")
                if isinstance(item, CustomModel):
                    print(format_custom_model(item))
                elif isinstance(item, DataProcessor):
                    print(format_data_processor(item))
                else:
                    print(f"<b>Value:</b> {item}<br>")
                print("<br>")
        else:
            # Handle generic objects
            print("<h4>🔍 Generic Object:</h4>")
            print(format_generic_object(data))
        
    except Exception as e:
        print(f"<h3>❌ Error Processing File</h3>")
        print(f"<b>Error:</b> {e}<br>")
        print(f"<b>Error type:</b> {type(e).__name__}<br>")
        
        # Provide helpful suggestions
        if "No module named" in str(e) or "cannot import name" in str(e):
            print("<br><h4>💡 Troubleshooting Suggestions:</h4>")
            print("1. <b>Check your Python path:</b> Ensure the script can import your local modules<br>")
            print("2. <b>Verify module structure:</b> Check that all required modules are in the Python path<br>")
            print("3. <b>Use virtual environment:</b> Configure VS Code to use a virtual environment with your project<br>")
            print("4. <b>Update custom script:</b> Modify this script to import your specific modules<br>")
            print(f"5. <b>Check file path:</b> Ensure the script directory is in sys.path<br>")
            print(f"<br><b>Current sys.path:</b><br>")
            for i, path in enumerate(sys.path[:5]):
                print(f"&nbsp;&nbsp;{i}: {path}<br>")
            print("&nbsp;&nbsp;...<br>")

def process_file(file_type, file_path):
    """Main function to process different file types"""
    print("<div style='font-family: monospace; font-size: 14px;'>")
    print(f"<h2>PyData Viewer - Custom Processor</h2>")
    print(f"<b>📁 File:</b> {file_path}<br>")
    print(f"<b>🔧 Processor:</b> Local Import Handler<br>")
    print(f"<b>🐍 Python:</b> {sys.version.split()[0]}<br>")
    print("<hr>")
    
    if file_type == FileType.PICKLE.value:
        process_pickle_with_local_imports(file_path)
    else:
        print(f"<b>ℹ️ Info:</b> This custom processor is designed for pickle files with local imports.<br>")
        print(f"<b>File type {file_type} is not handled by this processor.</b><br>")
        print(f"<b>💡 Tip:</b> Use the default processor for other file types.<br>")
    
    print("</div>")

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python local_import_processor.py <file_type> <file_path>")
        print("This processor is designed for pickle files with local imports.")
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
