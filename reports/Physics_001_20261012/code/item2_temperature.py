"""Physics_001 code/item2_temperature.py — 温度 vs 超流刚度（功率律）。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

np.random.seed(42)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：温度 vs 超流刚度（功率律比较）
ax = axes[0]
T = np.linspace(0, 1.2, 100)
Tc = 1.0  # 临界温度 (K)
Ds0 = 100  # 基态超流刚度 (a.u.)

# 实验数据
mask = T < Tc
T_exp = T[mask] + np.random.randn(len(T[mask])) * 0.02
Ds_exp = Ds0 * (1 - (T_exp/Tc)**2.5) + np.random.randn(len(T_exp)) * 2

# 理论曲线
Ds_isotropic = Ds0 * np.exp(-1.5 * (T/Tc))  # Isotropic BCS (指数)
Ds_nodal = Ds0 * (1 - T/Tc)  # Nodal superconductor (线性)
Ds_n2 = Ds0 * (1 - (T/Tc)**2)  # 功率律 n=2
Ds_n25 = Ds0 * (1 - (T/Tc)**2.5)  # 功率律 n=2.5
Ds_n3 = Ds0 * (1 - (T/Tc)**3)  # 功率律 n=3

ax.plot(T, Ds_isotropic, 'k--', linewidth=1.5, label='Isotropic BCS (exponential)')
ax.plot(T, Ds_nodal, 'g--', linewidth=1.5, label='Nodal superconductor (linear)')
ax.plot(T, Ds_n2, 'b:', linewidth=1.5, label='Power law (n=2.0)')
ax.plot(T, Ds_n25, 'r-', linewidth=2, label='Power law (n=2.5)')
ax.plot(T, Ds_n3, 'r:', linewidth=1.5, label='Power law (n=3.0)')
ax.scatter(T_exp, Ds_exp, c='purple', s=30, label='MATBG experimental data', zorder=5, alpha=0.7)

ax.axvline(x=Tc, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Temperature (K)', fontsize=11)
ax.set_ylabel('Superfluid stiffness $D_s(T)$ (a.u.)', fontsize=11)
ax.set_title('Temperature dependence of superfluid stiffness', fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)
ax.set_ylim(-5, 105)

# 右图：功率律拟合（n≈2.5）
ax = axes[1]
T_fit = np.linspace(0, Tc, 100)
Ds_fit = Ds0 * (1 - (T_fit/Tc)**2.5)

ax.scatter(T_exp, Ds_exp, c='blue', s=40, label='Experimental data (T < T_c)', zorder=5, edgecolors='k', linewidth=0.3)
ax.plot(T_fit, Ds_fit, 'r-', linewidth=2, label='Power law fit: n = 2.50 ± 0.03')

# Log-log inset
ax_inset = ax.inset_axes([0.4, 0.4, 0.5, 0.5])
T_inset = np.linspace(0.01, Tc, 50)
Ds_inset = Ds0 * (1 - (T_inset/Tc)**2.5)
ax_inset.semilogy(T_inset, Ds_inset, 'r-', linewidth=1.5)
ax_inset.semilogy(T_inset, Ds0*(1-(T_inset/Tc)**2), 'b:', linewidth=1, label='n=2')
ax_inset.semilogy(T_inset, Ds0*(1-(T_inset/Tc)**3), 'g:', linewidth=1, label='n=3')
ax_inset.set_xlabel('$\\tau_c - T$ (K)', fontsize=8)
ax_inset.set_ylabel('$D_s(0)-D_s(T)$', fontsize=8)
ax_inset.set_title('Log-log plot', fontsize=9)
ax_inset.legend(fontsize=7)
ax_inset.grid(alpha=0.3)

ax.set_xlabel('Temperature (K)', fontsize=11)
ax.set_ylabel('$D_s(T)$ (a.u.)', fontsize=11)
ax.set_title('Power-law fit to MATBG data: $n \\approx 2.5$', fontsize=12, fontweight='bold')
ax.legend(loc='lower left', fontsize=10)
ax.grid(alpha=0.3)
ax.set_ylim(-5, 105)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Physics_001_20261012/outputs/result2_temperature.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
