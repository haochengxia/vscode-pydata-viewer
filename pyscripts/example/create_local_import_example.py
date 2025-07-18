#!/usr/bin/env python3
"""
Example demonstrating how to handle local imports in pickle files

This example shows how to create and then read pickle files that contain
custom classes with local imports.
"""

import os
import pickle
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

class CustomModel:
    """Example custom class that might be in your project"""
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
        self.trained = False
    
    def train(self):
        self.trained = True
        return f"Model {self.name} trained successfully"
    
    def __repr__(self):
        return f"CustomModel(name='{self.name}', parameters={self.parameters}, trained={self.trained})"

class DataProcessor:
    """Example data processing class"""
    def __init__(self, config):
        self.config = config
        self.processed_count = 0
    
    def process(self, data):
        self.processed_count += 1
        return f"Processed {data} (count: {self.processed_count})"
    
    def __repr__(self):
        return f"DataProcessor(config={self.config}, processed_count={self.processed_count})"

def create_example_files():
    """Create example pickle files with local imports"""
    
    # Create output directory
    output_dir = Path(__file__).parent / "example_output"
    output_dir.mkdir(exist_ok=True)
    
    # Example 1: Simple custom object
    model = CustomModel("neural_net", {"layers": 3, "units": 128})
    model.train()
    
    with open(output_dir / "custom_model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    print(f"Created: {output_dir / 'custom_model.pkl'}")
    
    # Example 2: Dictionary with multiple custom objects
    processor = DataProcessor({"batch_size": 32, "normalize": True})
    processor.process("training_data")
    
    data_dict = {
        "model": model,
        "processor": processor,
        "metadata": {
            "version": "1.0",
            "created_by": "example_script",
            "timestamp": "2024-01-01"
        },
        "results": [0.95, 0.87, 0.92]
    }
    
    with open(output_dir / "experiment_results.pkl", "wb") as f:
        pickle.dump(data_dict, f)
    
    print(f"Created: {output_dir / 'experiment_results.pkl'}")
    
    # Example 3: List of custom objects
    models = [
        CustomModel("model_1", {"layers": 2, "units": 64}),
        CustomModel("model_2", {"layers": 4, "units": 256}),
        CustomModel("model_3", {"layers": 3, "units": 128})
    ]
    
    for model in models:
        model.train()
    
    with open(output_dir / "model_ensemble.pkl", "wb") as f:
        pickle.dump(models, f)
    
    print(f"Created: {output_dir / 'model_ensemble.pkl'}")
    
    print("\nExample files created successfully!")
    print(f"Open any of these files in VS Code to test the PyData Viewer extension:")
    print(f"- {output_dir / 'custom_model.pkl'}")
    print(f"- {output_dir / 'experiment_results.pkl'}")
    print(f"- {output_dir / 'model_ensemble.pkl'}")
    print("\nTo handle local imports:")
    print("1. Set your Python path to include this directory")
    print("2. Or use a custom processing script that imports these classes")
    print("3. Or set PYTHONPATH to include this directory")

def read_example_files():
    """Read and display the example files (for testing)"""
    output_dir = Path(__file__).parent / "example_output"
    
    files = ["custom_model.pkl", "experiment_results.pkl", "model_ensemble.pkl"]
    
    for filename in files:
        filepath = output_dir / filename
        if filepath.exists():
            print(f"\n--- Reading {filename} ---")
            try:
                with open(filepath, "rb") as f:
                    data = pickle.load(f)
                print(f"Successfully loaded: {data}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "read":
        read_example_files()
    else:
        create_example_files()
