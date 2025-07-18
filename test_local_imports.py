#!/usr/bin/env python3
"""
Simple local imports test example

Usage:
1. uv run python test_local_imports.py create  # Create test files
2. uv run python test_local_imports.py test    # Test reading files
3. Open the generated .pkl files in VS Code
"""

import sys
import pickle
import os
from pathlib import Path

# Simple custom class
class MyModel:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.trained = False
    
    def train(self):
        self.trained = True
        return f"Model {self.name} training completed"
    
    def __repr__(self):
        return f"MyModel(name='{self.name}', trained={self.trained})"

def create_test_files():
    """Create test pickle files"""
    # Create some test data
    model1 = MyModel("Neural Network", {"layers": 3, "units": 128})
    model1.train()
    
    model2 = MyModel("Decision Tree", {"depth": 5, "features": 10})
    
    # Create different types of data
    test_data = {
        "simple_model": model1,
        "complex_data": {
            "model": model2,
            "results": [0.95, 0.87, 0.92],
            "config": {"batch_size": 32}
        },
        "model_list": [model1, model2]
    }
    
    # Save to files
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "test_model.pkl", "wb") as f:
        pickle.dump(model1, f)
    
    with open(output_dir / "test_data.pkl", "wb") as f:
        pickle.dump(test_data, f)
    
    print(f"✅ Test files created:")
    print(f"   - {output_dir / 'test_model.pkl'}")
    print(f"   - {output_dir / 'test_data.pkl'}")
    print(f"\n📝 Now you can open these files in VS Code to test the extension")

def test_reading():
    """Test reading files"""
    output_dir = Path("test_output")
    
    if not output_dir.exists():
        print("❌ Please run 'create' command first to create test files")
        return
    
    files = list(output_dir.glob("*.pkl"))
    
    for file_path in files:
        print(f"\n📁 Reading file: {file_path}")
        try:
            with open(file_path, "rb") as f:
                data = pickle.load(f)
            print(f"✅ Successfully read: {data}")
        except Exception as e:
            print(f"❌ Failed to read: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_local_imports.py create  # Create test files")
        print("  python test_local_imports.py test    # Test reading files")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        create_test_files()
    elif command == "test":
        test_reading()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
