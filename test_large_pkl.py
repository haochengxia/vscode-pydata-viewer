#!/usr/bin/env python3
"""Test script to demonstrate the PKL file truncation issue"""

import pickle
import numpy as np
from pathlib import Path

def create_large_test_data():
    """Create test data that demonstrates the truncation issue"""
    
    # Create large list that gets truncated by default print
    large_list = list(range(100))  # This will be truncated with "..."
    
    # Create large numpy array
    large_array = np.random.random((50, 50))
    
    # Create nested dictionary with various data types
    complex_data = {
        'large_list': large_list,
        'large_array': large_array,
        'nested_dict': {
            'sub_list': list(range(20)),
            'sub_array': np.random.random((10, 10)),
            'meta': {
                'created_by': 'test_script',
                'version': '1.0',
                'description': 'This is a test file to demonstrate PKL truncation issues'
            }
        },
        'string_data': 'This is some string data that should be fully visible',
        'tuple_data': tuple(range(30))
    }
    
    return complex_data

def main():
    """Create test PKL file and demonstrate current vs improved behavior"""
    
    # Create test data
    test_data = create_large_test_data()
    
    # Save to PKL file
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    pkl_file = test_dir / "large_test.pkl"
    with open(pkl_file, 'wb') as f:
        pickle.dump(test_data, f)
    
    print(f"Created test file: {pkl_file}")
    print(f"File size: {pkl_file.stat().st_size} bytes")
    
    # Show what default print produces (current behavior)
    print("\n=== CURRENT BEHAVIOR (truncated) ===")
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    print(f"Item 1/1: {data}")
    
    return pkl_file

if __name__ == "__main__":
    main()