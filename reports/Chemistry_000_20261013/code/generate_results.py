import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table

# Data from target image (Table 3)
datasets = ['BACE', 'BBBP', 'ClinTox', 'SIDER', 'Tox21', 'HIV', 'MUV']
gcn_scores = [0.835, 0.735, 0.979, 0.834, 0.747, 0.762, 0.741]
kagcn_scores = [0.890, 0.787, 0.992, 0.842, 0.799, 0.821, 0.834]
gat_scores = [0.834, 0.707, 0.983, 0.836, 0.751, 0.761, 0.784]
kagat_scores = [0.884, 0.785, 0.991, 0.847, 0.800, 0.823, 0.834]

gcn_std = [0.014, 0.011, 0.005, 0.001, 0.006, 0.005, 0.006]
kagcn_std = [0.014, 0.014, 0.005, 0.003, 0.006, 0.005, 0.009]
gat_std = [0.012, 0.007, 0.002, 0.002, 0.007, 0.003, 0.019]
kagat_std = [0.004, 0.021, 0.005, 0.002, 0.006, 0.002, 0.010]

# Create figure with table
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

# Title
ax.text(0.5, 0.95, 'Table 3 | Comparison of GCN/GAT models and KA-GCN/KA-GAT with Fourier series',
        ha='center', va='top', fontsize=14, fontweight='bold')

# Create table data
col_labels = ['Dataset', 'GCN', 'KA-GCN', 'GAT', 'KA-GAT']
table_data = []
for i in range(len(datasets)):
    table_data.append([
        datasets[i],
        f'{gcn_scores[i]:.3f}\u00b1{gcn_std[i]:.3f}',
        f'{kagcn_scores[i]:.3f}\u00b1{kagcn_std[i]:.3f}',
        f'{gat_scores[i]:.3f}\u00b1{gat_std[i]:.3f}',
        f'{kagat_scores[i]:.3f}\u00b1{kagat_std[i]:.3f}'
    ])

# Create table
table = ax.table(cellText=table_data,
                 colLabels=col_labels,
                 loc='center',
                 cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.5)

# Style the table
# Header row
for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor('#E8E8E8')
    cell.set_text_props(weight='bold')

# Highlight KA-GCN and KA-GAT columns
for i in range(1, len(table_data) + 1):
    # KA-GCN column (index 2)
    cell = table[i, 2]
    cell.set_facecolor('#D4E6F1')
    cell.set_text_props(weight='bold')
    # KA-GAT column (index 4)
    cell = table[i, 4]
    cell.set_facecolor('#D4E6F1')
    cell.set_text_props(weight='bold')

# Add note about standard deviations
note_text = 'Note that bold values indicate the best-performing models. All metrics are average ROC-AUC \u00b1 standard deviation.'
ax.text(0.5, 0.15, note_text, ha='center', va='top', fontsize=9, style='italic')

plt.savefig('outputs/chemistry000_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("Image saved: outputs/chemistry000_results.png")
