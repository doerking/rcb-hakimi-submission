import numpy as np
import matplotlib.pyplot as plt

# Data from target image (figure6_depth_levels.png)
# SparseTrack: improves from 1 to 4 levels, then plateau
# ByteTrack: improves from 1 to 6 levels, then plateau

depth_levels = [1, 2, 3, 4, 5, 6, 7, 8]

# SparseTrack MOA (approximate from target image)
sparsetrack_moa = [0.48, 0.51, 0.53, 0.54, 0.538, 0.536, 0.534, 0.532]

# ByteTrack MOA (approximate from target image)
bytetrack_moa = [0.46, 0.48, 0.50, 0.51, 0.515, 0.518, 0.516, 0.514]

fig, ax = plt.subplots(figsize=(10, 7))

# Plot SparseTrack
ax.plot(depth_levels, sparsetrack_moa, 'o-', color='#4472C4', linewidth=2, markersize=8, label='SparseTrack')

# Plot ByteTrack
ax.plot(depth_levels, bytetrack_moa, 'o--', color='#ED7D31', linewidth=2, markersize=8, label='ByteTrack')

# Add shading for optimal region
ax.axvspan(4, 6, alpha=0.1, color='green', label='Optimal depth levels')

ax.set_xlabel('Number of depth levels (low-score)', fontsize=12)
ax.set_ylabel('Tracking Accuracy (simplified MOA)', fontsize=12)
ax.set_title('Effect of Depth Levels on Tracking Performance', fontsize=14, fontweight='bold')
ax.set_xticks(depth_levels)
ax.set_xticklabels([str(i) for i in depth_levels])
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11, loc='lower right')

# Add annotation for improvement
ax.annotate(f'+2.0 MOA\n(1→4 levels)', xy=(4, 0.54), xytext=(5.5, 0.53),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=10, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/math000_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("Image saved: outputs/math000_results.png")
