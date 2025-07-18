# PyData Viewer Configuration Guide / 配置指南

## Quick Setup / 快速配置

### 1. Basic Settings / 基本设置
Open VS Code Settings (`Cmd+,`) and search for "pydata viewer" to configure:

打开 VS Code 设置 (`Cmd+,`)，搜索 "pydata viewer"，配置：

- **Python Path**: Set to your Python interpreter path / 设置为你的 Python 解释器路径
- **Script Path**: Set to custom script path (optional) / 设置为自定义脚本路径（可选）

### 2. Using uv Environment / 使用 uv 环境
If you use uv to manage your Python environment:

如果你使用 uv 管理 Python 环境：

```bash
# Get uv environment Python path / 获取 uv 环境的 Python 路径
uv run python -c "import sys; print(sys.executable)"
```

Set the output path as Python Path.

将输出的路径设置为 Python Path。

### 3. Handling Local Imports / 处理本地导入

#### Method 1: Workspace Configuration / 方法 1: 工作区配置
Create `.vscode/settings.json` in your project root:

在项目根目录创建 `.vscode/settings.json`：

```json
{
  "vscode-pydata-viewer.pythonPath": "/path/to/your/python",
  "vscode-pydata-viewer.scriptPath": "${workspaceFolder}/simple_processor.py"
}
```

#### Method 2: Custom Script / 方法 2: 自定义脚本
Create a processing script:

创建一个处理脚本：

```python
import sys
import pickle
from pathlib import Path

# Add project root directory to Python path
# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# Import your custom classes
# 导入你的自定义类
from your_module import YourClass

def process_pickle_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print(f"<b>Data / 数据:</b> {data}")

if __name__ == "__main__":
    file_type = int(sys.argv[1])
    file_path = sys.argv[2]
    
    if file_type == 1:  # Pickle file / Pickle 文件
        process_pickle_file(file_path)
```

## Testing Steps / 测试步骤

1. **Create test files / 创建测试文件**：
   ```bash
   uv run python test_local_imports.py create
   ```

2. **Test custom script / 测试自定义脚本**：
   ```bash
   uv run python simple_processor.py 1 test_output/test_model.pkl
   ```

3. **Configure VS Code / 配置 VS Code**：
   - Set Python Path to your uv environment / 设置 Python Path 为你的 uv 环境
   - Set Script Path to `simple_processor.py` / 设置 Script Path 为 `simple_processor.py`

4. **Open in VS Code / 在 VS Code 中打开**：
   - Open `test_output/test_model.pkl` file / 打开 `test_output/test_model.pkl` 文件
   - You should see formatted output / 应该能看到格式化的输出

## Common Issues / 常见问题

**Q: Getting "No module named" error? / 出现 "No module named" 错误？**
A: Add `sys.path.insert(0, str(Path(__file__).parent))` to your custom script / 在自定义脚本中添加 `sys.path.insert(0, str(Path(__file__).parent))`

**Q: Can't find Python? / 找不到 Python？**
A: Use `uv run python -c "import sys; print(sys.executable)"` to get the full path / 使用 `uv run python -c "import sys; print(sys.executable)"` 获取完整路径

**Q: Custom script not working? / 自定义脚本不工作？**
A: Check if the script path is correct and ensure the script is executable / 检查脚本路径是否正确，确保脚本可执行

Now you can view pickle files with local imports in VS Code! / 这样就能在 VS Code 中查看包含本地导入的 pickle 文件了！
