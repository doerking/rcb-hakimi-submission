"""Lasso: VOS-Accelerated (FISTA + adaptive restart) vs Baseline (Proximal GD / ISTA).
Data: complex_optimization_data.npy (A 1000x2000, b, x_true; condition number 10).
Variable & Operator Splitting (VOS): split x into smooth part (quadratic data term)
and non-smooth part (L1), solved via proximal operator + momentum (Nesterov)."""
import numpy as np, json
d = np.load('data/complex_optimization_data.npy', allow_pickle=True).item()
A, b, x_true = np.asarray(d['A'],float), np.asarray(d['b'],float), np.asarray(d['x_true'],float)
n = A.shape[1]
L = float(np.linalg.norm(A, 2)**2)
lam = 0.1*np.max(np.abs(A.T@b))
def obj(x): return 0.5*np.linalg.norm(A@x-b)**2 + lam*np.sum(np.abs(x))
def grad(x): return A.T@(A@x-b)
def prox(x, t): return np.sign(x)*np.maximum(np.abs(x)-lam*t, 0.0)
N = 200
def run(algo):
    x=np.zeros(n); y=x.copy(); t=1.0; h=[obj(x)]
    for k in range(N):
        g=grad(y); xn=prox(y-g/L, 1/L)
        if algo=='baseline': x=xn; y=x          # Proximal GD (ISTA)
        else:                                    # VOS = FISTA + adaptive restart
            if np.dot(y-xn, xn-x) > 0: t=1.0
            tn=(1.0+np.sqrt(1.0+4.0*t*t))/2.0
            y=xn+((t-1.0)/tn)*(xn-x); x=xn; t=tn
        h.append(obj(x))
    return x, np.array(h)
xb, hb = run('baseline'); xa, ha = run('accelerated')
fstar = min(hb[-1], ha[-1]); f0 = hb[0]
def iters_to(h, tol): 
    idx=np.where(h<=tol)[0]; return int(idx[0]) if len(idx) else -1
res = dict(lam=float(lam), L=L, f0=float(f0), fstar=float(fstar), n_iter=N,
           final_baseline=float(hb[-1]), final_accel=float(ha[-1]),
           iters_1pct_baseline=iters_to(hb, fstar*1.01), iters_1pct_accel=iters_to(ha, fstar*1.01),
           iters_10pct_baseline=iters_to(hb, fstar*1.1), iters_10pct_accel=iters_to(ha, fstar*1.1),
           sparsity_accel=int((np.abs(xa)>1e-6).sum()), sparsity_true=int((np.abs(x_true)>1e-6).sum()))
json.dump(res, open('code/result.json','w'), indent=2)
np.save('code/hist_baseline.npy', hb); np.save('code/hist_accel.npy', ha)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# normalized objective f_k/f_0 (linear) — matches paper-style 0.8-1.0 band
plt.figure(figsize=(7.5,5))
plt.plot(np.arange(N+1), hb/f0, 'r--', lw=2.0, label='Baseline (Proximal GD)')
plt.plot(np.arange(N+1), ha/f0, 'b-',  lw=2.0, label='VOS Accelerated (FISTA)')
plt.xlabel('Iteration'); plt.ylabel('Normalized objective  $f(x_k)/f(x_0)$')
plt.title('Convergence trajectory — Lasso (1000x2000, cond=10)')
plt.grid(True, alpha=0.3); plt.legend(); plt.ylim(0.3,1.02)
plt.tight_layout(); plt.savefig('report/images/convergence.png', dpi=150); plt.close()
# second panel: absolute objective, log scale
plt.figure(figsize=(7.5,5))
plt.semilogy(np.arange(N+1), hb, 'r--', lw=2.0, label='Baseline (Proximal GD)')
plt.semilogy(np.arange(N+1), ha, 'b-',  lw=2.0, label='VOS Accelerated (FISTA)')
plt.xlabel('Iteration'); plt.ylabel('Objective Function Value (log scale)')
plt.grid(True, which='both', alpha=0.3); plt.legend()
plt.tight_layout(); plt.savefig('report/images/convergence_log.png', dpi=150); plt.close()
print(json.dumps(res, indent=2))
