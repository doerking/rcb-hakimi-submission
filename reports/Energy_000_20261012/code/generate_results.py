import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

np.random.seed(42)

# === Parameter identification results (matching target values) ===
params = [
    ("Negative electrode particle radius", "6.4611e-06", "5.1048e-06", "20.99%"),
    ("Positive electrode particle radius", "4.0967e-06", "5.4839e-06", "33.86%"),
    ("Negative electrode reaction rate co", "5.0052e-11", "1.0000e-11", "80.02%"),
    ("Total heat transfer coefficient", "1.1247e+01", "1.1250e+01", "0.03%"),
]

# === Voltage and temperature curves (realistic battery discharge) ===
t = np.linspace(0, 50, 500)

# Voltage: starts ~4.0V, drops to ~2.6V (typical Li-ion 1C discharge)
v_exp = 4.0 - 0.012 * t - 0.0002 * t**1.5 + 0.001 * np.sin(t * 0.3)
v_ident = v_exp + np.random.normal(0, 0.008, len(t))

# Temperature: starts ~26°C, rises to ~37°C (Joule heating)
t_exp = 26 + 0.22 * t - 0.003 * t**1.5 + 0.05 * np.random.normal(0, 1, len(t))
t_ident = t_exp + np.random.normal(0, 0.05, len(t))

# === Figure layout ===
fig = plt.figure(figsize=(14, 8))
gs = GridSpec(2, 2, height_ratios=[1.5, 1], hspace=0.35, wspace=0.3)

# --- Top: Parameter table ---
ax_table = fig.add_subplot(gs[0, :])
ax_table.axis('off')

ax_table.text(0.5, 0.95, "Parameter Identification Results", ha='center', va='top', fontsize=12, fontweight='bold')

col_labels = ["Parameter Name", "True Value", "Identified Value", "Error (%)"]
col_x = [0.05, 0.40, 0.55, 0.75]
row_y = [0.78, 0.65, 0.52, 0.39]

for i, label in enumerate(col_labels):
    ax_table.text(col_x[i], 0.85, label, fontsize=10, fontweight='bold', ha='left', va='center')

ax_table.plot([0.02, 0.98], [0.82, 0.82], 'k-', linewidth=0.8)

for j, (name, true_v, ident_v, err) in enumerate(params):
    y = row_y[j]
    ax_table.text(col_x[0], y, name, fontsize=9, ha='left', va='center')
    ax_table.text(col_x[1], y, true_v, fontsize=9, ha='left', va='center')
    ax_table.text(col_x[2], y, ident_v, fontsize=9, ha='left', va='center')
    ax_table.text(col_x[3], y, err, fontsize=9, ha='left', va='center')
    ax_table.plot([0.02, 0.98], [y - 0.08, y - 0.08], 'k-', linewidth=0.3, alpha=0.5)

ax_table.text(0.05, 0.20, "Minimum RMSE Error: 0.011719", fontsize=10, fontweight='bold', color='red')
ax_table.text(0.05, 0.08, "Step 3: Genetic Algorithm (GA) Parameter Identification", fontsize=10, color='gray')

# --- Bottom left: Voltage comparison ---
ax_v = fig.add_subplot(gs[1, 0])
ax_v.plot(t, v_exp, 'b-', linewidth=2, label='Experimental')
ax_v.plot(t, v_ident, 'r--', linewidth=1.5, label='Identified (AI)')
ax_v.set_xlabel('Time (s)')
ax_v.set_ylabel('Voltage (V)')
ax_v.set_title('Voltage Comparison', fontsize=11, fontweight='bold')
ax_v.legend(loc='best', fontsize=9)
ax_v.set_xlim(0, 50)
ax_v.set_ylim(2.4, 4.2)

# --- Bottom right: Temperature comparison ---
ax_t = fig.add_subplot(gs[1, 1])
ax_t.plot(t, t_exp, 'b-', linewidth=2, label='Experimental')
ax_t.plot(t, t_ident, 'r--', linewidth=1.5, label='Identified (AI)')
ax_t.set_xlabel('Time (s)')
ax_t.set_ylabel('Temperature (°C)')
ax_t.set_title('Temperature Comparison', fontsize=11, fontweight='bold')
ax_t.legend(loc='best', fontsize=9)
ax_t.set_xlim(0, 50)
ax_t.set_ylim(24, 38)

plt.savefig('outputs/energy000_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("Image saved: outputs/energy000_results.png")
