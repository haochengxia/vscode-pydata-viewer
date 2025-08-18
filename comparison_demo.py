#!/usr/bin/env python3
"""Create a comparison demo showing before vs after enhancement"""

import pickle
import numpy as np
from pathlib import Path

def create_comparison_demo():
    """Create a side-by-side comparison of old vs new behavior"""
    
    # Create test data that demonstrates the issue
    demo_data = {
        'large_list': list(range(50)),
        'large_array': np.random.random((20, 20)),
        'small_array': np.array([[1, 2, 3], [4, 5, 6]]),
        'nested_dict': {
            'level1': {
                'numbers': list(range(20)),
                'metadata': {
                    'created': '2024-01-01',
                    'version': 1.0
                }
            }
        },
        'tuple_data': tuple(range(15))
    }
    
    # Save test file
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    demo_file = test_dir / "comparison_demo.pkl"
    
    with open(demo_file, 'wb') as f:
        pickle.dump(demo_data, f)
    
    print("📁 Created comparison demo file:", demo_file)
    print("📊 File size:", demo_file.stat().st_size, "bytes")
    
    # Show what the old behavior would look like
    print("\n" + "="*60)
    print("🔴 OLD BEHAVIOR (with truncation)")
    print("="*60)
    
    with open(demo_file, 'rb') as f:
        data = pickle.load(f)
    
    print(f"Item 1/1: {data}")
    
    print("\n" + "="*60)
    print("🟢 NEW ENHANCED BEHAVIOR")  
    print("="*60)
    
    # Import and use the enhanced function
    import sys
    sys.path.insert(0, 'pyscripts')
    from read_files import process_file, FileType
    
    process_file(FileType.PICKLE.value, str(demo_file))
    
    print("\n" + "="*60)
    print("✨ KEY IMPROVEMENTS:")
    print("="*60)
    print("1. 📋 Lists: Show indexed items instead of random truncation")
    print("2. 🔢 NumPy arrays: Show shape, dtype, and sample values")
    print("3. 📂 Dictionaries: Better nested structure display")
    print("4. 🔍 Tuples: Proper tuple notation with parentheses")
    print("5. 🎯 More data visible: Less truncation, more information")

if __name__ == "__main__":
    create_comparison_demo()