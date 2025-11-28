import pytest
import numpy as np
import pickle
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path
import compress_pickle

# add project root to sys.path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from pyscripts.read_files import FileType, process_file

class TestReadFiles:
    @pytest.fixture
    def setup_test_files(self, tmp_path):
        """create test files for reading"""
        # create test data
        test_array = np.array([[1, 2], [3, 4]])
        test_dict = {'a': np.array([1, 2, 3]), 'b': 'test'}
        
        # create .npy file
        npy_path = tmp_path / "test.npy"
        np.save(npy_path, test_array)
        
        # create .npz file
        npz_path = tmp_path / "test.npz"
        np.savez(npz_path, array=test_array, dict=test_dict)
        
        # create .pkl file
        pkl_path = tmp_path / "test.pkl"
        with open(pkl_path, 'wb') as f:
            pickle.dump(test_dict, f)
            
        # create matplotlib pickle file
        plt_pkl_path = tmp_path / "test_plt.pkl"
        fig = plt.figure()
        plt.plot([1, 2, 3], [1, 2, 3])
        with open(plt_pkl_path, 'wb') as f:
            pickle.dump(fig, f)
            
        # create .pth file
        pth_path = tmp_path / "test.pth"
        model_dict = {'layer1': torch.randn(2, 2)}
        torch.save(model_dict, pth_path)
        
        # create compressed .pkl file
        compressed_pkl_path = tmp_path / "test.pkl.gz"
        test_data = {'compressed': 'data', 'array': np.array([1, 2, 3])}
        compress_pickle.dump(test_data, compressed_pkl_path)
        
        return {
            'npy_path': npy_path,
            'npz_path': npz_path,
            'pkl_path': pkl_path,
            'plt_pkl_path': plt_pkl_path,
            'pth_path': pth_path,
            'compressed_pkl_path': compressed_pkl_path
        }

    def test_numpy_file_reading(self, setup_test_files, capsys):
        process_file(FileType.NUMPY.value, str(setup_test_files['npy_path']))
        captured = capsys.readouterr()
        assert 'shape=(2,2)' in captured.out

    def test_numpy_archive_reading(self, setup_test_files, capsys):
        process_file(FileType.NUMPY.value, str(setup_test_files['npz_path']))
        captured = capsys.readouterr()
        assert 'array' in captured.out
        assert 'dict' in captured.out

    def test_pickle_file_reading(self, setup_test_files, capsys):
        process_file(FileType.PICKLE.value, str(setup_test_files['pkl_path']))
        captured = capsys.readouterr()
        assert "'a'" in captured.out
        assert "'b'" in captured.out

    def test_pytorch_file_reading(self, setup_test_files, capsys):
        process_file(FileType.PYTORCH.value, str(setup_test_files['pth_path']))
        captured = capsys.readouterr()
        assert 'layer1' in captured.out

    def test_matplotlib_pickle_reading(self, setup_test_files, capsys):
        process_file(FileType.PICKLE.value, str(setup_test_files['plt_pkl_path']))
        captured = capsys.readouterr()
        assert 'data:image/jpeg;base64' in captured.out

    def test_compressed_pickle_reading(self, setup_test_files, capsys):
        process_file(FileType.COMPRESSED_PICKLE.value, 
                    str(setup_test_files['compressed_pkl_path']))
        captured = capsys.readouterr()
        assert "'compressed'" in captured.out
        assert "'array'" in captured.out
        assert "data" in captured.out

    def test_invalid_file_type(self, capsys):
        process_file(999, 'nonexistent.file')
        captured = capsys.readouterr()
        assert "Unsupported file type" in captured.out

    def test_nonexistent_file(self, capsys):
        process_file(FileType.NUMPY.value, 'nonexistent.npy')
        captured = capsys.readouterr()
        assert "No such file" in captured.out
