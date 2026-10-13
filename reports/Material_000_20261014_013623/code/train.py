"""Train pre-trained CGCNN encoder (SS: node-feature reconstruction), then
fine-tune classifier on scarce positives, then screen candidates.

Outputs: metrics.json + report/images/training_results.png
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, Batch

sys.path.insert(0, os.path.dirname(__file__))
from loader import load_dataset
from model import CGCNNEncoder, SSDecoder, Classifier


def make_batch(data_list, indices):
    return Batch.from_data_list([data_list[i] for i in indices])


def ss_batch(data_list, indices):
    """Return x, edge_index, edge_attr, batch_vec, targets for SS training."""
    b = make_batch(data_list, indices)
    return b, b.x  # target = original x


def evaluate_with_shift(model, data_list, indices, bs=512):
    """Search best probability-calibration shift on the given indices (natural distribution).

    Returns (best_shift, train_acc, val_acc) using shift to interpret logits.
    """
    model.eval()
    with torch.no_grad():
        all_logs, all_y = [], []
        for i in range(0, len(indices), bs):
            b = make_batch(data_list, range(i, min(i+bs, len(indices))))
            if b is None:
                continue
            all_logs.append(model(b).squeeze(-1))
            all_y.append(b.y.float())
        logits = torch.cat(all_logs)
        y = torch.cat(all_y)
    grid = torch.linspace(-5, 5, 201)
    best_s, best_err = 0.0, float('inf')
    for s in grid:
        p = torch.sigmoid(logits + s)
        err = ((p - y) ** 2).mean().item()
        if err < best_err:
            best_err, best_s = err, s.item()
    acc = evaluate(model, data_list, indices, shift=best_s)
    return best_s, acc


def evaluate_with_noise(model, data_list, indices, bs=512, shift=0.0):
    """Standard deterministic evaluation."""
    model.eval()
    correct = 0
    total = 0
    n = len(indices)
    with torch.no_grad():
        for i in range(0, n, bs):
            b = make_batch(data_list, range(i, min(i+bs, n)))
            if b is None:
                continue
            p = model(b).squeeze(-1)
            y = b.y.float()
            pred = (p + shift > 0).float()
            correct += int((pred == y).sum())
            total += int(y.numel())
    return correct / max(total, 1)


def split_ft(data_list, seed=0):
    n = len(data_list)
    idx = list(range(n))
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)
    n_val = max(1, int(0.2 * n))
    return idx[n_val:], idx[:n_val]


def candidate_scores(model, data_list, bs=512):
    model.eval()
    all_probs = []
    n = len(data_list)
    with torch.no_grad():
        for i in range(0, n, bs):
            end = min(i+bs, n)
            b = make_batch(data_list, range(i, end))
            if b is None:
                continue
            p = torch.sigmoid(model(b).squeeze(-1))
            all_probs.extend(p.tolist())
    return np.array(all_probs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pretrain', default='data/pretrain_data.pt')
    ap.add_argument('--finetune', default='data/finetune_data.pt')
    ap.add_argument('--candidate', default='data/candidate_data.pt')
    ap.add_argument('--hidden', type=int, default=64)
    ap.add_argument('--layers', type=int, default=3)
    ap.add_argument('--pretrain-epochs', type=int, default=8)
    ap.add_argument('--finetune-epochs', type=int, default=20)
    ap.add_argument('--pretrain-bs', type=int, default=128)
    ap.add_argument('--finetune-bs', type=int, default=256)
    ap.add_argument('--lr-ss', type=float, default=1e-3)
    ap.add_argument('--lr-ft', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out-metrics', default='outputs/metrics.json')
    ap.add_argument('--out-curve-json', default='outputs/curves.json')
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    print('[data] loading ...')
    pre = load_dataset(args.pretrain)
    ft = load_dataset(args.finetune)
    cand = load_dataset(args.candidate)
    in_ch = pre.node_features
    print(f'  pre={pre.num_samples} ft={ft.num_samples} cand={cand.num_samples} in_ch={in_ch}')

    device = torch.device('cpu')

    print('[ss] self-supervised pre-training ...')
    encoder = CGCNNEncoder(in_ch, hidden=args.hidden, layers=args.layers).to(device)
    decoder = SSDecoder(args.hidden, in_ch).to(device)
    ss_params = list(encoder.parameters()) + list(decoder.parameters())
    ss_opt = torch.optim.Adam(ss_params, lr=args.lr_ss, weight_decay=1e-4)
    data_list_pre = pre.data_list
    pre_log = []
    for ep in range(args.pretrain_epochs):
        t0 = time.time()
        idx = np.random.default_rng(ep).permutation(len(data_list_pre))
        epoch_loss = 0.0
        n_batches = 0
        for i in range(0, len(idx), args.pretrain_bs):
            batch_idx = idx[i:i+args.pretrain_bs]
            b, target = ss_batch(data_list_pre, batch_idx)
            h = encoder(b.x, b.edge_index, b.edge_attr)
            recon = decoder(h)
            loss = F.mse_loss(recon, target)
            ss_opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(ss_params, 1.0)
            ss_opt.step()
            epoch_loss += loss.item() * len(batch_idx)
            n_batches += len(batch_idx)
        pre_log.append(epoch_loss / n_batches)
        print(f'  pretrain epoch {ep+1:2d} loss={pre_log[-1]:.5f} t={time.time()-t0:.1f}s')

    print('[ft] fine-tuning classifier ...')
    classifier = Classifier(CGCNNEncoder(in_ch, hidden=args.hidden, layers=args.layers),
                            hidden=args.hidden, dropout=0.25).to(device)
    # Warm-start encoder from pre-trained encoder (encoder remains trainable)
    with torch.no_grad():
        try:
            classifier.encoder.load_state_dict(encoder.state_dict())
            print('  warm-started encoder from pre-trained weights')
        except Exception as e:
            print(f'  warm-start failed: {e}')
    # Differential LR: encoder 3e-4, head 3e-3 (head must fit head-of-linear space)
    enc_params = list(classifier.encoder.parameters())
    head_params = list(classifier.head.parameters())
    optimizer_groups = [
        {'params': enc_params, 'lr': 3e-4},
        {'params': head_params, 'lr': 3e-3},
    ]

    ft_idx, val_idx = split_ft(ft.data_list, seed=args.seed)
    # Class-balanced sampling: oversample positives to match negatives
    pos_w = torch.tensor([1.0], device=device)
    ft_opt = torch.optim.Adam(optimizer_groups, weight_decay=1e-3)
    # Cosine LR schedule to prevent initial oscillation
    total_steps = args.finetune_epochs * max(1, len(ft_idx) // max(args.finetune_bs, 1))
    def lr_lambda(step):
        # Linear warmup for first 10% + cosine decay
        warm = int(total_steps * 0.1)
        if step < warm:
            return 0.1 + 0.9 * step / max(warm, 1)
        prog = (step - warm) / max(total_steps - warm, 1)
        return 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * prog))
    ft_sched = torch.optim.lr_scheduler.LambdaLR(ft_opt, lr_lambda)
    ft_log = {'train': [], 'val': []}
    pos_in_tr = [i for i in ft_idx if ft.data_list[i].y.item() == 1]
    neg_in_tr = [i for i in ft_idx if ft.data_list[i].y.item() == 0]
    print(f'  train split: {len(ft_idx)} total, {len(pos_in_tr)} pos, {len(neg_in_tr)} neg')
    for ep in range(args.finetune_epochs):
        t0 = time.time()
        rng = np.random.default_rng(ep+100)
        # Oversample positives to match negatives (natural 5%->balanced 50%)
        pos_repeated = np.random.default_rng(ep+100).choice(pos_in_tr, size=len(neg_in_tr), replace=True)
        all_idx = list(pos_repeated) + list(neg_in_tr)
        rng.shuffle(all_idx)
        epoch_loss = 0.0
        n_batches = 0
        for i in range(0, len(all_idx), args.finetune_bs):
            batch_idx = list(all_idx[i:i+args.finetune_bs])
            b = make_batch(ft.data_list, batch_idx)
            if b is None:
                continue
            logit = classifier(b).squeeze(-1)
            y = b.y.float()
            loss = F.binary_cross_entropy_with_logits(logit, y, pos_weight=pos_w)
            ft_opt.zero_grad()
            loss.backward()
            ft_opt.step()
            epoch_loss += loss.item() * len(batch_idx)
            n_batches += len(batch_idx)
        tr_acc = evaluate(classifier, ft.data_list, ft_idx)
        va_acc = evaluate(classifier, ft.data_list, val_idx)
        ft_log['train'].append(tr_acc)
        ft_log['val'].append(va_acc)
        print(f'  ft epoch {ep+1:2d} loss={epoch_loss/n_batches:.4f} train_acc={tr_acc:.4f} val_acc={va_acc:.4f} t={time.time()-t0:.1f}s')
        for _ in range(max(1, (len(all_idx)+args.finetune_bs-1)//args.finetune_bs)):
            ft_sched.step()

    print('[cand] scoring candidates ...')
    # Calibrate sigmoid shift using val set (training used balanced sampling => raw logits are shifted)
    def calibrate_shift(model, data_list, indices):
        model.eval()
        with torch.no_grad():
            b = make_batch(data_list, list(indices))
            logits = model(b).squeeze(-1)
            y = b.y.float()
            # search for shift s minimizing MSE(sigmoid(logit+s), y)
        grid = torch.linspace(-5, 5, 201)
        best = 0.0
        best_err = float('inf')
        for s in grid:
            p = torch.sigmoid(logits + s)
            err = ((p - y) ** 2).mean().item()
            if err < best_err:
                best_err, best = err, s.item()
        return best
    shift = calibrate_shift(classifier, ft.data_list, val_idx)
    print(f'  calibration shift={shift:.3f}')

    def probs_from_logit(model, data_list, bs=512):
        model.eval()
        all_p = []
        n = len(data_list)
        with torch.no_grad():
            for i in range(0, n, bs):
                end = min(i+bs, n)
                b = make_batch(data_list, range(i, end))
                if b is None:
                    continue
                p = torch.sigmoid(model(b).squeeze(-1) + shift)
                all_p.extend(p.tolist())
        return np.array(all_p)

    probs = probs_from_logit(classifier, cand.data_list)
    ys = np.concatenate([g.y.numpy() for g in cand.data_list])
    base_rate = ys.mean()
    tp_all = int(ys.sum())

    def disc_rate(thr):
        sel = probs > thr
        if sel.sum() == 0:
            return None, 0
        tp = int((ys[sel] == 1).sum())
        return tp / sel.sum(), int(sel.sum())

    dr_90, n_90 = disc_rate(0.9)
    dr_70, n_70 = disc_rate(0.7)
    # top-k discovery rate
    topk = 100
    top_idx = np.argsort(-probs)[:topk]
    topk_disc = float(ys[top_idx].mean()) if top_idx.size else None

    print(f'  candidates={len(probs)} positives={tp_all} base_rate={base_rate:.4f}')
    print(f'  p>0.9: n={n_90} disc_rate={dr_90}')
    print(f'  p>0.7: n={n_70} disc_rate={dr_70}')
    print(f'  top-100 disc_rate={topk_disc}')

    os.makedirs('outputs', exist_ok=True)
    with open(args.out_metrics, 'w', encoding='utf-8') as f:
        json.dump({
            'pretrain_loss': pre_log,
            'finetune_train_acc': ft_log['train'],
            'finetune_val_acc': ft_log['val'],
            'candidate_base_rate': base_rate,
            'candidate_positives': tp_all,
            'candidate_total': int(len(probs)),
            'discovery_rate_p_gt_0_9': dr_90,
            'n_selected_p_gt_0_9': n_90,
            'discovery_rate_p_gt_0_7': dr_70,
            'n_selected_p_gt_0_7': n_70,
            'top100_discovery_rate': topk_disc,
        }, f, indent=2, default=float)
    with open(args.out_curve_json, 'w', encoding='utf-8') as f:
        json.dump({'pre_loss': pre_log,
                   'ft_train': ft_log['train'],
                   'ft_val': ft_log['val']}, f, indent=2)
    print('[done] wrote', args.out_metrics)


if __name__ == '__main__':
    main()
