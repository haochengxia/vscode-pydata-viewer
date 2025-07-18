# PyData Viewer

[![Version](https://img.shields.io/visual-studio-marketplace/v/Percy.vscode-pydata-viewer?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=Percy.vscode-pydata-viewer)
[![Installs](https://img.shields.io/visual-studio-marketplace/i/Percy.vscode-pydata-viewer.svg?style=flat-square)](https://marketplace.visualstudio.com/items?itemName=Percy.vscode-pydata-viewer)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Python Tests](https://github.com/haochengxia/vscode-pydata-viewer/workflows/Python%20Tests/badge.svg)](https://github.com/haochengxia/vscode-pydata-viewer/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/gh/haochengxia/vscode-pydata-viewer/branch/main/graph/badge.svg)](https://codecov.io/gh/haochengxia/vscode-pydata-viewer)

Display Python data files in VSCode.

## Supported File Types

- **Numpy Files**: `.npz` `.npy`
- **Pickle Files**: `.pkl` `.pck` `.pickle` `.pkl.gz`
- **PyTorch Files**: `.pth` `.pt` `.ckpt`

## Quick Start

1. Install the extension from VS Code marketplace
2. Open any supported data file in VS Code
3. The file will automatically display with formatted content

## Requirements

:pushpin: **Python interpreter is required**. Add Python to your system PATH or configure a custom Python path in the extension settings.

## Configuration

### Extension Settings

- `vscode-pydata-viewer.pythonPath`: Path to Python interpreter (default: `"default"`)
- `vscode-pydata-viewer.scriptPath`: Path to custom processing script (default: `"default"`)

### Python Path Setup

1. Open VS Code Settings (`Cmd+,` or `Ctrl+,`)
2. Search for "pydata viewer"
3. Set **Python Path**:
   - **System Python**: Leave as `"default"`
   - **Virtual Environment**: `/path/to/venv/bin/python`
   - **Conda Environment**: `/path/to/conda/envs/myenv/bin/python`

## Handling Local Imports

If your pickle files contain custom classes from your project, you have these options:

### Option 1: Custom Processing Script

Create a custom script that imports your modules:

```python
import sys
import pickle
from pathlib import Path

# Add your project to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import your custom classes
from my_project.models import MyCustomClass

def process_pickle_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print(f"<b>Data:</b> {data}")

if __name__ == "__main__":
    file_type = int(sys.argv[1])
    file_path = sys.argv[2]
    
    if file_type == 1:  # Pickle file
        process_pickle_file(file_path)
```

Then set the script path in VS Code settings:
```json
{
  "vscode-pydata-viewer.scriptPath": "/path/to/your/custom_script.py"
}
```

### Option 2: Project Environment

Configure the extension to use your project's Python environment:

```json
{
  "vscode-pydata-viewer.pythonPath": "/path/to/your/project/venv/bin/python"
}
```

### Option 3: Workspace Settings

For project-specific configuration, create `.vscode/settings.json`:

```json
{
  "vscode-pydata-viewer.pythonPath": "${workspaceFolder}/venv/bin/python",
  "vscode-pydata-viewer.scriptPath": "${workspaceFolder}/scripts/custom_reader.py"
}
```

## Common Issues

**"No module named 'your_module'" Error**
- Use a custom script with proper imports
- Set Python path to your project environment
- Ensure your virtual environment contains required dependencies

**"Python not found" Error**
- Check Python installation
- Set full path to Python executable in settings
- Restart VS Code after changing settings

## Examples

### Basic Usage
Simply open any `.npy`, `.pkl`, or `.pth` file in VS Code.

### Custom Objects
```python
import pickle

class MyClass:
    def __init__(self, value):
        self.value = value

data = MyClass(42)
with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)
```

## Change Log

Please refer to [CHANGELOG.md](./CHANGELOG.md).

## Related Extensions

If you don't have Python available but need to view numpy files, try [vscode-numpy-viewer](https://github.com/haochengxia/vscode-numpy-viewer).


