#!/usr/bin/env python3
"""Test enhanced PKL formatting functionality"""

import sys
import numpy as np
import pickle
from pathlib import Path
import tempfile

# Add project root to sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from pyscripts.read_files import process_file, FileType

def test_enhanced_pkl_formatting():
    """Test that enhanced PKL formatting shows more complete data"""
    
    # Create test data with various types that used to get truncated
    test_data = {
        'large_list': list(range(100)),  # Should show first 5 and last 5
        'large_array': np.random.random((20, 20)),  # Should show shape and sample values
        'small_array': np.array([[1, 2], [3, 4]]),  # Should show full content
        'nested_dict': {
            'level1': {
                'level2': {
                    'numbers': list(range(30)),
                    'text': 'nested text'
                }
            }
        },
        'tuple_data': tuple(range(50)),  # Should show with proper tuple notation
    }
    
    # Create temporary PKL file
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_file:
        pickle.dump(test_data, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Capture output
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            process_file(FileType.PICKLE.value, tmp_path)
        
        output = captured_output.getvalue()
        
        # Test assertions
        assert '<b>Item 1/1:</b>' in output, "Should have enhanced formatting header"
        assert '... (90 more items)' in output, "Should show truncation info for large list"
        assert 'shape:' in output, "Should show array shape information"
        assert 'dtype:' in output, "Should show array dtype for large arrays"
        assert 'Sample values:' in output, "Should show sample values for large arrays"
        assert '[0]: 0,' in output, "Should show indexed list items"
        assert "'level1'" in output, "Should show nested dictionary structure"
        assert '(' in output and ')' in output, "Should properly display tuples"
        
        print("✅ All enhanced PKL formatting tests passed!")
        print(f"Output preview:\n{output[:500]}...")
        
        return True
        
    finally:
        # Clean up
        Path(tmp_path).unlink()

def test_backward_compatibility():
    """Test that the enhancement doesn't break existing functionality"""
    
    # Create simple test data
    simple_data = {'key': 'value', 'number': 42}
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_file:
        pickle.dump(simple_data, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            process_file(FileType.PICKLE.value, tmp_path)
        
        output = captured_output.getvalue()
        
        # Should contain the basic data
        assert "'key'" in output, "Should contain dictionary keys"
        assert "'value'" in output, "Should contain dictionary values"
        assert "42" in output, "Should contain numeric values"
        
        print("✅ Backward compatibility test passed!")
        return True
        
    finally:
        Path(tmp_path).unlink()

if __name__ == "__main__":
    print("Testing enhanced PKL formatting...")
    test_enhanced_pkl_formatting()
    test_backward_compatibility()
    print("All tests completed successfully! 🎉")