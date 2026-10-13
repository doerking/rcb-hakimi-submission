"""Loader for the packaged RealisticCrystalDataset .pt files.

The .pt files were pickled with a class from the closed-source `data_prepare`
module.  We register a shim so `torch.load` succeeds without touching the
original repo.
"""
import sys
import types
import torch
from torch_geometric.data import Dataset, Data


def _install_shim():
    if 'data_prepare' in sys.modules:
        return sys.modules['data_prepare']
    mod = types.ModuleType('data_prepare')
    class RealisticCrystalDataset(Dataset):
        def __init__(self, root=None, transform=None, pre_transform=None, pre_filter=None,
                     data_list=None, elem_to_idx=None, node_features=None, num_samples=None,
                     pos_ratio=None):
            self.data_list = data_list or []
            self.elem_to_idx = elem_to_idx or {}
            self.node_features = node_features or 0
            self.num_samples = num_samples or len(self.data_list)
            self.pos_ratio = pos_ratio or 0.0
        def len(self): return self.num_samples
        def get(self, idx): return self.data_list[idx]
    mod.RealisticCrystalDataset = RealisticCrystalDataset
    mod.RealisticCrystalData = Data
    sys.modules['data_prepare'] = mod
    return mod


def load_dataset(path):
    _install_shim()
    return torch.load(path, map_location='cpu', weights_only=False)
