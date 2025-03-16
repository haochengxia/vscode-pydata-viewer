# create example files
import numpy as np
import torch
import compress_pickle

np.save('./example.npy', np.array([1, 2, 3]))
torch.save(torch.tensor([1, 2, 3]), './example.pth')
compress_pickle.dump({'example': 'data'}, './example.pkl.gz')

tensors = {
    'tensor1': torch.tensor([1, 2, 3]),
    'tensor2': torch.tensor([4, 5, 6])
}
torch.save(tensors, './example_multi.pth')
