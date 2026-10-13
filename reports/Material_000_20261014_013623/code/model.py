"""CGCNN encoder + SS decoder + classifier for crystal graphs."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class GatedResCGCNConv(nn.Module):
    """Single CGCNNConv layer with gating + residual.

    Message = concat(x_src, edge_attr, x_dst), aggregated (mean) to dst,
    then h = concat(x, agg) fed through gate*conv, with residual.
    """
    def __init__(self, in_ch, out_ch, edge_ch=2):
        super().__init__()
        # pair (per edge) = x_src || edge_attr || x_dst => in_ch + edge_ch + in_ch
        self.conv = nn.Linear(in_ch * 3 + edge_ch, out_ch)
        self.gate = nn.Linear(in_ch * 3 + edge_ch, out_ch)
        self.act = nn.SiLU()
        self.res_proj = nn.Linear(in_ch, out_ch) if in_ch != out_ch else nn.Identity()

    def forward(self, x, edge_index, edge_attr):
        N = x.size(0)
        src_idx, dst_idx = edge_index
        pair = torch.cat([x[src_idx], edge_attr, x[dst_idx]], dim=-1)
        agg = torch.zeros(N, pair.size(-1), device=x.device).index_add_(0, dst_idx, pair)
        deg = torch.zeros(N, 1, device=x.device).index_add_(0, dst_idx, torch.ones(dst_idx.size(0), 1, device=x.device))
        agg = agg / deg.clamp_min(1.0)
        h = torch.cat([x, agg], dim=-1)
        gate = torch.sigmoid(self.gate(h))
        out = self.act(self.conv(h))
        out = gate * out
        return self.res_proj(x) + out


class CGCNNEncoder(nn.Module):
    """Stacked CGCNNConv encoder (3 layers by default)."""
    def __init__(self, in_ch, hidden=64, layers=3):
        super().__init__()
        chs = [in_ch] + [hidden] * layers
        self.convs = nn.ModuleList([GatedResCGCNConv(chs[i], chs[i+1]) for i in range(layers)])

    def forward(self, x, edge_index, edge_attr):
        h = x
        for conv in self.convs:
            h = conv(h, edge_index, edge_attr)
        return h


class SSDecoder(nn.Module):
    """MLP decoding node features (self-supervised target = original x)."""
    def __init__(self, hidden, in_ch):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden // 2), nn.SiLU(),
            nn.Linear(hidden // 2, in_ch),
        )

    def forward(self, h):
        return self.mlp(h)


class Classifier(nn.Module):
    """Encoder + global mean pooling + FC + dropout(0.25) + binary head."""
    def __init__(self, encoder, hidden=64, dropout=0.25):
        super().__init__()
        self.encoder = encoder
        self.drop = nn.Dropout(dropout)
        self.head = nn.Sequential(nn.Linear(hidden, hidden // 2), nn.SiLU(), nn.Linear(hidden // 2, 1))

    def embed(self, batch):
        """Aggregate node features to graph-level embedding via global mean pooling."""
        h = self.encoder(batch.x, batch.edge_index, batch.edge_attr)
        ptr = batch.ptr if batch.ptr is not None else torch.arange(len(batch.x), device=batch.x.device)
        return h, ptr

    def forward(self, batch):
        h, ptr = self.embed(batch)
        # global mean pool
        from torch_geometric.utils import segment
        emb = segment(h, ptr, reduce='mean')
        emb = self.drop(emb)
        return self.head(emb).squeeze(-1)
