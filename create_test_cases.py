#!/usr/bin/env python3
"""Create various test cases to demonstrate the PKL enhancement"""

import pickle
import numpy as np
from pathlib import Path

class CustomObject:
    def __init__(self):
        self.name = "Test Object"
        self.values = list(range(15))
        self.array = np.array([1, 2, 3, 4, 5])

def create_test_cases():
    """Create various pickle files to test the enhancement"""
    
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    # Test case 1: Large numeric data
    large_data = {
        'large_matrix': np.random.random((100, 100)),
        'long_list': list(range(200)),
        'description': 'This file contains large numeric data that would normally be truncated'
    }
    
    with open(test_dir / "large_numeric.pkl", 'wb') as f:
        pickle.dump(large_data, f)
    
    # Test case 2: Nested structures
    nested_data = {
        'level1': {
            'level2': {
                'level3': {
                    'data': list(range(50)),
                    'matrix': np.eye(10),
                    'info': 'deeply nested structure'
                }
            },
            'other_data': tuple(range(25))
        }
    }
    
    with open(test_dir / "nested_structure.pkl", 'wb') as f:
        pickle.dump(nested_data, f)
    
    # Test case 3: Mixed data types
    mixed_data = {
        'custom_obj': CustomObject(),
        'string_list': [f"item_{i}" for i in range(30)],
        'bool_array': np.array([True, False] * 10),
        'metadata': {
            'created': '2024-01-01',
            'version': 1.0,
            'tags': ['test', 'pickle', 'enhancement']
        }
    }
    
    with open(test_dir / "mixed_types.pkl", 'wb') as f:
        pickle.dump(mixed_data, f)
    
    print("Created test cases:")
    print(f"  - {test_dir / 'large_numeric.pkl'}")
    print(f"  - {test_dir / 'nested_structure.pkl'}")
    print(f"  - {test_dir / 'mixed_types.pkl'}")

if __name__ == "__main__":
    create_test_cases()